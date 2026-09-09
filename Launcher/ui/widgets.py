# -*- coding: utf-8 -*-
"""Small tkinter helpers used by the launcher window."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from . import launcher_config as cfg


class ScrollableFrame(ttk.Frame):
    """A frame with a vertical scrollbar; put the content into ``.inner``."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical",
                                       command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas)

        self._window = self.canvas.create_window((0, 0), window=self.inner,
                                                 anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.inner.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.bind("<Enter>", lambda _e: self._bind_wheel())
        self.bind("<Leave>", lambda _e: self._unbind_wheel())

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
    """Yellow hint box shown while the mouse rests on a widget."""

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
        if self._window is not None or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self._window = tk.Toplevel(self.widget)
        self._window.wm_overrideredirect(True)
        self._window.wm_geometry(f"+{x}+{y}")
        tk.Label(self._window, text=self.text, justify="left",
                 background="#ffffe0", relief="solid", borderwidth=1,
                 font=(cfg.FONT, cfg.FONT_SIZE - 1)).pack(ipadx=4, ipady=2)

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

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x")
        ttk.Label(toolbar, text="Output").pack(side="left", padx=cfg.PADX)
        self.autoscroll = tk.BooleanVar(value=True)
        ttk.Checkbutton(toolbar, text="Auto scroll",
                        variable=self.autoscroll).pack(side="right", padx=cfg.PADX)
        ttk.Button(toolbar, text="Clear",
                   command=self.clear).pack(side="right", padx=cfg.PADX)

        self.text = tk.Text(
            self, height=cfg.CONSOLE_HEIGHT, wrap="none",
            background=cfg.COLOR_CONSOLE_BG, foreground=cfg.COLOR_CONSOLE_FG,
            insertbackground=cfg.COLOR_CONSOLE_FG,
            font=(cfg.MONO_FONT, cfg.MONO_FONT_SIZE), state="disabled",
        )
        y_scroll = ttk.Scrollbar(self, orient="vertical", command=self.text.yview)
        x_scroll = ttk.Scrollbar(self, orient="horizontal", command=self.text.xview)
        self.text.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        self.text.tag_configure(self.TAG_INFO, foreground=cfg.COLOR_CONSOLE_INFO)
        self.text.tag_configure(self.TAG_OK, foreground=cfg.COLOR_CONSOLE_OK)
        self.text.tag_configure(self.TAG_ERROR, foreground=cfg.COLOR_CONSOLE_ERROR)

        x_scroll.pack(side="bottom", fill="x")
        y_scroll.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

        self._pending_return = False

    # --- content ------------------------------------------------------------
    def append(self, chunk: str, tag: str | None = None) -> None:
        self.text.configure(state="normal")
        for part in self._split_carriage_returns(chunk):
            if part == "\r":
                self._pending_return = True
                continue
            if self._pending_return:
                self._pending_return = False
                # a progress bar rewrites its line - drop the previous one
                self.text.delete("insert linestart", "insert lineend")
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
