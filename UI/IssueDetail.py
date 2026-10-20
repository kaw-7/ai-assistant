# -*- coding: utf-8 -*-
"""Right pane of the issue viewer: the selected issue, read or edited.

Read mode shows the texts as plain, selectable text.  Edit mode - switched
for the whole viewer by the App, see ``set_editing`` - makes the title, the
defect description, the risk assessment and the status changeable; every
change is written into the issue dictionary straight away and reported
through ``on_change``.  Nothing here reacts to the mouse wheel except the
text boxes, which scroll.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

try:
    import UI.ui_config as uiConf
    import UI.IssueModel as model
    import UI.theme as theme
except ImportError:
    import ui_config as uiConf
    import IssueModel as model
    import theme

DEFECT_MIN_LINES = 1
DEFECT_MAX_LINES = 8
# a longer title scrolls, so it cannot push the texts below out of the window
TITLE_MAX_LINES = 3


class _StatusButton(tk.Frame):
    """A status choice: coloured when chosen, clickable only in edit mode."""

    def __init__(self, master, key: str, fonts: theme.Fonts, on_pick):
        super().__init__(master, background=theme.BORDER_STRONG, takefocus=True)
        self.key = key
        self.on_pick = on_pick
        self.enabled = False
        colors = theme.STATUS_COLORS[key]
        self.label = tk.Label(self, text=f"{colors.icon}  {model.STATUS_LABELS[key]}",
                              font=fonts.small_bold,
                              padx=theme.SPACE_S, pady=0)
        self.label.pack(padx=1, pady=1)
        for widget in (self, self.label):
            widget.bind("<Button-1>", self._click)
        self.bind("<Key-space>", self._click)
        self.bind("<Return>", self._click)
        self.bind("<FocusIn>", lambda _e: self.configure(background=theme.ACCENT))
        self.bind("<FocusOut>", lambda _e: self.paint(self._chosen, self.enabled))
        self._chosen = False

    def paint(self, chosen: bool, enabled: bool) -> None:
        self._chosen = chosen
        self.enabled = enabled
        colors = theme.STATUS_COLORS[self.key]
        if chosen:
            bg, fg, border = colors.bg, colors.fg, colors.border
        else:
            bg = theme.SURFACE
            fg = theme.TEXT_SOFT if enabled else theme.TEXT_DISABLED
            border = theme.BORDER_STRONG if enabled else theme.BORDER
        self.configure(background=border, takefocus=enabled,
                       cursor="hand2" if enabled else "")
        self.label.configure(background=bg, foreground=fg,
                             cursor="hand2" if enabled else "")

    def _click(self, _event=None):
        if self.enabled and callable(self.on_pick):
            self.on_pick(self.key)
        return "break"


class IssueDetail(tk.Frame):

    def __init__(self, master, fonts: theme.Fonts, on_change=None):
        super().__init__(master, background=theme.GROUND)
        self.fonts = fonts
        self.on_change = on_change
        self.editing = False
        self.index: int | None = None
        self.item: dict | None = None

        self._empty = tk.Label(self, text="No issue matches the filter.",
                               background=theme.GROUND, foreground=theme.TEXT_MUTED,
                               font=fonts.body)
        self.body = tk.Frame(self, background=theme.GROUND)
        self._build_header()
        self._build_status()
        self._build_texts()

    # --- construction -------------------------------------------------------
    def _build_header(self):
        header = tk.Frame(self.body, background=theme.GROUND)
        header.pack(fill="x")

        # the title is the description of the issue, as it is in the report;
        # over the whole width, at most TITLE_MAX_LINES high - a longer one
        # gets a scrollbar instead of pushing the cards down
        title_row = tk.Frame(header, background=theme.GROUND)
        title_row.pack(fill="x")
        self.title = tk.Text(title_row, height=1, wrap="word", font=self.fonts.heading,
                             background=theme.GROUND, foreground=theme.TEXT,
                             relief="flat", borderwidth=0, highlightthickness=1,
                             highlightbackground=theme.GROUND,
                             highlightcolor=theme.GROUND, undo=True,
                             padx=2, pady=1, cursor="arrow",
                             insertbackground=theme.TEXT,
                             selectbackground=theme.ACCENT_SOFT,
                             selectforeground=theme.TEXT,
                             inactiveselectbackground=theme.ACCENT_SOFT)
        self.title_scrollbar = ttk.Scrollbar(title_row, orient="vertical",
                                             command=self.title.yview)
        self.title.configure(yscrollcommand=self.title_scrollbar.set, state="disabled")
        self.title.pack(side="left", fill="x", expand=True)
        self.title.bind("<Configure>", lambda _e: self._fit_title())

    def _build_status(self):
        row = tk.Frame(self.body, background=theme.GROUND)
        row.pack(fill="x", pady=(theme.SPACE_M, 0))
        # all IDs of the issue, left of the status; many IDs wrap, so they
        # never push the status buttons out of the window
        self.ids_label = tk.Label(row, background=theme.GROUND, foreground=theme.TEXT,
                                  font=self.fonts.small_bold, justify="left", anchor="w")
        self.ids_label.pack(side="left", padx=(0, theme.SPACE_L))
        status = tk.Frame(row, background=theme.GROUND)
        status.pack(side="left")
        row.bind("<Configure>", lambda e: self.ids_label.configure(
            wraplength=max(120, e.width - status.winfo_reqwidth() - theme.SPACE_L)))
        tk.Label(status, text="STATUS", background=theme.GROUND, foreground=theme.TEXT_MUTED,
                 font=self.fonts.small_bold).pack(side="left", padx=(0, theme.SPACE_M))
        self.status_buttons = []
        for key in model.STATUS_KEYS:
            button = _StatusButton(status, key, self.fonts, self._on_status)
            button.pack(side="left", padx=(0, theme.SPACE_S))
            self.status_buttons.append(button)

    def _build_texts(self):
        defect_card = theme.card(self.body)
        defect_card.pack(fill="x", pady=(theme.SPACE_M, 0))
        self._card_heading(defect_card, "DEFECT DESCRIPTION · FROM THE RELEASE NOTES")
        self.defect_text = self._text_box(defect_card, height=DEFECT_MIN_LINES)
        self.defect_text.pack(fill="x", padx=theme.SPACE_S, pady=(0, theme.SPACE_S))
        self.defect_text.bind("<Configure>", lambda _e: self._fit_defect())

        # packed from the bottom first, so the growing risk card cannot push it out
        # bottom line: the type, the source, then the edit mode on the right
        footer = tk.Frame(self.body, background=theme.GROUND)
        footer.pack(side="bottom", fill="x", pady=(theme.SPACE_S, 0))
        self.mode_label = tk.Label(footer, background=theme.GROUND, font=self.fonts.small)
        self.mode_label.pack(side="right")
        self.edited_tag = tk.Label(footer, text="edited", background=theme.WARN_SOFT,
                                   foreground=theme.WARN_TEXT, font=self.fonts.small_bold,
                                   padx=theme.SPACE_S - 2)
        self.tags = tk.Frame(footer, background=theme.GROUND)
        self.tags.pack(side="left")
        self.source = tk.Label(footer, background=theme.GROUND,
                               foreground=theme.TEXT_MUTED, font=self.fonts.small,
                               anchor="w")
        self.source.pack(side="left", fill="x", expand=True)

        risk_card = theme.card(self.body)
        risk_card.pack(fill="both", expand=True, pady=(theme.SPACE_M, 0))
        self._card_heading(risk_card, "RISK ASSESSMENT")
        holder = tk.Frame(risk_card, background=theme.SURFACE)
        holder.pack(fill="both", expand=True, padx=(theme.SPACE_S, theme.SPACE_XS),
                    pady=(0, theme.SPACE_S))
        self.risk_text = self._text_box(holder, height=6)
        scrollbar = ttk.Scrollbar(holder, orient="vertical", command=self.risk_text.yview)

        # the scrollbar only shows when the text does not fit. Stable: hiding it
        # makes the text wider, so a text that fitted with it still fits without.
        def scrolled(first, last):
            scrollbar.set(first, last)
            fits = float(first) <= 0.0 and float(last) >= 1.0
            if fits and scrollbar.winfo_manager():
                scrollbar.pack_forget()
            elif not fits and not scrollbar.winfo_manager():
                scrollbar.pack(side="right", fill="y", before=self.risk_text)
        self.risk_text.configure(yscrollcommand=scrolled)
        self.risk_text.pack(side="left", fill="both", expand=True)

        self._bind_sync(self.title, uiConf.DESCRIPTION)
        self._bind_sync(self.defect_text, uiConf.DEFECT_DESCRIPTION)
        self._bind_sync(self.risk_text, uiConf.RISK_ASSESSMENT)

    def _card_heading(self, card, text) -> None:
        tk.Label(card, text=text, background=theme.SURFACE, foreground=theme.TEXT_MUTED,
                 font=self.fonts.small_bold, anchor="w").pack(
            fill="x", padx=theme.SPACE_M, pady=(theme.SPACE_M, theme.SPACE_XS))

    def _text_box(self, master, height) -> tk.Text:
        return tk.Text(master, height=height, wrap="word", font=self.fonts.body,
                       background=theme.SURFACE, foreground=theme.TEXT,
                       relief="flat", borderwidth=0, highlightthickness=1,
                       highlightbackground=theme.SURFACE, highlightcolor=theme.SURFACE,
                       padx=theme.SPACE_XS, pady=theme.SPACE_XS, spacing2=3, spacing3=6, undo=True,
                       insertbackground=theme.TEXT, selectbackground=theme.ACCENT_SOFT,
                       selectforeground=theme.TEXT, inactiveselectbackground=theme.ACCENT_SOFT)

    # --- showing an issue ---------------------------------------------------
    def show(self, index: int | None, item: dict | None, edited: bool = False) -> None:
        self.index, self.item = index, item
        if item is None:
            self.body.pack_forget()
            self._empty.pack(expand=True)
            return
        self._empty.pack_forget()
        self.body.pack(fill="both", expand=True, padx=theme.SPACE_M,
                       pady=(theme.SPACE_M, theme.SPACE_S))

        self.ids_label.configure(text=", ".join(model.defect_ids(item)))
        for child in self.tags.winfo_children():
            child.destroy()
        kind = model.kind(item)
        if kind and model.is_improvement(item):
            tk.Label(self.tags, text=kind, background=theme.IMPROVEMENT_SOFT,
                     foreground=theme.IMPROVEMENT, font=self.fonts.small_bold, padx=6,
                     highlightthickness=1, highlightbackground=theme.IMPROVEMENT
                     ).pack(side="left", padx=(0, theme.SPACE_S))
        elif kind:
            tk.Label(self.tags, text=kind, background=theme.GROUND,
                     foreground=theme.TEXT_SOFT, font=self.fonts.small, padx=6,
                     highlightthickness=1, highlightbackground=theme.BORDER_STRONG
                     ).pack(side="left", padx=(0, theme.SPACE_S))

        self.title.configure(foreground=theme.IMPROVEMENT if model.is_improvement(item)
                             else theme.TEXT)
        self._load(self.title, item.get(uiConf.DESCRIPTION, ""))
        source = (item.get(uiConf.SOURCE) or "").strip()
        self.source.configure(text=f"Source: {source}" if source else "")
        self._load(self.defect_text, item.get(uiConf.DEFECT_DESCRIPTION, ""))
        self._load(self.risk_text, item.get(uiConf.RISK_ASSESSMENT, ""))
        self.mark_edited(edited)
        self._paint()
        self._fit_title()
        self._fit_defect()

    def mark_edited(self, edited: bool) -> None:
        if edited:
            self.edited_tag.pack(side="right", padx=(0, theme.SPACE_M))
        else:
            self.edited_tag.pack_forget()

    def _load(self, widget: tk.Text, text: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text or "")
        widget.edit_reset()
        widget.edit_modified(False)
        widget.yview_moveto(0.0)
        if not self.editing:
            widget.configure(state="disabled")

    def _fit_title(self) -> None:
        widget = self.title
        lines = int(widget.tk.call(widget._w, "count", "-displaylines", "1.0", "end-1c") or 0) + 1
        height = max(1, min(lines, TITLE_MAX_LINES))
        if int(widget.cget("height")) != height:
            widget.configure(height=height)
        if lines > TITLE_MAX_LINES:
            if not self.title_scrollbar.winfo_manager():
                self.title_scrollbar.pack(side="right", fill="y", before=widget)
        elif self.title_scrollbar.winfo_manager():
            self.title_scrollbar.pack_forget()

    def _fit_defect(self) -> None:
        widget = self.defect_text
        # counts the line breaks between the two indexes - one less than the lines
        lines = int(widget.tk.call(widget._w, "count", "-displaylines", "1.0", "end-1c") or 0) + 1
        # one spare line while editing, so typing at the end does not scroll
        height = max(DEFECT_MIN_LINES, min(lines, DEFECT_MAX_LINES)) + int(self.editing)
        if int(widget.cget("height")) != height:
            widget.configure(height=height)

    # --- editing ------------------------------------------------------------
    def set_editing(self, editing: bool) -> None:
        """Edit mode belongs to the viewer: it stays on from issue to issue."""
        self.editing = editing
        self._paint()
        self._fit_defect()

    def _paint(self) -> None:
        editing = self.editing
        self.mode_label.configure(
            text=f"✎ Edit mode {'on' if editing else 'off'} (Ctrl+E)",
            foreground=theme.ACCENT if editing else theme.TEXT_MUTED)
        current = model.status_key(self.item) if self.item is not None else None
        for button in self.status_buttons:
            button.paint(button.key == current, editing)
        for widget, ground in ((self.title, theme.GROUND),
                               (self.defect_text, theme.SURFACE),
                               (self.risk_text, theme.SURFACE)):
            widget.configure(
                state="normal" if editing else "disabled",
                cursor="xterm" if editing else "arrow",
                highlightbackground=theme.BORDER_STRONG if editing else ground,
                highlightcolor=theme.ACCENT if editing else ground,
            )

    def _on_status(self, key: str) -> None:
        if self.item is None or model.status_key(self.item) == key:
            return
        model.set_status(self.item, key)
        self._paint()
        self._changed()

    def _bind_sync(self, widget: tk.Text, key: str) -> None:
        def sync(_event=None):
            if not widget.edit_modified():
                return
            widget.edit_modified(False)
            if self.item is None:
                return
            text = widget.get("1.0", "end-1c")
            if text == self.item.get(key, ""):   # loading a new issue, no edit
                return
            self.item[key] = text
            if widget is self.defect_text:
                self._fit_defect()
            elif widget is self.title:
                self._fit_title()
            self._changed()
        widget.bind("<<Modified>>", sync)

    def _changed(self) -> None:
        self.mark_edited(True)
        if callable(self.on_change):
            self.on_change(self.index)
