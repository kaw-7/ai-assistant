# -*- coding: utf-8 -*-
"""The configuration editor of the launcher.

The panel is built completely out of the :class:`ConfigField` descriptors the
selected module exposes, so a new module gets its editor for free.

Two kinds of entries are shown:

* plain values - editable straight away, stored as an override as soon as they
  differ from what stands in the configuration file; they are then tagged
  "edited" and get a Reset button;
* derived values (f-strings, references to other entries) - tagged "computed",
  shown read only and recomputed while the values they depend on are edited.
  Switching "Override" on pins such an entry to a value of its own.

Every section is a card; the list on the left jumps to a section and follows
the scrolling.
"""
from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk
from typing import Any, Dict, List, Tuple

import UI.theme as theme
from Launcher.core.config_fields import ConfigField, FieldKind
from Launcher.core.config_sources import ConfigSource
from Launcher.core.project import PROJECT_ROOT

from . import launcher_config as cfg
from .widgets import ScrollableFrame, Tooltip

# text on the choice buttons; the stored value stays the configured one
_CHOICE_LABELS = {"y": "Yes", "n": "No"}


def _keep_compact(holder) -> None:
    """The spare width goes behind the actions, not into the value widget."""
    holder.columnconfigure(1, weight=0)
    holder.columnconfigure(9, weight=1)


