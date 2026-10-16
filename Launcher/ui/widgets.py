# -*- coding: utf-8 -*-
"""Small tkinter helpers used by the launcher window."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import UI.theme as theme

from . import launcher_config as cfg


class ScrollableFrame(ttk.Frame):
    """A frame with a vertical scrollbar; put the content into ``.inner``."""

    def __init__(self, master, on_scroll=None, **kwargs):
        super().__init__(master, **kwargs)
        self.on_scroll = on_scroll
        self.canvas = tk.Canvas(self, highlightthickness=0, background=theme.GROUND)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical",
                                       command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas)

        self._window = self.canvas.create_window((0, 0), window=self.inner,
                                                 anchor="nw")
        self.canvas.configure(yscrollcommand=self._on_yscroll)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.inner.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.bind("<Enter>", lambda _e: self._bind_wheel())
        self.bind("<Leave>", lambda _e: self._unbind_wheel())

    def _on_yscroll(self, first, last):
        self.scrollbar.set(first, last)
        if callable(self.on_scroll):
            self.on_scroll()

    def scroll_to(self, widget) -> None:
        """Scroll so that ``widget`` (inside ``.inner``) is at the top."""
        self.update_idletasks()
        total = self.inner.winfo_height()
        if total > 0:
            y = widget.winfo_rooty() - self.inner.winfo_rooty()
            self.canvas.yview_moveto(max(0.0, (y - 8) / total))

    def visible_top(self) -> int:
        """Y of the first visible pixel, in the coordinates of ``.inner``."""
        return int(self.canvas.canvasy(0))

    def _on_inner_configure(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        # keep the content as wide as the canvas
        self.canvas.itemconfigure(self._window, width=event.width)

    def _bind_wheel(self):
        self.canvas.bind_all("<MouseWheel>", self._on_wheel)

    def _unbind_wheel(self):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_wheel(self, event):
        self.canvas.yview_scroll(int(-event.delta / 120), "units")

    def clear(self):
        for child in self.inner.winfo_children():
            child.destroy()

    def scroll_to_top(self):
        self.canvas.yview_moveto(0.0)


class Tooltip:
    """Hint box shown while the mouse rests on a widget.

    ``text`` may be a callable, evaluated each time the box is about to show;
    an empty result shows nothing.
    """

    DELAY_MS = 450

    def __init__(self, widget, text: str):
        self.widget = widget
        self.text = text
        self._window = None
        self._after_id = None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def _schedule(self, _event=None):
        self._cancel()
        self._after_id = self.widget.after(self.DELAY_MS, self._show)

    def _cancel(self):
        if self._after_id is not None:
            self.widget.after_cancel(self._after_id)
            self._after_id = None

    def _show(self):
        text = self.text() if callable(self.text) else self.text
        if self._window is not None or not text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self._window = tk.Toplevel(self.widget)
        self._window.wm_overrideredirect(True)
        self._window.wm_geometry(f"+{x}+{y}")
        tk.Label(self._window, text=text, justify="left", wraplength=640,
                 background=theme.DARK, foreground="#FFFFFF", relief="flat",
                 borderwidth=0, font=(cfg.FONT, cfg.FONT_SIZE - 1)).pack(ipadx=8, ipady=4)

    def _hide(self, _event=None):
        self._cancel()
        if self._window is not None:
            self._window.destroy()
            self._window = None


class ConsolePane(ttk.Frame):
    """Read only output view that understands the carriage returns of tqdm."""

    TAG_INFO = "info"
    TAG_OK = "ok"
    TAG_ERROR = "error"

    # state shown in the pill of the title bar: dot colour per state
    STATE_IDLE = "idle"
    STATE_RUNNING = "running"
    STATE_OK = "ok"
    STATE_ERROR = "error"
    _STATE_DOTS = {
        STATE_IDLE: cfg.COLOR_SIDEBAR_MUTED,
        STATE_RUNNING: cfg.COLOR_CONSOLE_INFO,
        STATE_OK: cfg.COLOR_CONSOLE_OK,
        STATE_ERROR: cfg.COLOR_CONSOLE_ERROR,
    }

    def __init__(self, master, fonts: theme.Fonts, **kwargs):
        super().__init__(master, **kwargs)
        bar_bg = cfg.COLOR_CONSOLE_BAR

        toolbar = tk.Frame(self, background=bar_bg, padx=theme.SPACE_L, pady=6)
        toolbar.pack(fill="x")
        tk.Label(toolbar, text="Output", background=bar_bg,
                 foreground=cfg.COLOR_SIDEBAR_TEXT, font=fonts.body_bold).pack(side="left")
        pill = tk.Frame(toolbar, background=cfg.COLOR_SIDEBAR_SELECTED, padx=8, pady=1)
        pill.pack(side="left", padx=(theme.SPACE_M, 0))
        self._state_dot = tk.Label(pill, text="●", background=cfg.COLOR_SIDEBAR_SELECTED,
                                   font=fonts.small)
        self._state_dot.pack(side="left")
        self._state_text = tk.Label(pill, background=cfg.COLOR_SIDEBAR_SELECTED,
                                    foreground=cfg.COLOR_SIDEBAR_TEXT, font=fonts.small)
        self._state_text.pack(side="left", padx=(4, 0))
        self._message = tk.Label(toolbar, background=bar_bg,
                                 foreground=cfg.COLOR_SIDEBAR_MUTED, font=fonts.small)
        self._message.pack(side="left", padx=(theme.SPACE_M, 0))

        ttk.Button(toolbar, text="Clear", style="Dark.TButton",
                   command=self.clear).pack(side="right")
        self.autoscroll = tk.BooleanVar(value=True)
        ttk.Checkbutton(toolbar, text="Auto scroll", style="Dark.TCheckbutton",
                        variable=self.autoscroll).pack(side="right", padx=theme.SPACE_M)

        body = tk.Frame(self, background=cfg.COLOR_CONSOLE_BG)
        body.pack(fill="both", expand=True)
        self.text = tk.Text(
            body, height=cfg.CONSOLE_HEIGHT, wrap="none",
            background=cfg.COLOR_CONSOLE_BG, foreground=cfg.COLOR_CONSOLE_FG,
            insertbackground=cfg.COLOR_CONSOLE_FG, relief="flat", borderwidth=0,
            highlightthickness=0, padx=theme.SPACE_L, pady=theme.SPACE_S, spacing1=1,
            selectbackground=cfg.COLOR_SIDEBAR_LINE, inactiveselectbackground=cfg.COLOR_SIDEBAR_LINE,
            font=fonts.mono, state="disabled",
        )
        y_scroll = ttk.Scrollbar(body, orient="vertical", command=self.text.yview,
                                 style="Dark.Vertical.TScrollbar")
        x_scroll = ttk.Scrollbar(body, orient="horizontal", command=self.text.xview,
                                 style="Dark.Horizontal.TScrollbar")
        self.text.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        self.text.tag_configure(self.TAG_INFO, foreground=cfg.COLOR_CONSOLE_INFO)
        self.text.tag_configure(self.TAG_OK, foreground=cfg.COLOR_CONSOLE_OK)
        self.text.tag_configure(self.TAG_ERROR, foreground=cfg.COLOR_CONSOLE_ERROR)

        x_scroll.pack(side="bottom", fill="x")
        y_scroll.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

        self._pending_return = False
        self.set_state(self.STATE_IDLE, cfg.STATE_IDLE)

    # --- title bar ----------------------------------------------------------
    def set_state(self, state: str, text: str) -> None:
        self._state_dot.configure(foreground=self._STATE_DOTS.get(state, cfg.COLOR_SIDEBAR_MUTED))
        self._state_text.configure(text=text)

    def set_message(self, text: str) -> None:
        """Short note next to the state - "Settings saved" and the like."""
        self._message.configure(text=text)

    # --- content ------------------------------------------------------------
    def append(self, chunk: str, tag: str | None = None) -> None:
        self.text.configure(state="normal")
        for part in self._split_carriage_returns(chunk):
            if part == "\r":
                self._pending_return = True
                continue
            if self._pending_return:
                self._pending_return = False
                # a "\r\n" split over two reads is a plain line break
                if not part.startswith("\n"):
                    # a progress bar rewrites its line - drop the previous one.
                    # Anchor on the end, not on "insert": a click in the view
                    # moves the insert mark even while the widget is disabled.
                    self.text.delete("end-1c linestart", "end-1c")
            self.text.insert("end", part, tag or ())
        self._trim()
        self.text.configure(state="disabled")
        if self.autoscroll.get():
            self.text.see("end")

    @staticmethod
    def _split_carriage_returns(chunk: str):
        """Yield the text in pieces, isolating the bare carriage returns."""
        buffer = ""
        index = 0
        while index < len(chunk):
            char = chunk[index]
            if char == "\r":
                following = chunk[index + 1] if index + 1 < len(chunk) else ""
                if following == "\n":  # windows line end, keep as one break
                    buffer += "\n"
                    index += 2
                    continue
                if buffer:
                    yield buffer
                    buffer = ""
                yield "\r"
                index += 1
                continue
            buffer += char
            index += 1
        if buffer:
            yield buffer

    def _trim(self) -> None:
        lines = int(self.text.index("end-1c").split(".")[0])
        if lines > cfg.CONSOLE_MAX_LINES:
            self.text.delete("1.0", f"{lines - cfg.CONSOLE_MAX_LINES}.0")

    def clear(self) -> None:
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.configure(state="disabled")
        self._pending_return = False
