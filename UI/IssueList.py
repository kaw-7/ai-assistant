# -*- coding: utf-8 -*-
"""Left pane of the issue viewer: one row per issue - its status dot and ID."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

try:
    import UI.IssueModel as model
    import UI.theme as theme
except ImportError:
    import IssueModel as model
    import theme


# the status dot, the gaps around it and a little room on the right
DOT_AND_PADDING = 36
# how long the mouse rests on a row before its title shows
TOOLTIP_DELAY_MS = 450


class IssueList(ttk.Frame):
    """Shows the issues it is given; row ids are the indexes into the item list."""

    def __init__(self, master, fonts: theme.Fonts, on_select=None, on_delete=None):
        super().__init__(master, style="Surface.TFrame")
        self.on_select = on_select
        self.on_delete = on_delete
        self.fonts = fonts
        self._items: list[dict] = []
        self._tip_row = None        # the row the mouse is over
        self._tip_window = None
        self._tip_after = None
        self._dots = {key: theme.status_dot(self, key) for key in model.STATUS_KEYS}

        self.tree = ttk.Treeview(self, style="Issues.Treeview", selectmode="browse")
        self.tree.heading("#0", text="ID", anchor="w")
        # only the ID, so the details get the width; set_rows fits the column
        # to the longest ID, the title and the type are shown in the details
        self.font = fonts.body
        self.tree.column("#0", width=120, minwidth=60, stretch=True)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.footer = ttk.Label(self, style="Muted.Surface.TLabel",
                                padding=(theme.SPACE_S, theme.SPACE_XS))
        separator = tk.Frame(self, height=1, background=theme.DIVIDER)

        self.footer.pack(side="bottom", fill="x")
        separator.pack(side="bottom", fill="x")
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.tag_configure("improvement", foreground=theme.IMPROVEMENT)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree.bind("<Motion>", self._on_motion, add="+")
        self.tree.bind("<Leave>", lambda _e: self._hide_tip(), add="+")
        self.tree.bind("<ButtonPress>", lambda _e: self._hide_tip(), add="+")
        self.tree.bind("<MouseWheel>", lambda _e: self._hide_tip(), add="+")
        self.tree.bind("<Delete>", lambda _e: callable(self.on_delete) and self.on_delete())

    # --- content ------------------------------------------------------------
    def set_rows(self, items: list[dict], indexes: list[int]) -> None:
        self._hide_tip()
        self._items = items
        self.tree.delete(*self.tree.get_children())
        for index in indexes:
            self.tree.insert("", "end", iid=str(index), **self._row(items[index]))
        # wide enough for the dot and the longest ID of all issues - not only
        # the shown ones, so the list keeps its width when filtering
        widest = max((self.font.measure(self._row(item)["text"]) for item in items),
                     default=0)
        self.tree.column("#0", width=widest + DOT_AND_PADDING)
        self.footer.configure(text=f"{len(indexes)} of {len(items)} issues")

    def update_row(self, index: int, item: dict) -> None:
        if self.tree.exists(str(index)):
            self.tree.item(str(index), **self._row(item))

    def _row(self, item: dict) -> dict:
        ids = model.defect_ids(item)
        shown_id = ids[0] + (f" +{len(ids) - 1}" if len(ids) > 1 else "") if ids else ""
        return {
            "text": "  " + (shown_id or "(no ID)"),
            "image": self._dots[model.status_key(item)],
            "tags": ("improvement",) if model.is_improvement(item) else (),
        }

    # --- tooltip: the title of the row under the mouse -----------------------
    def _on_motion(self, event) -> None:
        row = self.tree.identify_row(event.y)
        if row == self._tip_row:
            return
        self._hide_tip()
        self._tip_row = row
        if row:
            self._tip_after = self.after(TOOLTIP_DELAY_MS, self._show_tip)

    def _show_tip(self) -> None:
        self._tip_after = None
        row = self._tip_row
        if not row or not self.tree.exists(row) or int(row) >= len(self._items):
            return
        box = self.tree.bbox(row)
        if not box:
            return
        _x, y, _w, height = box
        x = self.tree.winfo_rootx() + self.tree.winfo_width() + 4
        y = self.tree.winfo_rooty() + y + (height - 4) // 2 - 10
        self._tip_window = tk.Toplevel(self)
        self._tip_window.wm_overrideredirect(True)
        self._tip_window.wm_geometry(f"+{x}+{y}")
        tk.Label(self._tip_window, text=model.title(self._items[int(row)]),
                 justify="left", wraplength=560, background=theme.DARK,
                 foreground="#FFFFFF", font=self.fonts.small).pack(ipadx=8, ipady=4)

    def _hide_tip(self) -> None:
        self._tip_row = None
        if self._tip_after is not None:
            self.after_cancel(self._tip_after)
            self._tip_after = None
        if self._tip_window is not None:
            self._tip_window.destroy()
            self._tip_window = None

    # --- selection ----------------------------------------------------------
    def visible(self) -> list[int]:
        return [int(iid) for iid in self.tree.get_children()]

    def selected(self) -> int | None:
        selection = self.tree.selection()
        return int(selection[0]) if selection else None

    def select(self, index: int | None) -> None:
        if index is None or not self.tree.exists(str(index)):
            self.tree.selection_set(())
            return
        self.tree.selection_set(str(index))
        self.tree.focus(str(index))
        self.tree.see(str(index))

    def step(self, delta: int) -> None:
        """Move the selection ``delta`` rows up or down."""
        rows = self.visible()
        if not rows:
            return
        current = self.selected()
        position = rows.index(current) if current in rows else -delta
        position = max(0, min(len(rows) - 1, position + delta))
        self.select(rows[position])

    def _on_tree_select(self, _event=None) -> None:
        if callable(self.on_select):
            self.on_select(self.selected())