class _FieldEditor:
    """One row of a section card: label and hint, the value, its state tags.

    ``parent`` is the card's grid; the row takes grid rows ``2*row`` (the
    divider) and ``2*row+1`` (the content).
    """

    def __init__(self, parent, field: ConfigField, row: int, fonts: theme.Fonts,
                 on_commit, on_reset):
        self.field = field
        self.fonts = fonts
        self.on_commit = on_commit
        self.on_reset = on_reset
        self.override_var: tk.BooleanVar | None = None
        self.var: tk.Variable
        self._choice_buttons: List[ttk.Radiobutton] = []

        if row:
            tk.Frame(parent, height=1, background=theme.DIVIDER).grid(
                row=2 * row, column=0, columnspan=2, sticky="ew")

        # --- left: label, state tags, hint
        left = tk.Frame(parent, background=theme.SURFACE)
        left.grid(row=2 * row + 1, column=0, sticky="nw", pady=theme.SPACE_S + 2,
                  padx=(0, theme.SPACE_L))
        line = tk.Frame(left, background=theme.SURFACE)
        line.pack(anchor="w")
        self.label = tk.Label(line, text=field.label, background=theme.SURFACE,
                              foreground=theme.TEXT, font=fonts.body, anchor="w",
                              justify="left", wraplength=cfg.LABEL_WIDTH - 80)
        self.label.pack(side="left")
        self.edited_tag = self._tag(line, "edited", theme.WARN_SOFT, theme.WARN_TEXT)
        if field.derived:
            self._tag(line, "computed", theme.CHIP, theme.TEXT_SOFT).pack(
                side="left", padx=(6, 0))
        if field.help:
            tk.Label(left, text=field.help, background=theme.SURFACE,
                     foreground=theme.TEXT_MUTED, font=fonts.small, anchor="w",
                     justify="left", wraplength=cfg.LABEL_WIDTH - 10).pack(anchor="w")

        # --- right: amber edge while edited, the value, the actions
        holder = tk.Frame(parent, background=theme.SURFACE)
        holder.grid(row=2 * row + 1, column=1, sticky="ew", pady=theme.SPACE_S)
        holder.columnconfigure(1, weight=1)
        self.edge = tk.Frame(holder, width=3, background=theme.SURFACE)
        self.edge.grid(row=0, column=0, sticky="ns", padx=(0, 4))
        self.widget = self._build_widget(holder)

        column = 2
        if field.kind in (FieldKind.FILE, FieldKind.DIR):
            browse = ttk.Button(holder, text="…", width=3, style="Icon.TButton",
                                command=self._browse)
            browse.grid(row=0, column=column, padx=(6, 0))
            Tooltip(browse, "Choose the folder" if field.kind is FieldKind.DIR
                    else "Choose the file")
            column += 1
        if field.derived:
            self.override_var = tk.BooleanVar(value=False)
            toggle = ttk.Checkbutton(holder, text="Override", style="Override.Toolbutton",
                                     variable=self.override_var,
                                     command=self._on_override_toggled)
            toggle.grid(row=0, column=column, padx=(6, 0))
            Tooltip(toggle, "This value is computed from the other settings. "
                            "Switch Override on to set it by hand instead.")
            column += 1
        # shown only while a plain value differs from the file - see mark()
        self.reset_button = ttk.Button(holder, text="Reset", style="Link.TButton",
                                       command=lambda: self.on_reset(self))
        self._reset_column = column

        self._apply_enabled_state()

    def _tag(self, master, text, background, foreground) -> tk.Label:
        return tk.Label(master, text=text, background=background, foreground=foreground,
                        font=self.fonts.small_bold, padx=6)

    # --- construction -------------------------------------------------------
    def _build_widget(self, holder):
        field = self.field
        if field.kind is FieldKind.BOOL:
            _keep_compact(holder)
            self.var = tk.BooleanVar(value=bool(field.default))
            widget = ttk.Checkbutton(holder, variable=self.var,
                                     style="Surface.TCheckbutton", command=self._commit)
            widget.grid(row=0, column=1, sticky="w")
            return widget

        self.var = tk.StringVar(value=field.to_display(field.default))

        if field.kind is FieldKind.CHOICE and 0 < len(field.choices) <= cfg.CHOICE_BUTTONS_MAX:
            _keep_compact(holder)
            # a few choices are buttons: one click, and the wheel cannot touch them
            widget = tk.Frame(holder, background=theme.SURFACE)
            widget.grid(row=0, column=1, sticky="w")
            for choice in field.choices:
                button = ttk.Radiobutton(widget, text=_CHOICE_LABELS.get(choice, choice),
                                         value=choice, variable=self.var,
                                         style="Chip.Toolbutton", command=self._commit)
                button.pack(side="left", padx=(0, 6))
                self._choice_buttons.append(button)
            return widget

        if field.kind is FieldKind.CHOICE:
            widget = ttk.Combobox(holder, textvariable=self.var,
                                  values=list(field.choices), state="readonly")
            widget.grid(row=0, column=1, sticky="ew")
            widget.bind("<<ComboboxSelected>>", lambda _e: self._commit())
            # the wheel must scroll the form, never change the selected value:
            # drop the class binding so the event reaches the scrollable frame
            widget.unbind_class("TCombobox", "<MouseWheel>")
            widget.unbind_class("TCombobox", "<Button-4>")
            widget.unbind_class("TCombobox", "<Button-5>")
            return widget

        if field.kind is FieldKind.MULTILINE:
            widget = tk.Text(holder, height=4, wrap="word", font=self.fonts.mono,
                             relief="flat", borderwidth=0, highlightthickness=1,
                             highlightbackground=theme.BORDER_STRONG,
                             highlightcolor=theme.ACCENT, padx=6, pady=4)
            widget.insert("1.0", self.var.get())
            widget.grid(row=0, column=1, sticky="ew")
            widget.bind("<FocusOut>", lambda _e: self._commit())
            return widget

        show = "•" if field.secret else ""
        widget = ttk.Entry(holder, textvariable=self.var, show=show)
        if field.kind in (FieldKind.FILE, FieldKind.DIR):
            widget.configure(font=self.fonts.mono)
        widget.grid(row=0, column=1, sticky="ew")
        widget.bind("<FocusOut>", lambda _e: self._commit())
        widget.bind("<Return>", lambda _e: self._commit())
        # long values (document names, paths) may not fit - show them whole
        Tooltip(widget, self._full_value_hint)
        return widget

    # --- state --------------------------------------------------------------
    def _apply_enabled_state(self) -> None:
        enabled = self.field.editable and (
            self.override_var is None or self.override_var.get()
        )
        state = "normal" if enabled else "disabled"
        if self._choice_buttons:
            for button in self._choice_buttons:
                button.configure(state=state)
        elif isinstance(self.widget, ttk.Combobox):
            self.widget.configure(state="readonly" if enabled else "disabled")
        elif isinstance(self.widget, tk.Text):
            self.widget.configure(state=state,
                                  background=theme.SURFACE if enabled else theme.READONLY)
        else:
            self.widget.configure(state=state)

    def _on_override_toggled(self) -> None:
        self._apply_enabled_state()
        self._commit()

    def _full_value_hint(self) -> str:
        """The value as tooltip text, but only when the entry cuts it off."""
        # the entry knows best which part of its text it shows
        first, last = self.widget.xview()
        if first <= 0.0 and last >= 1.0:
            return ""
        return self.var.get()

    def _commit(self) -> None:
        if callable(self.on_commit):
            self.on_commit()

    def _browse(self) -> None:
        current = self.raw_value()
        start = PROJECT_ROOT
        if current:
            candidate = Path(current)
            if not candidate.is_absolute():
                candidate = PROJECT_ROOT / candidate
            start = candidate.parent if candidate.parent.exists() else PROJECT_ROOT

        if self.field.kind is FieldKind.DIR:
            chosen = filedialog.askdirectory(initialdir=str(start))
        else:
            chosen = filedialog.askopenfilename(initialdir=str(start))
        if not chosen:
            return

        path = Path(chosen)
        try:  # keep the project relative style of the configuration files
            path = path.relative_to(PROJECT_ROOT)
        except ValueError:
            pass
        self.set_raw_value(str(path).replace("\\", "/"))
        if self.override_var is not None:
            self.override_var.set(True)
            self._apply_enabled_state()
        self._commit()

    # --- values -------------------------------------------------------------
    def raw_value(self) -> Any:
        if self.field.kind is FieldKind.MULTILINE:
            return self.widget.get("1.0", "end-1c")
        return self.var.get()

    def set_raw_value(self, value: Any) -> None:
        if self.field.kind is FieldKind.MULTILINE:
            state = self.widget.cget("state")
            self.widget.configure(state="normal")
            self.widget.delete("1.0", "end")
            self.widget.insert("1.0", "" if value is None else str(value))
            self.widget.configure(state=state)
            return
        self.var.set(self.field.to_display(value))

    def is_overridden(self, file_value: Any) -> bool:
        if self.override_var is not None:
            return bool(self.override_var.get())
        if not self.field.editable:
            return False
        raw = self.raw_value()
        if file_value is None and raw in ("", None):
            return False
        return self.field.to_python(raw) != file_value

    def set_override_flag(self, flag: bool) -> None:
        if self.override_var is not None:
            self.override_var.set(flag)
            self._apply_enabled_state()

    def mark(self, overridden: bool) -> None:
        """Show whether the value differs from the configuration file."""
        self.edge.configure(background=theme.WARN if overridden else theme.SURFACE)
        if overridden:
            self.edited_tag.pack(side="left", padx=(6, 0))
        else:
            self.edited_tag.pack_forget()
        # a computed value is reset by switching Override off
        if overridden and self.override_var is None:
            self.reset_button.grid(row=0, column=self._reset_column, padx=(4, 0))
        else:
            self.reset_button.grid_remove()


