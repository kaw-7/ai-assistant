import tkinter as tk
from tkinter import messagebox, ttk

try:
    import UI.ui_config as uiConf
    import UI.IssueModel as model
    import UI.theme as theme
    from UI.IssueDetail import IssueDetail
    from UI.IssueList import IssueList
    from UI.IssueSerializer import issueCards_to_markup
except ImportError:
    import ui_config as uiConf
    import IssueModel as model
    import theme
    from IssueDetail import IssueDetail
    from IssueList import IssueList
    from IssueSerializer import issueCards_to_markup

FILTER_ALL = "all"
FILTERS = ((FILTER_ALL, uiConf.ALL),) + tuple(
    (key, model.STATUS_LABELS[key]) for key in model.STATUS_KEYS)


def _shorten(path: str, keep: int = 70) -> str:
    return path if len(path) <= keep else "…" + path[-(keep - 1):]


class App(tk.Tk):
    """Issue list on the left, the selected issue on the right."""

    def __init__(self, items, items_file_path):
        super().__init__()
        self.title("Issue viewer")
        self.geometry(uiConf.GEOMETRY)
        self.minsize(900, 560)
        self.fonts = theme.apply(self)

        self.items = items
        self.items_file_path = items_file_path
        self._changed = set()          # indexes of the issues edited since the last save
        self._deleted = 0              # issues deleted since the last save
        self.editing = False           # edit mode is for the whole viewer, not one issue

        self.filter_var = tk.StringVar(value=FILTER_ALL)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_a: self._refresh_list())

        self._build_header()
        self._build_filters()
        self._build_body()

        self.bind("<Control-s>", lambda _e: self._save())
        self.bind("<Control-e>", lambda _e: self._toggle_edit())
        self.bind("<Control-f>", lambda _e: self.search.focus_set())
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._update_counts()
        self._refresh_list()
        self.issue_list.tree.focus_set()

    # --- construction -------------------------------------------------------
    def _build_header(self):
        header = ttk.Frame(self, style="Surface.TFrame",
                           padding=(theme.SPACE_L, theme.SPACE_XS))
        header.pack(fill="x")

        ttk.Button(header, text="Save to report", style="Accent.TButton",
                   command=self._save).pack(side="right")
        self.dirty_label = tk.Label(header, background=theme.SURFACE,
                                    foreground=theme.WARN_TEXT, font=self.fonts.small)
        self.dirty_label.pack(side="right", padx=theme.SPACE_M)
        # a fixed-size holder, so flipping between "Edit" and "Done" (the blue
        # style has a bold font) does not resize the button
        holder = tk.Frame(header, background=theme.SURFACE)
        holder.pack(side="right", padx=(theme.SPACE_M, 0))
        self.edit_button = ttk.Button(holder, text="Edit", command=self._toggle_edit)
        self.edit_button.place(relwidth=1, relheight=1)
        sizes = []
        for text, style in (("Edit", "TButton"), ("Done", "Accent.TButton")):
            self.edit_button.configure(text=text, style=style)
            sizes.append((self.edit_button.winfo_reqwidth(),
                          self.edit_button.winfo_reqheight()))
        self.edit_button.configure(text="Edit", style="TButton")
        holder.configure(width=max(w for w, _h in sizes),
                         height=max(h for _w, h in sizes))

        self.search = ttk.Entry(header, textvariable=self.search_var, width=32)
        self.search.pack(side="right", padx=(theme.SPACE_S, theme.SPACE_S))
        tk.Label(header, text="Search", background=theme.SURFACE,
                 foreground=theme.TEXT_MUTED, font=self.fonts.small).pack(side="right")

        titles = ttk.Frame(header, style="Surface.TFrame")
        titles.pack(side="left", fill="x", expand=True)
        # name and file on one line, so the header is only as high as its buttons
        tk.Label(titles, text="Issue viewer", background=theme.SURFACE,
                 foreground=theme.TEXT, font=self.fonts.heading).pack(side="left")
        tk.Label(titles, text=_shorten(str(self.items_file_path)), background=theme.SURFACE,
                 foreground=theme.TEXT_MUTED, font=self.fonts.mono).pack(
            side="left", padx=(theme.SPACE_M, 0))

        tk.Frame(self, height=1, background=theme.BORDER).pack(fill="x")

    def _build_filters(self):
        bar = ttk.Frame(self, style="Surface.TFrame",
                        padding=(theme.SPACE_L, theme.SPACE_XS))
        bar.pack(fill="x")
        self.filter_buttons = {}
        for key, _label in FILTERS:
            button = ttk.Radiobutton(bar, variable=self.filter_var, value=key,
                                     style="Chip.Toolbutton", command=self._refresh_list)
            button.pack(side="left", padx=(0, theme.SPACE_S))
            self.filter_buttons[key] = button

        # moving through the issues and deleting one, at the filters' level so
        # the details below keep their height for the texts
        ttk.Button(bar, text="Next", style="Icon.TButton",
                   command=lambda: self.issue_list.step(1)).pack(side="right")
        ttk.Button(bar, text="Previous", style="Icon.TButton",
                   command=lambda: self.issue_list.step(-1)).pack(
            side="right", padx=(0, theme.SPACE_XS))
        self.delete_button = ttk.Button(bar, text="Delete", style="Danger.TButton",
                                        command=self._delete_issue, state="disabled")
        self.delete_button.pack(side="right", padx=(0, theme.SPACE_M))
        tk.Frame(self, height=1, background=theme.BORDER).pack(fill="x")

    def _build_body(self):
        panes = ttk.PanedWindow(self, orient="horizontal")
        panes.pack(fill="both", expand=True)

        self.issue_list = IssueList(panes, self.fonts, on_select=self._on_select,
                                    on_delete=self._delete_issue)
        self.detail = IssueDetail(panes, self.fonts, on_change=self._on_change)
        panes.add(self.issue_list, weight=0)
        panes.add(self.detail, weight=1)
        # the list only shows the IDs - give it just their width (plus the
        # scrollbar). Done on the first real size, before that the width is still 1.
        def first_layout(event):
            if event.width > 1:
                panes.unbind("<Configure>", binding)
                panes.sashpos(0, self.issue_list.winfo_reqwidth())
        binding = panes.bind("<Configure>", first_layout, add="+")

    # --- list and filter ----------------------------------------------------
    def _refresh_list(self, keep=None):
        wanted = self.filter_var.get()
        query = self.search_var.get()
        indexes = [
            index for index, item in enumerate(self.items)
            if (wanted == FILTER_ALL or model.status_key(item) == wanted)
            and model.matches_query(item, query)
        ]
        if keep is None:
            keep = self.detail.index
        self.issue_list.set_rows(self.items, indexes)
        if keep in indexes:
            self.issue_list.select(keep)
        elif indexes:
            self.issue_list.select(indexes[0])
        else:
            self._on_select(None)

    def _update_counts(self):
        counts = {FILTER_ALL: len(self.items)}
        for item in self.items:
            key = model.status_key(item)
            counts[key] = counts.get(key, 0) + 1
        for key, label in FILTERS:
            self.filter_buttons[key].configure(text=f"{label}   {counts.get(key, 0)}")

    def _on_select(self, index):
        item = self.items[index] if index is not None else None
        self.detail.show(index, item, edited=index in self._changed)
        self._update_delete_button()

    def _update_delete_button(self):
        self.delete_button.configure(
            state="normal" if self.editing and self.detail.item is not None else "disabled")

    # --- edit mode ----------------------------------------------------------
    def _toggle_edit(self):
        self.editing = not self.editing
        self.edit_button.configure(text="Done" if self.editing else "Edit",
                                   style="Accent.TButton" if self.editing else "TButton")
        self.detail.set_editing(self.editing)
        self._update_delete_button()

    # --- changes ------------------------------------------------------------
    def _on_change(self, index):
        self._changed.add(index)
        # the row stays where it is even when it no longer fits the filter -
        # it would be confusing to see the issue vanish while working on it
        self.issue_list.update_row(index, self.items[index])
        self._update_counts()
        self._update_dirty()

    def _delete_issue(self):
        """Removes the shown issue from the list; the report changes on save."""
        index = self.detail.index
        if not self.editing or index is None:
            return
        if not messagebox.askyesno(
                "Issue viewer",
                f"Delete this issue from the report?\n\n{model.title(self.items[index])}\n\n"
                "It is removed from the report file when you save.",
                icon="warning", default="no", parent=self):
            return
        rows = self.issue_list.visible()
        position = rows.index(index) if index in rows else 0
        del self.items[index]
        # the indexes behind the deleted issue move one up
        def shift(i):
            return i - 1 if i > index else i
        self._changed = {shift(i) for i in self._changed if i != index}
        rows = [shift(i) for i in rows if i != index]
        self._deleted += 1
        self.detail.index = None
        self._refresh_list(keep=rows[min(position, len(rows) - 1)] if rows else None)
        self._update_counts()
        self._update_dirty()
        self.issue_list.tree.focus_set()

    def _unsaved(self) -> bool:
        return bool(self._changed or self._deleted)

    def _update_dirty(self):
        parts = []
        if self._changed:
            count = len(self._changed)
            parts.append(f"{count} {'issue' if count == 1 else 'issues'} changed")
        if self._deleted:
            parts.append(f"{self._deleted} deleted")
        if parts:
            self.dirty_label.configure(text=f"●  {', '.join(parts)}, not saved",
                                       foreground=theme.WARN_TEXT)
        else:
            self.dirty_label.configure(text="")

    def _save(self) -> bool:
        try:
            issueCards_to_markup(self.items, self.items_file_path)
        except OSError as exc:
            messagebox.showerror("Issue viewer", f"The report could not be saved:\n{exc}",
                                 parent=self)
            return False
        self._changed.clear()
        self._deleted = 0
        self.detail.mark_edited(False)
        self.dirty_label.configure(text="✓  Saved", foreground=theme.STATUS_COLORS[
            model.NO_RISK].fg)
        self.after(2500, self._update_dirty)
        return True

    def _on_close(self):
        if self._unsaved():
            answer = messagebox.askyesnocancel(
                "Issue viewer",
                f"{len(self._changed)} changed and {self._deleted} deleted issue(s)"
                " are not saved yet.\n"
                "Save them into the report before closing?",
                parent=self)
            if answer is None:
                return
            if answer and not self._save():
                return
        self.destroy()
