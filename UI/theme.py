# -*- coding: utf-8 -*-
"""Colours, fonts and ttk styles of the issue viewer.

Built on the 'clam' theme - the only built-in ttk theme whose colours can be
changed freely - so no extra package is needed.
"""
from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from tkinter import font as tkfont
from tkinter import ttk

try:
    import UI.ui_config as uiConf
    import UI.IssueModel as model
except ImportError:
    import ui_config as uiConf
    import IssueModel as model

GROUND = "#F4F5F7"
SURFACE = "#FFFFFF"
SURFACE_HOVER = "#F0F2F5"
BORDER = "#E1E4E9"
BORDER_STRONG = "#C9CED6"
DIVIDER = "#EEF0F3"
READONLY = "#F6F7F9"

TEXT = "#1B1F24"
TEXT_SOFT = "#3D4652"
TEXT_MUTED = "#5B6470"
TEXT_DISABLED = "#9AA1AB"

ACCENT = "#1F5FAD"
ACCENT_HOVER = "#174A87"
ACCENT_SOFT = "#E4ECF7"
ACCENT_RING = "#D6E3F5"

DARK = "#1C232D"
DARK_SOFT = "#3A4658"

WARN = "#E3A23B"
WARN_TEXT = "#8A5A00"
WARN_SOFT = "#FBEED5"
CHIP = "#ECEEF1"

# issues the release notes name an improvement
IMPROVEMENT = ACCENT
IMPROVEMENT_SOFT = ACCENT_SOFT

DANGER = "#B42318"
DANGER_SOFT = "#FDECEA"


@dataclass(frozen=True)
class StatusColors:
    fg: str
    bg: str
    border: str
    dot: str
    icon: str


STATUS_COLORS = {
    model.RISK_EXISTS: StatusColors("#8F4300", "#FDEBD3", "#E9A55A", "#D9822B", "▲"),
    model.NO_RISK: StatusColors("#0B5E55", "#DDF1EE", "#6BB8AD", "#1F8A7C", "✓"),
    model.NOT_EVALUATED: StatusColors("#3D4652", "#ECEEF1", "#B5BCC6", "#8A94A3", "—"),
}

SPACE_XS = 4
SPACE_S = 8
SPACE_M = 12
SPACE_L = 16
SPACE_XL = 24


@dataclass
class Fonts:
    body: tkfont.Font
    body_bold: tkfont.Font
    small: tkfont.Font
    small_bold: tkfont.Font
    heading: tkfont.Font
    title: tkfont.Font
    mono: tkfont.Font


def _family(root, wanted: str, *fallbacks: str) -> str:
    available = set(tkfont.families(root))
    for name in (wanted, *fallbacks):
        if name in available:
            return name
    return "TkDefaultFont"


def _fonts(root, family: str, size: int) -> Fonts:
    family = _family(root, family, "Segoe UI Variable Text", "Segoe UI")
    mono = _family(root, "Cascadia Mono", "Consolas", "Courier New")

    def make(fam, sz, weight="normal"):
        return tkfont.Font(root, family=fam, size=sz, weight=weight)

    return Fonts(
        body=make(family, size),
        body_bold=make(family, size, "bold"),
        small=make(family, size - 1),
        small_bold=make(family, size - 2, "bold"),
        heading=make(family, size + 1, "bold"),
        title=make(family, size + 5, "bold"),
        mono=make(mono, size - 1),
    )


def sharp_on_high_dpi() -> None:
    """Without this Windows scales the window up as a bitmap - blurry text.

    Call it before the first Tk window is created.
    """
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):    # not Windows, or older than 8.1
        pass