class ConfigPanel(ttk.Frame):
    """Shows and collects the configuration of the selected module."""

    def __init__(self, master, store, fonts: theme.Fonts, on_change=None, **kwargs):
        super().__init__(master, **kwargs)
        self.store = store
        self.fonts = fonts
        self.on_change = on_change

        self._toc = tk.Frame(self, background=theme.GROUND, width=cfg.TOC_WIDTH)
        self._toc.pack_propagate(False)
        self._scroller = ScrollableFrame(self, on_scroll=self._sync_toc)
        self._scroller.pack(side="right", fill="both", expand=True)

        self._module = None
        self._sources: List[ConfigSource] = []
        self._editors: List[Tuple[ConfigSource, _FieldEditor]] = []
        self._file_values: Dict[str, Dict[str, Any]] = {}
        self._sections: List[Tuple[tk.Widget, tk.Label]] = []   # card, toc entry
        self._refreshing = False

    # --- building -----------------------------------------------------------
    def show_module(self, module) -> None:
        self._module = module
        self._scroller.clear()
        for child in self._toc.winfo_children():
            child.destroy()
        self._editors = []
        self._sources = []
        self._file_values = {}
        self._sections = []

        if module is None:
            return

        self._sources = module.config_sources()
        if not self._sources:
            self._toc.pack_forget()
            ttk.Label(self._scroller.inner,
                      text="This module has no configurable value.",
                      foreground=theme.TEXT_MUTED).pack(anchor="w", padx=theme.SPACE_XL,
                                                        pady=theme.SPACE_XL)
            return

        tk.Label(self._toc, text="SECTIONS", background=theme.GROUND,
                 foreground=theme.TEXT_MUTED, font=self.fonts.small_bold,
                 anchor="w").pack(fill="x", padx=10, pady=(0, 6))
        for source in self._sources:
            self._build_source(source)
        # one section needs no table of contents
        if len(self._sections) > 1:
            self._toc.pack(side="left", fill="y", padx=(theme.SPACE_L, 0),
                           pady=(theme.SPACE_L, 0), before=self._scroller)
        else:
            self._toc.pack_forget()

        self._scroller.scroll_to_top()
        self.refresh_values()
        self.after_idle(self._sync_toc)

    def _build_source(self, source: ConfigSource) -> None:
        inner = self._scroller.inner
        try:
            self._file_values[source.id] = source.evaluate({}, side_effects=False)
        except Exception as exc:
            self._file_values[source.id] = {}
            tk.Label(inner, text=f"{source.title}: could not be read ({exc})",
                     background=theme.GROUND, foreground="#B42318", font=self.fonts.small,
                     anchor="w", justify="left").pack(fill="x", padx=theme.SPACE_L,
                                                      pady=(theme.SPACE_L, 0))

        # the file the values come from, with the reset of all its values
        header = tk.Frame(inner, background=theme.GROUND)
        header.pack(fill="x", padx=theme.SPACE_L, pady=(theme.SPACE_L, theme.SPACE_S))
        ttk.Button(header, text="Reset to file defaults", style="Ground.Link.TButton",
                   command=lambda s=source: self.reset_source(s)).pack(side="right", anchor="n")
        tk.Label(header, text=source.title, background=theme.GROUND, foreground=theme.TEXT,
                 font=self.fonts.body_bold, anchor="w").pack(fill="x")
        if source.description:
            description = tk.Label(header, text=source.description, background=theme.GROUND,
                                   foreground=theme.TEXT_MUTED, font=self.fonts.small,
                                   anchor="w", justify="left")
            description.pack(fill="x")
            header.bind("<Configure>", lambda e, d=description: d.configure(
                wraplength=max(300, e.width - 200)))

        sections: Dict[str, List[ConfigField]] = {}
        for field in source.fields():
            sections.setdefault(field.section or "Settings", []).append(field)

        for section_name, fields in sections.items():
            card = theme.card(inner)
            card.pack(fill="x", padx=theme.SPACE_L, pady=(0, theme.SPACE_M))
            tk.Label(card, text=section_name, background=theme.SURFACE,
                     foreground=theme.TEXT, font=self.fonts.heading, anchor="w").pack(
                fill="x", padx=theme.SPACE_L + 4, pady=(theme.SPACE_M, theme.SPACE_XS))
            grid = tk.Frame(card, background=theme.SURFACE)
            grid.pack(fill="x", padx=(theme.SPACE_L + 4, theme.SPACE_L),
                      pady=(0, theme.SPACE_S))
            # fixed label width keeps all cards aligned, the values take the rest
            grid.columnconfigure(0, weight=0, minsize=cfg.LABEL_WIDTH)
            grid.columnconfigure(1, weight=1, minsize=cfg.FIELD_WIDTH)
            for row, field in enumerate(fields):
                editor = _FieldEditor(grid, field, row, self.fonts,
                                      self._on_editor_commit,
                                      lambda e, s=source: self.reset_field(s, e))
                self._editors.append((source, editor))
            self._add_toc_entry(section_name, card)

    def _add_toc_entry(self, name: str, card: tk.Widget) -> None:
        entry = tk.Label(self._toc, text=name, background=theme.GROUND,
                         foreground=theme.TEXT, font=self.fonts.body, anchor="w",
                         padx=10, pady=5, cursor="hand2")
        entry.pack(fill="x", pady=1)
        entry.bind("<Button-1>", lambda _e: self._scroller.scroll_to(card))
        self._sections.append((card, entry))

    def _sync_toc(self) -> None:
        """Highlight the section at the top of the visible part of the form."""
        if not self._sections:
            return
        top = self._scroller.visible_top() + 24
        inner_y = self._scroller.inner.winfo_rooty()
        current = self._sections[0][0]
        for card, _entry in self._sections:
            if card.winfo_rooty() - inner_y <= top:
                current = card
        for card, entry in self._sections:
            chosen = card is current
            entry.configure(background=theme.ACCENT_SOFT if chosen else theme.GROUND,
                            font=self.fonts.body_bold if chosen else self.fonts.body)

    # --- values -------------------------------------------------------------
    def refresh_values(self) -> None:
        """Fill the widgets from the stored overrides plus the file defaults."""
        self._refreshing = True
        try:
            for source in self._sources:
                overrides = self.store.overrides(source.id)
                effective = self._evaluate(source, overrides)
                for src, editor in self._editors:
                    if src is not source:
                        continue
                    name = editor.field.name
                    editor.set_override_flag(name in overrides)
                    if name in overrides:
                        editor.set_raw_value(overrides[name])
                    else:
                        editor.set_raw_value(effective.get(name,
                                                           editor.field.default))
                    editor.mark(name in overrides)
        finally:
            self._refreshing = False

    def _on_editor_commit(self) -> None:
        if self._refreshing:
            return
        self.update_derived()
        if callable(self.on_change):
            self.on_change()

    def update_derived(self) -> None:
        """Recompute the derived entries from what stands in the form now."""
        values, _errors = self.collect(validate=False)
        self._refreshing = True
        try:
            for source in self._sources:
                effective = self._evaluate(source, values.get(source.id, {}))
                for src, editor in self._editors:
                    if src is not source:
                        continue
                    name = editor.field.name
                    overridden = name in values.get(source.id, {})
                    editor.mark(overridden)
                    if editor.field.derived and not overridden:
                        editor.set_raw_value(effective.get(name, ""))
        finally:
            self._refreshing = False

    def collect(self, validate: bool = True) -> Tuple[Dict[str, Dict[str, Any]],
                                                      List[str]]:
        """Return ``{source_id: {name: value}}`` plus the validation errors."""
        values: Dict[str, Dict[str, Any]] = {}
        errors: List[str] = []
        for source, editor in self._editors:
            field = editor.field
            raw = editor.raw_value()
            if validate:
                message = field.validate(raw)
                if message:
                    errors.append(f"{source.title} - {message}")
                    continue
            file_value = self._file_values.get(source.id, {}).get(field.name)
            if not editor.is_overridden(file_value):
                continue
            try:
                values.setdefault(source.id, {})[field.name] = field.to_python(raw)
            except (TypeError, ValueError) as exc:
                errors.append(f"{source.title} - {field.label}: {exc}")
        return values, errors

    def volatile_keys(self, source_id: str) -> List[str]:
        """Names of the fields that must not reach the settings file."""
        return [
            editor.field.name
            for source, editor in self._editors
            if source.id == source_id and not editor.field.persist
        ]

    def store_values(self) -> List[str]:
        """Push the form into the settings store, return the errors found."""
        values, errors = self.collect(validate=True)
        if errors:
            return errors
        for source in self._sources:
            self.store.set_overrides(source.id, values.get(source.id, {}),
                                     self.volatile_keys(source.id))
        return []

    def reset_source(self, source: ConfigSource) -> None:
        self.store.clear_source(source.id)
        self.refresh_values()
        if callable(self.on_change):
            self.on_change()

    def reset_field(self, source: ConfigSource, editor: _FieldEditor) -> None:
        """Put one plain value back to what stands in the configuration file."""
        file_value = self._file_values.get(source.id, {}).get(editor.field.name,
                                                              editor.field.default)
        editor.set_raw_value(file_value)
        self._on_editor_commit()

    # --- helpers ------------------------------------------------------------
    @staticmethod
    def _evaluate(source: ConfigSource, overrides) -> Dict[str, Any]:
        """Preview of the effective values - never touches the disk."""
        try:
            return source.evaluate(overrides, side_effects=False)
        except Exception:
            return {}
