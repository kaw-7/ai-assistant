# -*- coding: utf-8 -*-
"""The dark side bar: the modules as the numbered steps of the pipeline."""
from __future__ import annotations

import re
import tkinter as tk
from tkinter import ttk

import UI.theme as theme

from . import launcher_config as cfg

# horizontal padding of the side bar and of each module entry in it
NAV_PADX = 6
ENTRY_PADX = 6
BADGE_GAP = 8

_NUMBERED_TITLE = re.compile(r"^\s*(\d+[a-z]?)\s*[.)]\s*(.+)$")


def split_title(title: str) -> tuple[str, str]:
    """``"3. Issue import ..."`` -> ``("3", "Issue import ...")``; no number -> ``("", title)``."""
    match = _NUMBERED_TITLE.match(title or "")
    if match:
        return match.group(1), match.group(2).strip().rstrip(".")
    return "", (title or "").strip()


class _ModuleEntry(tk.Frame):
    """Number badge, name and one line summary - one per module."""

    BADGE = 24

    def __init__(self, master, module, number: str, fonts: theme.Fonts, on_click, on_double):
        super().__init__(master, background=cfg.COLOR_SIDEBAR, padx=ENTRY_PADX, pady=8,
                         cursor="hand2")
        self.module = module
        self.fonts = fonts
        self.selected = False
        self.enabled = True
        self._hover = False
        _number, name = split_title(module.label())

        self.badge = tk.Canvas(self, width=self.BADGE, height=self.BADGE,
                               highlightthickness=0, background=cfg.COLOR_SIDEBAR)
        self.badge.grid(row=0, column=0, sticky="n", padx=(0, BADGE_GAP), pady=(1, 0))
        self._circle = self.badge.create_oval(1, 1, self.BADGE - 1, self.BADGE - 1, width=1.5)
        self._number = self.badge.create_text(self.BADGE / 2, self.BADGE / 2,
                                              text=number, font=fonts.small_bold)

        # the width inside the side bar and this entry; the name stands next to
        # the badge, the summary below both and so also under the badge
        inner = cfg.SIDEBAR_WIDTH - 2 * (NAV_PADX + ENTRY_PADX) - 4
        self.name = tk.Label(self, text=name, font=fonts.body, anchor="w", justify="left",
                             wraplength=inner - self.BADGE - BADGE_GAP,
                             background=cfg.COLOR_SIDEBAR)
        self.name.grid(row=0, column=1, sticky="w")
        summary = getattr(module, "summary", "") or ""
        if module.opens_window:
            summary = (summary + " · " if summary else "") + "opens a window"
        self.summary = tk.Label(self, text=summary, font=fonts.small, anchor="w",
                                justify="left", wraplength=inner, background=cfg.COLOR_SIDEBAR)
        if summary:
            self.summary.grid(row=1, column=0, columnspan=2, sticky="w", pady=(2, 0))
        self.columnconfigure(1, weight=1)

        for widget in (self, self.badge, self.name, self.summary):
            widget.bind("<Button-1>", lambda _e: on_click(self.module))
            widget.bind("<Double-Button-1>", lambda _e: on_double(self.module))
            widget.bind("<Enter>", lambda _e: self._set_hover(True))
            widget.bind("<Leave>", lambda _e: self._set_hover(False))
        self.paint()

    def _set_hover(self, hover: bool) -> None:
        self._hover = hover
        self.paint()

    def paint(self) -> None:
        if self.selected:
            ground = cfg.COLOR_SIDEBAR_SELECTED
        elif self._hover and self.enabled:
            ground = cfg.COLOR_SIDEBAR_HOVER
        else:
            ground = cfg.COLOR_SIDEBAR
        for widget in (self, self.badge, self.name, self.summary):
            widget.configure(background=ground)
        self.configure(cursor="hand2" if self.enabled else "")

        if self.selected:
            self.badge.itemconfigure(self._circle, fill=theme.ACCENT, outline=theme.ACCENT)
            self.badge.itemconfigure(self._number, fill="#FFFFFF")
            self.name.configure(foreground="#FFFFFF", font=self.fonts.body_bold)
        else:
            self.badge.itemconfigure(self._circle, fill="", outline="#4A5566")
            self.badge.itemconfigure(self._number, fill="#C3CAD4")
            self.name.configure(foreground=cfg.COLOR_SIDEBAR_TEXT if self.enabled
                                else cfg.COLOR_SIDEBAR_MUTED, font=self.fonts.body)
        self.summary.configure(foreground="#A9B3C1" if self.selected else cfg.COLOR_SIDEBAR_MUTED)


