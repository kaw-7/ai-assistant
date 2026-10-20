# -*- coding: utf-8 -*-
"""Left pane of the issue viewer: one row per issue, a dot for its status."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

try:
    import UI.IssueModel as model
    import UI.theme as theme
except ImportError:
    import IssueModel as model
    import theme


class IssueList(ttk.Frame):
    """Shows the issues it is given; row ids are the indexes into the item list."""

    def __init__(self, master, fonts: theme.Fonts, on_select=None, on_delete=None):
        super().__init__(master, style="Surface.TFrame")
        self.on_select = on_select
        self.on_delete = on_delete
        self._dots = {key: theme.status_dot(self, key) for key in model.STATUS_KEYS}

        self.tree = ttk.Treeview(self, style="Issues.Treeview",
                                 columns=("id",), selectmode="browse")
        self.tree.heading("#0", text="ISSUE", anchor="w")
        self.tree.heading("id", text="ID", anchor="w")
        # wide enough for "BAUHAUS-30395 +1"; the type is shown in the details
        id_width = fonts.body.measure("BAUHAUS-00000 +0") + 16
        self.tree.column("#0", width=200, minwidth=160, stretch=True)
        self.tree.column("id", width=id_width, minwidth=id_width // 2, stretch=False)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.footer = ttk.Label(self, style="Muted.Surface.TLabel",
                                padding=(theme.SPACE_M, theme.SPACE_S))
        separator = tk.Frame(self, height=1, background=theme.DIVIDER)

        self.footer.pack(side="bottom", fill="x")
        separator.pack(side="bottom", fill="x")
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True,
                       padx=(theme.SPACE_XS, 0), pady=(theme.SPACE_XS, 0))

        self.tree.tag_configure("improvement", foreground=theme.IMPROVEMENT)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree.bind("<Delete>", lambda _e: callable(self.on_delete) and self.on_delete())

    # --- content ------------------------------------------------------------
    def set_rows(self, items: list[dict], indexes: list[int]) -> None:
        self.tree.delete(*self.tree.get_children())
        for index in indexes:
            self.tree.insert("", "end", iid=str(index), **self._row(items[index]))
        self.footer.configure(text=f"{len(indexes)} of {len(items)} issues"
                                   "  ·  ↑ ↓ move between issues  ·  Del deletes (edit mode)")

    def update_row(self, index: int, item: dict) -> None:
        if self.tree.exists(str(index)):
            self.tree.item(str(index), **self._row(item))

    def _row(self, item: dict) -> dict:
        ids = model.defect_ids(item)
        shown_id = ids[0] + (f" +{len(ids) - 1}" if len(ids) > 1 else "") if ids else ""
        return {
            "text": "  " + model.title(item),
            "image": self._dots[model.status_key(item)],
            "values": (shown_id,),
            "tags": ("improvement",) if model.is_improvement(item) else (),
        }

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
