# -*- coding: utf-8 -*-
"""ttk styles of the launcher, on top of the look shared with the issue viewer."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import UI.theme as theme

from . import launcher_config as cfg


def apply(root: tk.Misc) -> theme.Fonts:
    fonts = theme.apply(root, family=cfg.FONT, size=cfg.FONT_SIZE)
    style = ttk.Style(root)

    # --- the form -----------------------------------------------------------
    style.map("TEntry",
              fieldbackground=[("disabled", theme.READONLY)],
              foreground=[("disabled", theme.TEXT_SOFT)],
              bordercolor=[("disabled", theme.BORDER), ("focus", theme.ACCENT)],
              lightcolor=[("disabled", theme.READONLY), ("focus", theme.ACCENT_RING)])
    style.configure("TCombobox", fieldbackground=theme.SURFACE, background=theme.SURFACE,
                    foreground=theme.TEXT, bordercolor=theme.BORDER_STRONG,
                    lightcolor=theme.SURFACE, darkcolor=theme.SURFACE,
                    arrowcolor=theme.TEXT_MUTED, padding=(8, 4))
    style.map("TCombobox",
              fieldbackground=[("disabled", theme.READONLY), ("readonly", theme.SURFACE)],
              foreground=[("disabled", theme.TEXT_SOFT)],
              selectbackground=[("readonly", theme.SURFACE)],
              selectforeground=[("readonly", theme.TEXT)],
              bordercolor=[("focus", theme.ACCENT)])
    root.option_add("*TCombobox*Listbox.font", fonts.body)
    root.option_add("*TCombobox*Listbox.selectBackground", theme.ACCENT_SOFT)
    root.option_add("*TCombobox*Listbox.selectForeground", theme.TEXT)

    style.configure("Surface.TCheckbutton", background=theme.SURFACE)
    style.map("Surface.TCheckbutton", background=[("active", theme.SURFACE)])

    # a choice shown as buttons: same as the filter chips, greyed when locked
    style.map("Chip.Toolbutton",
              background=[("disabled", "selected", theme.CHIP),
                          ("disabled", theme.READONLY),
                          ("selected", theme.DARK), ("active", theme.SURFACE_HOVER)],
              foreground=[("disabled", theme.TEXT_DISABLED), ("selected", "#FFFFFF")])

    # "Override" on a computed value: a toggle, blue while it is on
    style.configure("Override.Toolbutton", background=theme.SURFACE,
                    foreground=theme.TEXT, bordercolor=theme.BORDER_STRONG,
                    lightcolor=theme.SURFACE, darkcolor=theme.SURFACE,
                    padding=(10, 4), relief="solid", borderwidth=1)
    style.map("Override.Toolbutton",
              background=[("selected", theme.ACCENT_SOFT), ("active", theme.SURFACE_HOVER)],
              foreground=[("selected", theme.ACCENT_HOVER)],
              bordercolor=[("selected", theme.ACCENT)],
              lightcolor=[("selected", theme.ACCENT_SOFT)],
              darkcolor=[("selected", theme.ACCENT_SOFT)])

    # small text button: "Reset", "Reset to file defaults"
    style.configure("Link.TButton", background=theme.SURFACE, foreground=theme.ACCENT,
                    bordercolor=theme.SURFACE, lightcolor=theme.SURFACE,
                    darkcolor=theme.SURFACE, padding=(4, 2), font=fonts.small)
    style.map("Link.TButton",
              foreground=[("active", theme.ACCENT_HOVER)],
              background=[("active", theme.SURFACE)],
              bordercolor=[("focus", theme.ACCENT_RING)],
              lightcolor=[("active", theme.SURFACE)],
              darkcolor=[("active", theme.SURFACE)])
    style.configure("Ground.Link.TButton", background=theme.GROUND,
                    bordercolor=theme.GROUND, lightcolor=theme.GROUND,
                    darkcolor=theme.GROUND)
    style.map("Ground.Link.TButton", background=[("active", theme.GROUND)],
              lightcolor=[("active", theme.GROUND)], darkcolor=[("active", theme.GROUND)])

    # --- the dark side bar and output pane ----------------------------------
    for name, ground, hover in (("Sidebar.TButton", cfg.COLOR_SIDEBAR, cfg.COLOR_SIDEBAR_HOVER),
                                ("Dark.TButton", cfg.COLOR_CONSOLE_BAR, cfg.COLOR_SIDEBAR_SELECTED)):
        style.configure(name, background=ground, foreground=cfg.COLOR_SIDEBAR_TEXT,
                        bordercolor=cfg.COLOR_SIDEBAR_LINE, lightcolor=ground,
                        darkcolor=ground, padding=(10, 3), font=fonts.small,
                        anchor="w")
        style.map(name,
                  background=[("disabled", ground), ("active", hover)],
                  foreground=[("disabled", cfg.COLOR_SIDEBAR_MUTED)],
                  bordercolor=[("focus", theme.ACCENT)],
                  lightcolor=[("active", hover)], darkcolor=[("active", hover)])

    style.configure("Dark.TCheckbutton", background=cfg.COLOR_CONSOLE_BAR,
                    foreground=cfg.COLOR_SIDEBAR_TEXT, font=fonts.small,
                    indicatorbackground=cfg.COLOR_CONSOLE_BG,
                    indicatorforeground=cfg.COLOR_SIDEBAR_TEXT,
                    bordercolor=cfg.COLOR_SIDEBAR_LINE, upperbordercolor=cfg.COLOR_SIDEBAR_LINE,
                    lowerbordercolor=cfg.COLOR_SIDEBAR_LINE)
    style.map("Dark.TCheckbutton", background=[("active", cfg.COLOR_CONSOLE_BAR)],
              indicatorbackground=[("selected", theme.ACCENT)])

    for orient in ("Vertical", "Horizontal"):
        style.configure(f"Dark.{orient}.TScrollbar", troughcolor=cfg.COLOR_CONSOLE_BG,
                        background=cfg.COLOR_SIDEBAR_LINE, bordercolor=cfg.COLOR_CONSOLE_BG,
                        lightcolor=cfg.COLOR_SIDEBAR_LINE, darkcolor=cfg.COLOR_SIDEBAR_LINE)
        style.map(f"Dark.{orient}.TScrollbar",
                  background=[("active", "#55637A")],
                  lightcolor=[("active", "#55637A")], darkcolor=[("active", "#55637A")])
    return fonts