class ModuleNav(tk.Frame):
    """Lists the modules; ``on_select`` / ``on_activate`` get the module."""

    def __init__(self, master, fonts: theme.Fonts, on_select=None, on_activate=None):
        super().__init__(master, background=cfg.COLOR_SIDEBAR, width=cfg.SIDEBAR_WIDTH,
                         padx=NAV_PADX, pady=18, takefocus=True)
        self.pack_propagate(False)
        self.fonts = fonts
        self.on_select = on_select
        self.on_activate = on_activate
        self.enabled = True
        self._entries: list[_ModuleEntry] = []

        brand = tk.Frame(self, background=cfg.COLOR_SIDEBAR)
        brand.pack(fill="x", padx=ENTRY_PADX, pady=(0, 18))
        mark = tk.Canvas(brand, width=30, height=30, highlightthickness=0,
                         background=cfg.COLOR_SIDEBAR)
        mark.create_rectangle(0, 0, 30, 30, fill=theme.ACCENT, outline=theme.ACCENT)
        mark.create_line(9, 15, 13, 19, 21, 11, fill="#FFFFFF", width=2.5,
                         capstyle="round", joinstyle="round")
        mark.pack(side="left", padx=(0, 10))
        tk.Label(brand, text=cfg.APP_NAME, background=cfg.COLOR_SIDEBAR,
                 foreground=cfg.COLOR_SIDEBAR_TEXT, font=fonts.heading).pack(side="left")

        tk.Label(self, text="PIPELINE", background=cfg.COLOR_SIDEBAR,
                 foreground=cfg.COLOR_SIDEBAR_MUTED, font=fonts.small_bold,
                 anchor="w").pack(fill="x", padx=ENTRY_PADX, pady=(0, 6))
        self._list = tk.Frame(self, background=cfg.COLOR_SIDEBAR)
        self._list.pack(fill="x")

        # bottom part: pending changes and the settings actions
        self.footer = tk.Frame(self, background=cfg.COLOR_SIDEBAR)
        self.footer.pack(side="bottom", fill="x")
        tk.Frame(self.footer, height=1, background="#2E3846").pack(fill="x", pady=(0, 12))
        self.changes = tk.Label(self.footer, background=cfg.COLOR_SIDEBAR,
                                foreground=cfg.COLOR_SIDEBAR_MUTED, font=fonts.small,
                                anchor="w", justify="left",
                                wraplength=cfg.SIDEBAR_WIDTH - 2 * (NAV_PADX + ENTRY_PADX))
        self.changes.pack(fill="x", padx=ENTRY_PADX, pady=(0, 10))
        self.actions = tk.Frame(self.footer, background=cfg.COLOR_SIDEBAR)
        self.actions.pack(fill="x", padx=ENTRY_PADX)

        self.bind("<Up>", lambda _e: self.step(-1))
        self.bind("<Down>", lambda _e: self.step(1))
        self.bind("<Return>", lambda _e: self._activate_selected())

    def add_action(self, text: str, command) -> ttk.Button:
        button = ttk.Button(self.actions, text=text, style="Sidebar.TButton", command=command)
        button.pack(fill="x", pady=(0, 6))
        return button

    def set_changes(self, count: int) -> None:
        if count:
            noun = "value differs" if count == 1 else "values differ"
            self.changes.configure(text=f"●  {count} {noun} from the configuration files",
                                   foreground=theme.WARN)
        else:
            self.changes.configure(text="Same as the configuration files",
                                   foreground=cfg.COLOR_SIDEBAR_MUTED)

    # --- modules ------------------------------------------------------------
    def set_modules(self, modules) -> None:
        for entry in self._entries:
            entry.destroy()
        self._entries = []
        for index, module in enumerate(modules):
            number = split_title(module.label())[0] or str(index + 1)
            entry = _ModuleEntry(self._list, module, number, self.fonts,
                                 self._clicked, self._double_clicked)
            entry.pack(fill="x", pady=1)
            self._entries.append(entry)

    def select(self, module) -> None:
        for entry in self._entries:
            entry.selected = entry.module is module
            entry.paint()

    def set_enabled(self, enabled: bool) -> None:
        """While a module runs the selection is locked."""
        self.enabled = enabled
        for entry in self._entries:
            entry.enabled = enabled
            entry.paint()

    def step(self, delta: int) -> None:
        if not self._entries:
            return
        current = next((i for i, e in enumerate(self._entries) if e.selected), 0)
        target = max(0, min(len(self._entries) - 1, current + delta))
        self._clicked(self._entries[target].module)

    def _clicked(self, module) -> None:
        self.focus_set()
        if self.enabled and callable(self.on_select):
            self.on_select(module)

    def _double_clicked(self, module) -> None:
        if self.enabled and callable(self.on_activate):
            self.on_activate(module)

    def _activate_selected(self) -> None:
        selected = next((e.module for e in self._entries if e.selected), None)
        if selected is not None:
            self._double_clicked(selected)
