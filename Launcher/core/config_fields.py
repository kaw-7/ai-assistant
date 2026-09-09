# -*- coding: utf-8 -*-
"""Descriptors for a single editable configuration value.

A :class:`ConfigField` says *how* one configuration entry has to be rendered and
how the text typed by the user is converted back into a Python value.  Config
sources either declare their fields explicitly or let them be discovered
automatically (see :mod:`Launcher.core.config_sources`).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Sequence


class FieldKind(str, Enum):
    """Widget to use for a field."""
    TEXT = "text"
    MULTILINE = "multiline"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    CHOICE = "choice"
    FILE = "file"
    DIR = "dir"


_TRUE_WORDS = {"1", "true", "yes", "y", "on"}


@dataclass
class ConfigField:
    """One editable configuration entry.

    name      - identifier inside the configuration source (module constant, env key)
    label     - text shown in front of the widget
    kind      - which widget/conversion to use
    choices   - allowed values, turns the field into a combo box
    help      - tooltip / hint line shown under the widget
    section   - group box the field is placed in
    secret    - value is masked in the UI
    derived   - value is computed from other entries; the editor shows the
                computed result and asks for an explicit tick before overriding
    editable  - False makes the entry read only
    persist   - False keeps the value out of the settings file (e.g. passwords)
    default   - value used when nothing has been stored yet
    """
    name: str
    label: str = ""
    kind: FieldKind = FieldKind.TEXT
    choices: Sequence[str] = field(default_factory=tuple)
    help: str = ""
    section: str = ""
    secret: bool = False
    derived: bool = False
    editable: bool = True
    persist: bool = True
    default: Any = None

    def __post_init__(self):
        if not self.label:
            self.label = self.name
        if self.choices and self.kind is FieldKind.TEXT:
            self.kind = FieldKind.CHOICE
        self.choices = tuple(str(c) for c in self.choices)

    # --- conversion helpers -------------------------------------------------
    def to_python(self, raw: Any) -> Any:
        """Convert the raw widget content into the value the module expects."""
        if self.kind is FieldKind.BOOL:
            if isinstance(raw, bool):
                return raw
            return str(raw).strip().lower() in _TRUE_WORDS
        if self.kind is FieldKind.INT:
            text = str(raw).strip()
            return int(text) if text else 0
        if self.kind is FieldKind.FLOAT:
            text = str(raw).strip()
            return float(text) if text else 0.0
        return "" if raw is None else str(raw)

    def to_display(self, value: Any) -> str:
        """Convert a stored value into the text shown by the widget."""
        if value is None:
            return ""
        if self.kind is FieldKind.BOOL:
            return "True" if value else "False"
        return str(value)

    def validate(self, raw: Any) -> str:
        """Return an error message, or an empty string when the value is fine."""
        if self.kind in (FieldKind.INT, FieldKind.FLOAT):
            text = str(raw).strip()
            if text:
                try:
                    int(text) if self.kind is FieldKind.INT else float(text)
                except ValueError:
                    return f"{self.label}: '{text}' is not a valid {self.kind.value}"
        if self.kind is FieldKind.CHOICE and self.choices:
            text = str(raw).strip()
            if text and text not in self.choices:
                return f"{self.label}: '{text}' is not one of {', '.join(self.choices)}"
        return ""


def kind_for_value(value: Any) -> FieldKind:
    """Guess the widget kind from a literal found in a configuration file."""
    if isinstance(value, bool):
        return FieldKind.BOOL
    if isinstance(value, int):
        return FieldKind.INT
    if isinstance(value, float):
        return FieldKind.FLOAT
    return FieldKind.TEXT