def apply(root: tk.Misc, family: str | None = None, size: int | None = None) -> Fonts:
    """Set up the styles on ``root`` and return the fonts the widgets use.

    The issue viewer takes the font from ``ui_config``; the launcher, which
    shares this look, passes its own.
    """
    fonts = _fonts(root, family or uiConf.FONT, int(size or uiConf.FONT_SIZE))
    root.configure(background=GROUND)

    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".", background=GROUND, foreground=TEXT, font=fonts.body,
                    bordercolor=BORDER, lightcolor=GROUND, darkcolor=GROUND,
                    troughcolor=GROUND, focuscolor=ACCENT,
                    selectbackground=ACCENT_SOFT, selectforeground=TEXT)
    style.configure("Surface.TFrame", background=SURFACE)
    style.configure("Surface.TLabel", background=SURFACE)
    style.configure("Muted.Surface.TLabel", background=SURFACE,
                    foreground=TEXT_MUTED, font=fonts.small)

    # buttons: a white secondary one and the blue primary one
    style.configure("TButton", background=SURFACE, foreground=TEXT,
                    bordercolor=BORDER_STRONG, lightcolor=SURFACE,
                    darkcolor=SURFACE, padding=(14, 5), relief="solid",
                    borderwidth=1, focusthickness=0)
    style.map("TButton",
              background=[("disabled", SURFACE), ("pressed", BORDER),
                          ("active", SURFACE_HOVER)],
              foreground=[("disabled", TEXT_DISABLED)],
              bordercolor=[("disabled", BORDER), ("focus", ACCENT)],
              lightcolor=[("active", SURFACE_HOVER)],
              darkcolor=[("active", SURFACE_HOVER)])
    style.configure("Accent.TButton", background=ACCENT, foreground="#FFFFFF",
                    bordercolor=ACCENT, lightcolor=ACCENT, darkcolor=ACCENT,
                    font=fonts.body_bold)
    style.map("Accent.TButton",
              background=[("disabled", ACCENT_RING), ("pressed", ACCENT_HOVER),
                          ("active", ACCENT_HOVER)],
              foreground=[("disabled", "#FFFFFF")],
              bordercolor=[("disabled", ACCENT_RING), ("focus", ACCENT_HOVER)],
              lightcolor=[("disabled", ACCENT_RING), ("active", ACCENT_HOVER)],
              darkcolor=[("disabled", ACCENT_RING), ("active", ACCENT_HOVER)])
    style.configure("Icon.TButton", padding=(8, 5))
    style.configure("Danger.TButton", foreground=DANGER, padding=(8, 5))
    style.map("Danger.TButton",
              background=[("disabled", SURFACE), ("pressed", BORDER),
                          ("active", DANGER_SOFT)],
              foreground=[("disabled", TEXT_DISABLED)],
              bordercolor=[("disabled", BORDER), ("focus", DANGER)],
              lightcolor=[("active", DANGER_SOFT)],
              darkcolor=[("active", DANGER_SOFT)])

    # the status filter: toggle chips, dark when chosen
    style.configure("Chip.Toolbutton", background=SURFACE, foreground=TEXT,
                    bordercolor=BORDER_STRONG, lightcolor=SURFACE,
                    darkcolor=SURFACE, padding=(12, 4), relief="solid",
                    borderwidth=1, focusthickness=0)
    style.map("Chip.Toolbutton",
              background=[("selected", DARK), ("active", SURFACE_HOVER)],
              foreground=[("selected", "#FFFFFF")],
              bordercolor=[("selected", DARK)],
              lightcolor=[("selected", DARK), ("active", SURFACE_HOVER)],
              darkcolor=[("selected", DARK), ("active", SURFACE_HOVER)])

    style.configure("TEntry", fieldbackground=SURFACE, foreground=TEXT,
                    bordercolor=BORDER_STRONG, lightcolor=SURFACE,
                    darkcolor=SURFACE, padding=(8, 5), insertcolor=TEXT)
    style.map("TEntry", bordercolor=[("focus", ACCENT)],
              lightcolor=[("focus", ACCENT_RING)])

    # the issue list
    row_height = fonts.body.metrics("linespace") + 8
    style.configure("Issues.Treeview", background=SURFACE,
                    fieldbackground=SURFACE, foreground=TEXT, font=fonts.body,
                    rowheight=row_height, borderwidth=0, relief="flat")
    style.map("Issues.Treeview",
              background=[("selected", ACCENT_SOFT)],
              foreground=[("selected", TEXT)])
    style.layout("Issues.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
    style.configure("Issues.Treeview.Heading", background=SURFACE,
                    foreground=TEXT_MUTED, font=fonts.small_bold, relief="flat",
                    borderwidth=0, bordercolor=DIVIDER, lightcolor=SURFACE,
                    darkcolor=SURFACE, padding=(6, 3))
    style.map("Issues.Treeview.Heading", background=[("active", SURFACE)])

    # slim scrollbars without arrows
    for orient in ("Vertical", "Horizontal"):
        name = f"{orient}.TScrollbar"
        style.layout(name, [(f"{orient}.Scrollbar.trough", {"sticky": "nswe", "children": [
            (f"{orient}.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"})]})])
        style.configure(name, background="#D5DAE1", troughcolor=SURFACE,
                        bordercolor=SURFACE, lightcolor="#D5DAE1",
                        darkcolor="#D5DAE1", gripcount=0, arrowsize=10)
        style.map(name, background=[("active", "#B5BCC6")],
                  lightcolor=[("active", "#B5BCC6")],
                  darkcolor=[("active", "#B5BCC6")])

    style.configure("TPanedwindow", background=GROUND)
    style.configure("Sash", sashthickness=6, background=GROUND,
                    lightcolor=GROUND, bordercolor=GROUND)
    return fonts


def card(master, **kwargs) -> tk.Frame:
    """White box with a thin border - the cards of the detail pane."""
    return tk.Frame(master, background=SURFACE, highlightthickness=1,
                    highlightbackground=BORDER, highlightcolor=BORDER, **kwargs)


def status_dot(master, key: str, size: int = 10) -> tk.PhotoImage:
    """A filled circle in the colour of the status, for the issue list."""
    image = tk.PhotoImage(master=master, width=size + 6, height=size)
    color = STATUS_COLORS[key].dot
    radius = size / 2
    # pixels left out stay transparent; the extra width spaces the dot from the text
    for y in range(size):
        for x in range(size):
            if (x + 0.5 - radius) ** 2 + (y + 0.5 - radius) ** 2 <= radius ** 2:
                image.put(color, (x, y))
    return image
