# -*- coding: utf-8 -*-
"""The configuration editor of the launcher.

The panel is built completely out of the :class:`ConfigField` descriptors the
selected module exposes, so a new module gets its editor for free.

Two kinds of entries are shown:

* plain values - editable straight away, stored as an override as soon as they
  differ from what stands in the configuration file;
* derived values (f-strings, references to other entries) - shown read only and
  recomputed while the values they depend on are edited.  Ticking the box in
  front of such an entry pins it to a value of its own.
"""
from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk
from typing import Any, Dict, List, Tuple

from Launcher.core.config_fields import ConfigField, FieldKind
from Launcher.core.config_sources import ConfigSource
from Launcher.core.project import PROJECT_ROOT

from . import launcher_config as cfg
from .widgets import ScrollableFrame, Tooltip


class _FieldEditor:
    """One row of the form: label, widget and the optional override tick."""

    def __init__(self, parent, field: ConfigField, row: int, on_commit):
        self.field = field
        self.on_commit = on_commit
        self.override_var: tk.BooleanVar | None = None
        self.var: tk.Variable

        self.label = ttk.Label(parent, text=field.label, width=cfg.LABEL_WIDTH,
                               anchor="w")
        self.label.grid(row=row, column=1, sticky="w", padx=cfg.PADX, pady=1)

        if field.derived:
            self.override_var = tk.BooleanVar(value=False)
            check = ttk.Checkbutton(parent, variable=self.override_var,
                                    command=self._on_override_toggled)
            check.grid(row=row, column=0, sticky="w")
            Tooltip(check, "This value is computed from the other settings. "
                           "Tick to set it by hand instead.")
        else:
            ttk.Label(parent, text="").grid(row=row, column=0)

        holder = ttk.Frame(parent)
        holder.grid(row=row, column=2, sticky="ew", padx=cfg.PADX, pady=1)
        holder.columnconfigure(0, weight=1)
        self.widget = self._build_widget(holder)

        hint = field.help
        if field.derived and not hint:
            hint = "computed from the other settings"
        if hint:
            ttk.Label(parent, text=hint, foreground=cfg.COLOR_HINT,
                      font=(cfg.FONT, cfg.FONT_SIZE - 1)).grid(
                row=row, column=3, sticky="w", padx=cfg.PADX)

        self._apply_enabled_state()

    # --- construction -------------------------------------------------------
    def _build_widget(self, holder):
        field = self.field
        if field.kind is FieldKind.BOOL:
            self.var = tk.BooleanVar(value=bool(field.default))
            widget = ttk.Checkbutton(holder, variable=self.var,
                                     command=self._commit)
            widget.grid(row=0, column=0, sticky="w")
            return widget

        self.var = tk.StringVar(value=field.to_display(field.default))

        if field.kind is FieldKind.CHOICE:
            widget = ttk.Combobox(holder, textvariable=self.var,
                                  values=list(field.choices), state="readonly")
            widget.grid(row=0, column=0, sticky="ew")
            widget.bind("<<ComboboxSelected>>", lambda _e: self._commit())
            return widget

        if field.kind is FieldKind.MULTILINE:
            widget = tk.Text(holder, height=4, wrap="word",
                             font=(cfg.MONO_FONT, cfg.MONO_FONT_SIZE))
            widget.insert("1.0", self.var.get())
            widget.grid(row=0, column=0, sticky="ew")
            widget.bind("<FocusOut>", lambda _e: self._commit())
            return widget

        show = "*" if field.secret else ""
        widget = ttk.Entry(holder, textvariable=self.var, show=show)
        widget.grid(row=0, column=0, sticky="ew")
        widget.bind("<FocusOut>", lambda _e: self._commit())
        widget.bind("<Return>", lambda _e: self._commit())

        if field.kind in (FieldKind.FILE, FieldKind.DIR):
            ttk.Button(holder, text="...", width=3,
                       command=self._browse).grid(row=0, column=1, padx=(4, 0))
        return widget

    # --- state --------------------------------------------------------------
    def _apply_enabled_state(self) -> None:
        enabled = self.field.editable and (
            self.override_var is None or self.override_var.get()
        )
        state = "normal" if enabled else "disabled"
        if isinstance(self.widget, ttk.Combobox):
            self.widget.configure(state="readonly" if enabled else "disabled")
        else:
            self.widget.configure(state=state)

    def _on_override_toggled(self) -> None:
        self._apply_enabled_state()
        self._commit()

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
        text = self.field.label + (" *" if overridden else "")
        self.label.configure(text=text)


