# -*- coding: utf-8 -*-
"""Right pane of the issue viewer: the selected issue, read or edited.

Read mode shows the texts as plain, selectable text.  Edit mode - switched
for the whole viewer by the App, see ``set_editing`` - makes the defect
description, the risk assessment and the status changeable; every
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
                              font=fonts.body_bold,
                              padx=theme.SPACE_M, pady=theme.SPACE_XS + 1)
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

    def __init__(self, master, fonts: theme.Fonts, on_change=None,
                 on_prev=None, on_next=None, on_delete=None):
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
        self._build_header(on_prev, on_next, on_delete)
        self._build_status()
        self._build_texts()

    # --- construction -------------------------------------------------------
    def _build_header(self, on_prev, on_next, on_delete):
        header = tk.Frame(self.body, background=theme.GROUND)
        header.pack(fill="x")

        # first line: IDs and type on the left, edit mode and navigation on the right
        top = tk.Frame(header, background=theme.GROUND)
        top.pack(fill="x", pady=(0, theme.SPACE_S))
        buttons = tk.Frame(top, background=theme.GROUND)
        buttons.pack(side="right")
        self.mode_label = tk.Label(buttons, background=theme.GROUND, font=self.fonts.small)
        self.mode_label.pack(side="left", padx=(0, theme.SPACE_M))
        self.delete_button = ttk.Button(buttons, text="Delete", style="Danger.TButton",
                                        command=on_delete, state="disabled")
        self.delete_button.pack(side="left", padx=(0, theme.SPACE_M))
        ttk.Button(buttons, text="Previous", style="Icon.TButton",
                   command=on_prev).pack(side="left")
        ttk.Button(buttons, text="Next", style="Icon.TButton",
                   command=on_next).pack(side="left", padx=(theme.SPACE_XS, 0))

        self.tags = tk.Frame(top, background=theme.GROUND)
        self.tags.pack(side="left")
        self.edited_tag = tk.Label(top, text="edited", background=theme.WARN_SOFT,
                                   foreground=theme.WARN_TEXT, font=self.fonts.small_bold,
                                   padx=theme.SPACE_S - 2)

        # second line: the title over the whole width, at most TITLE_MAX_LINES
        # high - a longer one gets a scrollbar instead of pushing the cards down
        title_row = tk.Frame(header, background=theme.GROUND)
        title_row.pack(fill="x")
        self.title = tk.Text(title_row, height=1, wrap="word", font=self.fonts.title,
                             background=theme.GROUND, foreground=theme.TEXT,
                             relief="flat", borderwidth=0, highlightthickness=0,
                             padx=0, pady=0, cursor="arrow",
                             selectbackground=theme.ACCENT_SOFT,
                             selectforeground=theme.TEXT,
                             inactiveselectbackground=theme.ACCENT_SOFT)
        self.title_scrollbar = ttk.Scrollbar(title_row, orient="vertical",
                                             command=self.title.yview)
        self.title.configure(yscrollcommand=self.title_scrollbar.set, state="disabled")
        self.title.pack(side="left", fill="x", expand=True)
        self.title.bind("<Configure>", lambda _e: self._fit_title())

    def _build_status(self):
        block = tk.Frame(self.body, background=theme.GROUND)
        block.pack(fill="x", pady=(theme.SPACE_L, 0))
        tk.Label(block, text="STATUS", background=theme.GROUND,
                 foreground=theme.TEXT_MUTED, font=self.fonts.small_bold).pack(anchor="w")
        row = tk.Frame(block, background=theme.GROUND)
        row.pack(fill="x", pady=(theme.SPACE_XS, 0))
        self.status_buttons = []
        for key in model.STATUS_KEYS:
            button = _StatusButton(row, key, self.fonts, self._on_status)
            button.pack(side="left", padx=(0, theme.SPACE_S))
            self.status_buttons.append(button)

    def _build_texts(self):
        defect_card = theme.card(self.body)
        defect_card.pack(fill="x", pady=(theme.SPACE_L, 0))
        self._card_heading(defect_card, "DEFECT DESCRIPTION · FROM THE RELEASE NOTES")
        self.defect_text = self._text_box(defect_card, height=DEFECT_MIN_LINES)
        self.defect_text.pack(fill="x", padx=theme.SPACE_M, pady=(0, theme.SPACE_M))
        self.defect_text.bind("<Configure>", lambda _e: self._fit_defect())

        # packed from the bottom first, so the growing risk card cannot push it out
        self.source = tk.Label(self.body, background=theme.GROUND,
                               foreground=theme.TEXT_MUTED, font=self.fonts.small,
                               anchor="w")
        self.source.pack(side="bottom", fill="x", pady=(theme.SPACE_S, 0))

        risk_card = theme.card(self.body)
        risk_card.pack(fill="both", expand=True, pady=(theme.SPACE_M, 0))
        self._card_heading(risk_card, "RISK ASSESSMENT")
        holder = tk.Frame(risk_card, background=theme.SURFACE)
        holder.pack(fill="both", expand=True, padx=(theme.SPACE_M, theme.SPACE_XS),
                    pady=(0, theme.SPACE_M))
        self.risk_text = self._text_box(holder, height=6)
        scrollbar = ttk.Scrollbar(holder, orient="vertical", command=self.risk_text.yview)
        self.risk_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.risk_text.pack(side="left", fill="both", expand=True)

        self._bind_sync(self.defect_text, uiConf.DEFECT_DESCRIPTION)
        self._bind_sync(self.risk_text, uiConf.RISK_ASSESSMENT)

    def _card_heading(self, card, text) -> None:
        tk.Label(card, text=text, background=theme.SURFACE, foreground=theme.TEXT_MUTED,
                 font=self.fonts.small_bold, anchor="w").pack(
            fill="x", padx=theme.SPACE_M + 4, pady=(theme.SPACE_M, theme.SPACE_XS))

    def _text_box(self, master, height) -> tk.Text:
        return tk.Text(master, height=height, wrap="word", font=self.fonts.body,
                       background=theme.SURFACE, foreground=theme.TEXT,
                       relief="flat", borderwidth=0, highlightthickness=1,
                       highlightbackground=theme.SURFACE, highlightcolor=theme.SURFACE,
                       padx=4, pady=4, spacing2=3, spacing3=6, undo=True,
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
        self.body.pack(fill="both", expand=True, padx=theme.SPACE_XL + 8,
                       pady=theme.SPACE_XL)

        for child in self.tags.winfo_children():
            child.destroy()
        for defect_id in model.defect_ids(item):
            tk.Label(self.tags, text=defect_id, background=theme.CHIP,
                     foreground=theme.TEXT_SOFT, font=self.fonts.mono,
                     padx=6, pady=1).pack(side="left", padx=(0, theme.SPACE_XS))
        kind = model.kind(item)
        if kind and model.is_improvement(item):
            tk.Label(self.tags, text=kind, background=theme.IMPROVEMENT_SOFT,
                     foreground=theme.IMPROVEMENT, font=self.fonts.small_bold, padx=6,
                     highlightthickness=1, highlightbackground=theme.IMPROVEMENT
                     ).pack(side="left", padx=(0, theme.SPACE_XS))
        elif kind:
            tk.Label(self.tags, text=kind, background=theme.GROUND,
                     foreground=theme.TEXT_SOFT, font=self.fonts.small, padx=6,
                     highlightthickness=1, highlightbackground=theme.BORDER_STRONG
                     ).pack(side="left", padx=(0, theme.SPACE_XS))

        self.title.configure(state="normal",
                             foreground=theme.IMPROVEMENT if model.is_improvement(item)
                             else theme.TEXT)
        self.title.delete("1.0", "end")
        self.title.insert("1.0", model.title(item))
        self.title.configure(state="disabled")
        self.title.yview_moveto(0.0)
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
            self.edited_tag.pack(side="left", padx=(theme.SPACE_XS, 0))
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
        self.delete_button.configure(
            state="normal" if editing and self.item is not None else "disabled")
        current = model.status_key(self.item) if self.item is not None else None
        for button in self.status_buttons:
            button.paint(button.key == current, editing)
        for widget in (self.defect_text, self.risk_text):
            widget.configure(
                state="normal" if editing else "disabled",
                cursor="xterm" if editing else "arrow",
                highlightbackground=theme.BORDER_STRONG if editing else theme.SURFACE,
                highlightcolor=theme.ACCENT if editing else theme.SURFACE,
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
            self._changed()
        widget.bind("<<Modified>>", sync)

    def _changed(self) -> None:
        self.mark_edited(True)
        if callable(self.on_change):
            self.on_change(self.index)
