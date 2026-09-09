# -*- coding: utf-8 -*-
"""The launcher window - module list, configuration editor and output pane."""
from __future__ import annotations

import queue
import tkinter as tk
from tkinter import messagebox, ttk

from Launcher.core.process_runner import (
    MSG_FINISHED,
    MSG_OUTPUT,
    MSG_STATUS,
    ProcessRunner,
)
from Launcher.core.registry import ModuleRegistry
from Launcher.core.settings_store import SettingsStore

from . import launcher_config as cfg
from .config_panel import ConfigPanel
from .widgets import ConsolePane

UI_LAST_MODULE = "last_module"


class LauncherApp(tk.Tk):
    """Top level UI running the modules of the tool validation assistant."""

    def __init__(self, registry: ModuleRegistry | None = None,
                 store: SettingsStore | None = None):
        super().__init__()
        self.title(cfg.WINDOW_TITLE)
        self.geometry(cfg.GEOMETRY)
        self.minsize(cfg.MIN_WIDTH, cfg.MIN_HEIGHT)
        self.option_add("*Font", (cfg.FONT, cfg.FONT_SIZE))

        self.registry = registry if registry is not None else ModuleRegistry().discover()
        self.store = store if store is not None else SettingsStore()
        self.runner = ProcessRunner()
        self._current = None

        self._build_menu()
        self._build_layout()
        self._fill_module_list()

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(cfg.QUEUE_POLL_MS, self._drain_queue)

        for error in self.registry.errors:
            self._log(f"[launcher] module discovery: {error}\n",
                      ConsolePane.TAG_ERROR)

    # --- construction -------------------------------------------------------
    def _build_menu(self) -> None:
        menu = tk.Menu(self)

        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Save settings", command=self._save_settings)
        file_menu.add_command(label="Reload settings from disk",
                              command=self._reload_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Rescan modules", command=self._rescan_modules)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close)
        menu.add_cascade(label="File", menu=file_menu)

        run_menu = tk.Menu(menu, tearoff=0)
        run_menu.add_command(label="Run selected module", command=self._run_module)
        run_menu.add_command(label="Stop", command=self._stop_module)
        menu.add_cascade(label="Run", menu=run_menu)

        help_menu = tk.Menu(menu, tearoff=0)
        help_menu.add_command(label="About", command=self._show_about)
        menu.add_cascade(label="Help", menu=help_menu)

        self.configure(menu=menu)

    def _build_layout(self) -> None:
        outer = ttk.PanedWindow(self, orient="horizontal")
        outer.pack(fill="both", expand=True, padx=cfg.PADX, pady=cfg.PADY)

        # --- left: the modules ---
        left = ttk.LabelFrame(outer, text="Modules")
        self.module_list = tk.Listbox(left, exportselection=False,
                                      activestyle="dotbox",
                                      width=cfg.MODULE_LIST_WIDTH)
        self.module_list.pack(fill="both", expand=True, padx=cfg.PADX,
                              pady=cfg.PADY)
        self.module_list.bind("<<ListboxSelect>>", self._on_module_selected)
        self.module_list.bind("<Double-Button-1>", lambda _e: self._run_module())
        outer.add(left, weight=0)

        # --- right: configuration and output ---
        right = ttk.PanedWindow(outer, orient="vertical")
        outer.add(right, weight=1)

        top = ttk.Frame(right)
        right.add(top, weight=3)

        header = ttk.Frame(top)
        header.pack(fill="x")
        self.module_title = ttk.Label(header, text="",
                                      font=(cfg.FONT, cfg.TITLE_FONT_SIZE, "bold"))
        self.module_title.pack(anchor="w", padx=cfg.PADX, pady=(cfg.PADY, 0))
        self.module_description = ttk.Label(header, text="", wraplength=700,
                                            justify="left",
                                            foreground=cfg.COLOR_HINT)
        self.module_description.pack(anchor="w", padx=cfg.PADX, pady=(0, cfg.PADY))

        toolbar = ttk.Frame(top)
        toolbar.pack(fill="x", padx=cfg.PADX)
        self.run_button = ttk.Button(toolbar, text="Run module",
                                     command=self._run_module)
        self.run_button.pack(side="left")
        self.stop_button = ttk.Button(toolbar, text="Stop", state="disabled",
                                      command=self._stop_module)
        self.stop_button.pack(side="left", padx=cfg.PADX)
        ttk.Button(toolbar, text="Save settings",
                   command=self._save_settings).pack(side="left", padx=cfg.PADX)
        self.changes_label = ttk.Label(toolbar, text="", foreground=cfg.COLOR_HINT)
        self.changes_label.pack(side="right", padx=cfg.PADX)

        self.config_panel = ConfigPanel(top, self.store,
                                        on_change=self._on_config_changed)
        self.config_panel.pack(fill="both", expand=True, padx=cfg.PADX,
                               pady=cfg.PADY)

        self.console = ConsolePane(right)
        right.add(self.console, weight=2)

        self.status = ttk.Label(self, text=cfg.STATE_IDLE, anchor="w",
                                relief="sunken")
        self.status.pack(fill="x", side="bottom")

    def _fill_module_list(self) -> None:
        self.module_list.delete(0, "end")
        self._modules = self.registry.modules
        for module in self._modules:
            self.module_list.insert("end", "  " + module.label())

        if not self._modules:
            self._set_status("No runnable module was found in Launcher/modules")
            return

        wanted = self.store.ui_value(UI_LAST_MODULE)
        index = next((i for i, m in enumerate(self._modules) if m.id == wanted), 0)
        self.module_list.selection_set(index)
        self._select_module(self._modules[index])

    # --- module selection ---------------------------------------------------
    def _on_module_selected(self, _event=None) -> None:
        selection = self.module_list.curselection()
        if not selection:
            return
        module = self._modules[selection[0]]
        if module is self._current:
            return
        # keep what was typed for the previous module before switching
        self._store_current_values(silent=True)
        self._select_module(module)

    def _select_module(self, module) -> None:
        self._current = module
        self.module_title.configure(text=module.label())
        description = module.description
        if module.opens_window:
            description += "  (opens its own window)"
        self.module_description.configure(text=description)
        self.config_panel.show_module(module)
        self.store.set_ui_value(UI_LAST_MODULE, module.id)
        self._on_config_changed()

    # --- configuration ------------------------------------------------------
    def _on_config_changed(self) -> None:
        values, _errors = self.config_panel.collect(validate=False)
        count = sum(len(v) for v in values.values())
        self.changes_label.configure(
            text=f"{count} value(s) differ from the configuration files"
            if count else "configuration files unchanged"
        )

    def _store_current_values(self, silent: bool = False) -> bool:
        errors = self.config_panel.store_values()
        if errors and not silent:
            messagebox.showerror("Invalid configuration", "\n".join(errors),
                                 parent=self)
        return not errors

    def _save_settings(self) -> None:
        if not self._store_current_values():
            return
        self.store.save()
        self._log(f"[launcher] settings saved to {self.store.path}\n",
                  ConsolePane.TAG_INFO)
        self._set_status("Settings saved")

    def _reload_settings(self) -> None:
        self.store.load()
        self.config_panel.refresh_values()
        self._on_config_changed()
        self._set_status("Settings reloaded")

    def _rescan_modules(self) -> None:
        self.registry.discover()
        for error in self.registry.errors:
            self._log(f"[launcher] module discovery: {error}\n",
                      ConsolePane.TAG_ERROR)
        self._current = None
        self._fill_module_list()
        self._set_status(f"{len(self.registry)} module(s) found")

    # --- running ------------------------------------------------------------
    def _run_module(self) -> None:
        if self._current is None:
            return
        if self.runner.is_running():
            messagebox.showinfo("Already running",
                                "Stop the running module first.", parent=self)
            return
        if not self._store_current_values():
            return

        self.store.save()
        self.console.append(
            f"\n=== {self._current.label()} ===\n", ConsolePane.TAG_INFO)
        self.runner.start(self._current.id, self.store.as_dict())
        self._set_running(True)

    def _stop_module(self) -> None:
        if self.runner.is_running():
            self.runner.stop()

    def _set_running(self, running: bool) -> None:
        self.run_button.configure(state="disabled" if running else "normal")
        self.stop_button.configure(state="normal" if running else "disabled")
        self.module_list.configure(state="disabled" if running else "normal")
        if running:
            self._set_status(f"{cfg.STATE_RUNNING}: {self._current.label()}")
        else:
            self._set_status(cfg.STATE_IDLE)

    # --- output -------------------------------------------------------------
    def _drain_queue(self) -> None:
        try:
            while True:
                kind, payload = self.runner.queue.get_nowait()
                if kind == MSG_OUTPUT:
                    self.console.append(payload)
                elif kind == MSG_STATUS:
                    self.console.append(str(payload) + "\n", ConsolePane.TAG_INFO)
                elif kind == MSG_FINISHED:
                    self._on_finished(int(payload))
        except queue.Empty:
            pass
        self.after(cfg.QUEUE_POLL_MS, self._drain_queue)

    def _on_finished(self, code: int) -> None:
        tag = ConsolePane.TAG_OK if code == 0 else ConsolePane.TAG_ERROR
        self.console.append(f"=== finished with exit code {code} ===\n", tag)
        self._set_running(False)
        self._set_status(f"Last run finished with exit code {code}")

    def _log(self, text: str, tag: str | None = None) -> None:
        self.console.append(text, tag)

    def _set_status(self, text: str) -> None:
        self.status.configure(text=text)

    # --- misc ---------------------------------------------------------------
    def _show_about(self) -> None:
        modules = "\n".join(f"  - {m.label()}" for m in self.registry.modules)
        messagebox.showinfo(
            "About",
            "Tool Validation Assistant - Launcher\n\n"
            "Runs the modules of the assistant one by one and lets their "
            "configuration be changed before every run.\n\n"
            f"Modules found:\n{modules}\n\n"
            f"Settings file:\n  {self.store.path}",
            parent=self,
        )

    def _on_close(self) -> None:
        if self.runner.is_running():
            if not messagebox.askyesno(
                "A module is running",
                "Stop the running module and close the launcher?", parent=self
            ):
                return
            self.runner.stop()
        self._store_current_values(silent=True)
        self.store.save()
        self.destroy()