class ConfigPanel(ttk.Frame):
    """Shows and collects the configuration of the selected module."""

    def __init__(self, master, store, on_change=None, **kwargs):
        super().__init__(master, **kwargs)
        self.store = store
        self.on_change = on_change

        self._scroller = ScrollableFrame(self)
        self._scroller.pack(fill="both", expand=True)

        self._module = None
        self._sources: List[ConfigSource] = []
        self._editors: List[Tuple[ConfigSource, _FieldEditor]] = []
        self._file_values: Dict[str, Dict[str, Any]] = {}
        self._refreshing = False

    # --- building -----------------------------------------------------------
    def show_module(self, module) -> None:
        self._module = module
        self._scroller.clear()
        self._editors = []
        self._sources = []
        self._file_values = {}

        if module is None:
            return

        self._sources = module.config_sources()
        if not self._sources:
            ttk.Label(self._scroller.inner,
                      text="This module has no configurable value.",
                      foreground=cfg.COLOR_HINT).pack(anchor="w",
                                                      padx=cfg.SECTION_PADX,
                                                      pady=cfg.SECTION_PADY)
            return

        for source in self._sources:
            self._build_source(source)

        self._scroller.scroll_to_top()
        self.refresh_values()

    def _build_source(self, source: ConfigSource) -> None:
        try:
            self._file_values[source.id] = source.evaluate({}, side_effects=False)
        except Exception as exc:
            self._file_values[source.id] = {}
            ttk.Label(self._scroller.inner,
                      text=f"{source.title}: could not be read ({exc})",
                      foreground=cfg.COLOR_CONSOLE_ERROR).pack(anchor="w")

        box = ttk.LabelFrame(self._scroller.inner, text=source.title)
        box.pack(fill="x", expand=False, padx=cfg.SECTION_PADX,
                 pady=cfg.SECTION_PADY)

        header = ttk.Frame(box)
        header.pack(fill="x")
        # the button is packed first so that it always keeps its place
        ttk.Button(header, text="Reset to file defaults",
                   command=lambda s=source: self.reset_source(s)).pack(
            side="right", padx=cfg.PADX, pady=cfg.PADY)
        if source.description:
            ttk.Label(header, text=source.description, foreground=cfg.COLOR_HINT,
                      wraplength=cfg.WRAP_LENGTH, justify="left").pack(
                side="left", padx=cfg.PADX, pady=cfg.PADY)

        sections: Dict[str, List[ConfigField]] = {}
        for field in source.fields():
            sections.setdefault(field.section or "Settings", []).append(field)

        for section_name, fields in sections.items():
            grid = ttk.LabelFrame(box, text=section_name)
            grid.pack(fill="x", expand=False, padx=cfg.PADX, pady=cfg.PADY)
            # fixed widths keep the sections aligned, the hints take the rest
            grid.columnconfigure(0, weight=0, minsize=cfg.CHECK_WIDTH)
            grid.columnconfigure(2, weight=0, minsize=cfg.FIELD_WIDTH)
            grid.columnconfigure(3, weight=1)
            for row, field in enumerate(fields):
                editor = _FieldEditor(grid, field, row, self._on_editor_commit)
                self._editors.append((source, editor))

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

    # --- helpers ------------------------------------------------------------
    @staticmethod
    def _evaluate(source: ConfigSource, overrides) -> Dict[str, Any]:
        """Preview of the effective values - never touches the disk."""
        try:
            return source.evaluate(overrides, side_effects=False)
        except Exception:
            return {}
