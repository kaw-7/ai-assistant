# -*- coding: utf-8 -*-
"""Persistence of the values entered in the launcher.

The original configuration files are never rewritten - the launcher only keeps
the *differences* the user typed and injects them before a module starts.  That
way ``config.py`` stays the readable default and the launcher stays additive.

The overrides are keyed by configuration source id, not by module id, so two
modules sharing ``config.py`` really see the same values.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from .project import SETTINGS_FILE

SETTINGS_VERSION = 1


class SettingsStore:
    """Reads / writes ``Launcher/launcher_settings.json``."""

    def __init__(self, path: Path = SETTINGS_FILE):
        self.path = Path(path)
        self._sources: Dict[str, Dict[str, Any]] = {}
        self._volatile: Dict[str, Dict[str, Any]] = {}
        self._ui: Dict[str, Any] = {}
        self.load()

    # --- io -----------------------------------------------------------------
    def load(self) -> None:
        self._sources = {}
        self._ui = {}
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        self._sources = dict(data.get("sources", {}))
        self._ui = dict(data.get("ui", {}))

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": SETTINGS_VERSION,
            "ui": self._ui,
            "sources": self._sources,
        }
        self.path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )

    # --- overrides ----------------------------------------------------------
    def overrides(self, source_id: str) -> Dict[str, Any]:
        """Stored plus in memory only values of one configuration source."""
        values = dict(self._sources.get(source_id, {}))
        values.update(self._volatile.get(source_id, {}))
        return values

    def set_overrides(
        self,
        source_id: str,
        values: Mapping[str, Any],
        volatile_keys: Iterable[str] = (),
    ) -> None:
        """Replace the overrides of one source.

        ``volatile_keys`` (fields marked ``persist=False``, typically
        passwords) are kept for the running session only and never written to
        the settings file.
        """
        volatile_keys = set(volatile_keys)
        stored, volatile = {}, {}
        for key, value in values.items():
            if value is None:
                continue
            (volatile if key in volatile_keys else stored)[key] = value

        if stored:
            self._sources[source_id] = stored
        else:
            self._sources.pop(source_id, None)
        if volatile:
            self._volatile[source_id] = volatile
        else:
            self._volatile.pop(source_id, None)

    def clear_source(self, source_id: str) -> None:
        self._sources.pop(source_id, None)
        self._volatile.pop(source_id, None)

    def as_dict(self) -> Dict[str, Dict[str, Any]]:
        """Full override map, as handed over to the child process."""
        merged: Dict[str, Dict[str, Any]] = {
            k: dict(v) for k, v in self._sources.items()
        }
        for source_id, values in self._volatile.items():
            merged.setdefault(source_id, {}).update(values)
        return merged

    # --- ui state -----------------------------------------------------------
    def ui_value(self, key: str, default: Any = None) -> Any:
        return self._ui.get(key, default)

    def set_ui_value(self, key: str, value: Any) -> None:
        self._ui[key] = value
