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

import UI.theme as theme

from . import launcher_config as cfg
from . import style
from .config_panel import ConfigPanel
from .module_nav import ModuleNav, split_title
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
        self.fonts = style.apply(self)

        self.registry = registry if registry is not None else ModuleRegistry().discover()
        self.store = store if store is not None else SettingsStore()
        self.runner = ProcessRunner()
        self._current = None

        self._build_layout()
        self._bind_keys()
        self._fill_module_list()

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(cfg.QUEUE_POLL_MS, self._drain_queue)

        for error in self.registry.errors:
            self._log(f"[launcher] module discovery: {error}\n",
                      ConsolePane.TAG_ERROR)

    # --- construction -------------------------------------------------------
    def _bind_keys(self) -> None:
        self.bind("<F5>", lambda _e: self._run_module())
        self.bind("<Shift-F5>", lambda _e: self._stop_module())
        self.bind("<Control-s>", lambda _e: self._save_settings())

    def _build_layout(self) -> None:
        # --- left: the modules as the steps of the pipeline ---
        self.nav = ModuleNav(self, self.fonts, on_select=self._on_module_selected,
                             on_activate=lambda _m: self._run_module())
        self.nav.pack(side="left", fill="y")
        self.nav.add_action("Reload", self._reload_settings)
        self.nav.add_action("Rescan modules", self._rescan_modules)
        self.nav.add_action("About", self._show_about)

        main = ttk.Frame(self)
        main.pack(side="left", fill="both", expand=True)

        # --- header: what the module does and the actions ---
        header = ttk.Frame(main, style="Surface.TFrame",
                           padding=(theme.SPACE_XL + 4, theme.SPACE_L + 2,
                                    theme.SPACE_XL + 4, theme.SPACE_L))
        header.pack(fill="x")
        # the description is packed first from the bottom, so it runs below the
        # actions over the whole width of the header
        self.module_description = tk.Label(header, background=theme.SURFACE,
                                           foreground=theme.TEXT_MUTED, font=self.fonts.body,
                                           anchor="w", justify="left")
        self.module_description.pack(side="bottom", fill="x")
        header.bind("<Configure>", lambda e: self.module_description.configure(
            wraplength=max(300, e.width - 2 * (theme.SPACE_XL + 4))))

        actions = ttk.Frame(header, style="Surface.TFrame")
        actions.pack(side="right", anchor="n")
        ttk.Button(actions, text="Save settings",
                   command=self._save_settings).pack(side="left")
        self.stop_button = ttk.Button(actions, text="Stop", state="disabled",
                                      command=self._stop_module)
        self.stop_button.pack(side="left", padx=(theme.SPACE_S, 0))
        self.run_button = ttk.Button(actions, text="Run   F5", style="Accent.TButton",
                                     command=self._run_module)
        self.run_button.pack(side="left", padx=(theme.SPACE_S, 0))

        texts = ttk.Frame(header, style="Surface.TFrame")
        texts.pack(side="left", fill="x", expand=True, padx=(0, theme.SPACE_XL))
        self.module_step = tk.Label(texts, background=theme.SURFACE,
                                    foreground=theme.TEXT_MUTED, font=self.fonts.small_bold,
                                    anchor="w")
        self.module_step.pack(fill="x")
        self.module_title = tk.Label(texts, background=theme.SURFACE, foreground=theme.TEXT,
                                     font=self.fonts.title, anchor="w", justify="left")
        self.module_title.pack(fill="x", pady=(2, 4))
        texts.bind("<Configure>", lambda e: self.module_title.configure(
            wraplength=max(300, e.width)))
        tk.Frame(main, height=1, background=theme.BORDER).pack(fill="x")

        # --- the form and, below it, the output ---
        split = ttk.PanedWindow(main, orient="vertical")
        split.pack(fill="both", expand=True)
        self.config_panel = ConfigPanel(split, self.store, self.fonts,
                                        on_change=self._on_config_changed)
        split.add(self.config_panel, weight=1)
        self.console = ConsolePane(split, self.fonts,
                                   on_toggle_size=self._toggle_console_size)
        # the output keeps its height when the window is resized - the form
        # gets the difference
        split.add(self.console, weight=0)
        self._split = split

        # the output starts as its header and one line; placed on the first
        # real size (before, the height is 1)
        def first_layout(event):
            if event.height > 1:
                split.unbind("<Configure>", binding)
                self._show_console_rows(cfg.CONSOLE_ROWS_START)
        binding = split.bind("<Configure>", first_layout, add="+")

    def _fill_module_list(self) -> None:
        self._modules = self.registry.modules
        self.nav.set_modules(self._modules)

        if not self._modules:
            self._set_status("No runnable module was found in Launcher/modules")
            return

        wanted = self.store.ui_value(UI_LAST_MODULE)
        index = next((i for i, m in enumerate(self._modules) if m.id == wanted), 0)
        self._select_module(self._modules[index])

    # --- module selection ---------------------------------------------------
    def _on_module_selected(self, module) -> None:
        if module is self._current:
            return
        # keep what was typed for the previous module before switching
        self._store_current_values(silent=True)
        self._select_module(module)

    def _select_module(self, module) -> None:
        self._current = module
        self.nav.select(module)
        number, name = split_title(module.label())
        self.module_step.configure(
            text=f"STEP {number} OF {len(self._modules)}" if number else "")
        self.module_title.configure(text=name)
        description = module.description
        if module.opens_window:
            description += "  The module opens its own window."
        self.module_description.configure(text=description)
        self.config_panel.show_module(module)
        self.store.set_ui_value(UI_LAST_MODULE, module.id)
        self._on_config_changed()

    # --- configuration ------------------------------------------------------
    def _on_config_changed(self) -> None:
        values, _errors = self.config_panel.collect(validate=False)
        self.nav.set_changes(sum(len(v) for v in values.values()))

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
        # values the module would misuse (a '/' in a document id) - the
        # fields are red, their tooltips say what to change
        problems = self.config_panel.problems()
        if problems:
            messagebox.showerror("Cannot run", "\n\n".join(problems), parent=self)
            return

        # a run opens the output to CONSOLE_ROWS_RUN rows and leaves it so -
        # only ever made larger, never smaller than the user dragged it
        self._show_console_rows(cfg.CONSOLE_ROWS_RUN, grow_only=True)
        self.store.save()
        self.console.append(
            f"\n=== {self._current.label()} ===\n", ConsolePane.TAG_INFO)
        self.runner.start(self._current.id, self.store.as_dict())
        self._set_running(True)

    def _toggle_console_size(self) -> None:
        self._show_console_rows(cfg.CONSOLE_ROWS_START if self.console.is_expanded()
                                else cfg.CONSOLE_ROWS_RUN)

    def _show_console_rows(self, rows: int, grow_only: bool = False) -> None:
        split = self._split
        wanted = self.console.height_for(rows)
        if grow_only and self.console.winfo_height() >= wanted:
            return
        split.sashpos(0, max(0, split.winfo_height() - wanted))
        # the divider itself takes some pixels from the output - give them back
        split.update_idletasks()
        missing = wanted - self.console.winfo_height()
        if missing:
            split.sashpos(0, max(0, split.sashpos(0) - missing))

    def _stop_module(self) -> None:
        if self.runner.is_running():
            self.runner.stop()

    def _set_running(self, running: bool) -> None:
        self.run_button.configure(state="disabled" if running else "normal")
        self.stop_button.configure(state="normal" if running else "disabled")
        self.nav.set_enabled(not running)
        if running:
            self.console.set_state(ConsolePane.STATE_RUNNING, cfg.STATE_RUNNING)
            self._set_status(split_title(self._current.label())[1])
        else:
            self.console.set_state(ConsolePane.STATE_IDLE, cfg.STATE_IDLE)

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
        self.console.set_state(ConsolePane.STATE_OK if code == 0 else ConsolePane.STATE_ERROR,
                               "Finished" if code == 0 else f"Failed \u00B7 exit code {code}")
        self._set_status("")

    def _log(self, text: str, tag: str | None = None) -> None:
        self.console.append(text, tag)

    def _set_status(self, text: str) -> None:
        self.console.set_message(text)

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
