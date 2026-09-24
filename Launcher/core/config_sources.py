# -*- coding: utf-8 -*-
"""Configuration back ends the launcher can read, preview and apply.

A configuration source wraps one place where a runnable module keeps its
settings - a python config module (``config.py``, ``UI/ui_config.py``,
``testspec_config.py``) or a dotenv file (``.polarion.env``).

Every source offers the same three operations:

* :meth:`fields`   - what can be edited and how it has to be rendered
* :meth:`evaluate` - the resulting values for a given set of user overrides
                     (used by the launcher UI to preview derived entries)
* :meth:`apply`    - install the overridden values into the running process
                     (used by the child process just before a module starts)

To support a new kind of configuration (YAML, INI, database, ...) subclass
:class:`ConfigSource` and implement those three methods.
"""
from __future__ import annotations

import ast
import builtins
import contextlib
import importlib
import io
import os
import sys
import tokenize
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from .config_fields import ConfigField, FieldKind, kind_for_value


class ConfigSource(ABC):
    """Base class of everything the configuration editor can show."""

    def __init__(self, source_id: str, title: str, description: str = ""):
        self.id = source_id
        self.title = title
        self.description = description

    @abstractmethod
    def fields(self) -> List[ConfigField]:
        """Editable entries, in the order they should be displayed."""

    @abstractmethod
    def evaluate(self, overrides: Mapping[str, Any],
                 side_effects: bool = True) -> Dict[str, Any]:
        """Values that would be seen by the module for the given overrides.

        ``side_effects=False`` asks for a pure preview - the launcher uses it
        while the user is typing, so that half finished values do not create
        folders on disk.
        """

    @abstractmethod
    def apply(self, overrides: Mapping[str, Any]) -> None:
        """Make the overridden values effective in the current process."""

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<{type(self).__name__} {self.id}>"


# ---------------------------------------------------------------------------
# python module configuration
# ---------------------------------------------------------------------------

@contextlib.contextmanager
def _no_directory_creation(enabled: bool):
    """Keep a preview evaluation from creating folders on disk.

    The configuration files of the project create their output folder while
    they are read.  That is wanted when a module really starts, but not while
    the user is still typing in the launcher.
    """
    if not enabled:
        yield
        return
    original_mkdir, original_makedirs = Path.mkdir, os.makedirs
    Path.mkdir = lambda *args, **kwargs: None
    os.makedirs = lambda *args, **kwargs: None
    try:
        yield
    finally:
        Path.mkdir, os.makedirs = original_mkdir, original_makedirs


class _OverridingNamespace(dict):
    """Namespace that replaces assignments listed in ``overrides``.

    The config modules of this project derive values from each other::

        tool_folder = "STM32Cube"
        TEMP_OUTPUT_FILE = f"output/{tool_folder}/temp_output_risk.txt"

    Executing the module source in this namespace substitutes the user value at
    the moment ``tool_folder`` is assigned, so every derived entry is
    recomputed instead of becoming stale.
    """

    def __init__(self, overrides: Mapping[str, Any]):
        super().__init__()
        self._overrides = dict(overrides)

    def __setitem__(self, key, value):
        if key in self._overrides:
            value = self._overrides[key]
        super().__setitem__(key, value)

    def apply_unassigned(self) -> None:
        """Add overrides for names the module source never assigns."""
        for key, value in self._overrides.items():
            if key not in self:
                dict.__setitem__(self, key, value)


class PyModuleConfigSource(ConfigSource):
    """A plain python module made of module level constants.

    ``field_specs`` lets a module refine the automatically discovered entries
    (nicer labels, choices, file pickers, sections).  Everything not mentioned
    there is still offered to the user in the ``section_default`` group.

    ``aliases`` lists the other names the same file is imported under.
    ``UI/ui_config.py`` for instance is read as ``UI.ui_config`` from the
    project root and as ``ui_config`` from inside the ``UI`` folder - python
    would build two unrelated module objects and only one of them would carry
    the overridden values.
    """

    def __init__(
        self,
        source_id: str,
        title: str,
        module_name: str,
        file_path,
        field_specs: Sequence[ConfigField] = (),
        description: str = "",
        ignore: Iterable[str] = (),
        section_default: str = "Other settings",
        show_undeclared: bool = True,
        aliases: Iterable[str] = (),
    ):
        super().__init__(source_id, title, description)
        self.module_name = module_name
        self.file_path = Path(file_path)
        self._specs = {f.name: f for f in field_specs}
        self._spec_order = [f.name for f in field_specs]
        self.ignore = set(ignore)
        self.section_default = section_default
        self.show_undeclared = show_undeclared
        self.aliases = tuple(aliases)
        self._parsed: Optional[Dict[str, Dict[str, Any]]] = None

    # --- source parsing -----------------------------------------------------
    def _read_source(self) -> str:
        return self.file_path.read_text(encoding="utf-8-sig")

    def _parse(self) -> Dict[str, Dict[str, Any]]:
        """Collect ``name -> {literal, value, comment, order}`` from the file."""
        if self._parsed is not None:
            return self._parsed

        info: Dict[str, Dict[str, Any]] = {}
        try:
            source = self._read_source()
        except OSError:
            self._parsed = info
            return info

        comments = self._trailing_comments(source)
        try:
            tree = ast.parse(source)
        except SyntaxError:
            self._parsed = info
            return info

        for index, node in enumerate(tree.body):
            if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                continue
            target = node.targets[0]
            if not isinstance(target, ast.Name):
                continue
            literal = isinstance(node.value, ast.Constant) and isinstance(
                node.value.value, (str, int, float, bool)
            )
            info[target.id] = {
                "literal": literal,
                "value": node.value.value if literal else None,
                "comment": comments.get(node.lineno, ""),
                "order": index,
            }
        self._parsed = info
        return info

    @staticmethod
    def _trailing_comments(source: str) -> Dict[int, str]:
        """Map line number -> trailing '#' comment text."""
        result: Dict[int, str] = {}
        try:
            for token in tokenize.generate_tokens(io.StringIO(source).readline):
                if token.type == tokenize.COMMENT:
                    text = token.string.lstrip("#").strip()
                    if text:
                        result.setdefault(token.start[0], text)
        except (tokenize.TokenError, IndentationError, SyntaxError):
            pass
        return result

    # --- ConfigSource interface --------------------------------------------
    def fields(self) -> List[ConfigField]:
        parsed = self._parse()
        fields: List[ConfigField] = []
        used = set()

        # declared fields first, in the order the module listed them
        for name in self._spec_order:
            spec = self._specs[name]
            entry = parsed.get(name, {})
            if spec.default is None and entry.get("literal"):
                spec.default = entry.get("value")
            if not spec.help:
                spec.help = entry.get("comment", "")
            if not spec.section:
                spec.section = self.section_default
            if entry:
                spec.derived = not entry.get("literal", False)
            fields.append(spec)
            used.add(name)

        if not self.show_undeclared:
            return fields

        # everything else discovered in the file
        for name, entry in sorted(parsed.items(), key=lambda kv: kv[1]["order"]):
            if name in used or name in self.ignore or name.startswith("_"):
                continue
            value = entry["value"]
            fields.append(
                ConfigField(
                    name=name,
                    kind=kind_for_value(value) if entry["literal"] else FieldKind.TEXT,
                    help=entry["comment"],
                    section=self.section_default,
                    derived=not entry["literal"],
                    default=value,
                )
            )
        return fields

    def evaluate(self, overrides: Mapping[str, Any],
                 side_effects: bool = True) -> Dict[str, Any]:
        """Execute the module source with the overrides injected.

        Falls back to a plain import plus overrides when the module cannot be
        executed in isolation.
        """
        try:
            globals_ns, local_ns = self._exec_source(overrides, side_effects)
        except Exception:
            values = self._import_values()
            values.update(overrides)
            return values
        values = {k: v for k, v in local_ns.items() if not k.startswith("__")}
        for key, value in globals_ns.items():
            values.setdefault(key, value)
        values.pop("__builtins__", None)
        return values

    def apply(self, overrides: Mapping[str, Any]) -> None:
        """Import the module and force the overridden (and derived) values."""
        module = importlib.import_module(self.module_name)
        targets = self._alias_modules(module)
        try:
            _, local_ns = self._exec_source(overrides)
        except Exception as exc:  # keep the run going with a plain override
            print(f"[launcher] could not re-evaluate {self.file_path}: {exc}")
            values = dict(overrides)
        else:
            values = {k: v for k, v in local_ns.items() if not k.startswith("__")}
        for target in targets:
            for key, value in values.items():
                setattr(target, key, value)

    def _alias_modules(self, module) -> List[Any]:
        """Every module object the configuration file is reachable through.

        Modules already imported under another name are collected by their
        ``__file__``; the names of :attr:`aliases` that are not imported yet
        are bound to the same object, so a later ``import ui_config`` returns
        the module the overrides were written into instead of re-reading the
        file.
        """
        targets = [module]
        try:
            resolved = self.file_path.resolve()
        except OSError:
            resolved = self.file_path
        for name, other in list(sys.modules.items()):
            if other is None or other is module:
                continue
            other_file = getattr(other, "__file__", None)
            if not other_file:
                continue
            try:
                same = Path(other_file).resolve() == resolved
            except OSError:
                continue
            if same:
                targets.append(other)
        for alias in self.aliases:
            if sys.modules.get(alias) is None:
                sys.modules[alias] = module
        return targets

    # --- internals ----------------------------------------------------------
    def _exec_source(self, overrides: Mapping[str, Any],
                     side_effects: bool = True):
        source = self._read_source()
        code = compile(source, str(self.file_path), "exec")
        globals_ns: Dict[str, Any] = {
            "__name__": self.module_name + "__launcher_preview",
            "__file__": str(self.file_path),
            "__builtins__": builtins,
        }
        local_ns = _OverridingNamespace(overrides)
        with _no_directory_creation(enabled=not side_effects):
            exec(code, globals_ns, local_ns)  # project owned configuration file
        local_ns.apply_unassigned()
        # functions defined inside a config file look names up in globals_ns
        globals_ns.update(local_ns)
        return globals_ns, local_ns

    def _import_values(self) -> Dict[str, Any]:
        try:
            module = importlib.import_module(self.module_name)
        except Exception:
            return {}
        return {k: v for k, v in vars(module).items() if not k.startswith("__")}


# ---------------------------------------------------------------------------
# dotenv configuration
# ---------------------------------------------------------------------------

class EnvFileConfigSource(ConfigSource):
    """A ``KEY=VALUE`` file such as ``.env`` / ``.polarion.env``.

    Applying puts the values into ``os.environ``.  ``python-dotenv`` does not
    overwrite variables that are already set, so the launcher values win over
    the file content without the file being touched.  Set ``write_back`` to
    also persist them into the file itself.
    """

    def __init__(
        self,
        source_id: str,
        title: str,
        file_path,
        field_specs: Sequence[ConfigField] = (),
        description: str = "",
        write_back: bool = False,
        section_default: str = "Environment",
    ):
        super().__init__(source_id, title, description)
        self.file_path = Path(file_path)
        self._specs = {f.name: f for f in field_specs}
        self._spec_order = [f.name for f in field_specs]
        self.write_back = write_back
        self.section_default = section_default

    def _read_file(self) -> Dict[str, str]:
        values: Dict[str, str] = {}
        if not self.file_path.exists():
            return values
        for line in self.file_path.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip().strip('"').strip("'")
        return values

    def fields(self) -> List[ConfigField]:
        file_values = self._read_file()
        fields: List[ConfigField] = []
        for name in self._spec_order:
            spec = self._specs[name]
            if spec.default is None:
                spec.default = file_values.get(name, "")
            if not spec.section:
                spec.section = self.section_default
            fields.append(spec)
        for name, value in file_values.items():
            if name in self._specs:
                continue
            fields.append(
                ConfigField(name=name, default=value, section=self.section_default)
            )
        return fields

    def evaluate(self, overrides: Mapping[str, Any],
                 side_effects: bool = True) -> Dict[str, Any]:
        values: Dict[str, Any] = dict(self._read_file())
        values.update(overrides)
        return values

    def apply(self, overrides: Mapping[str, Any]) -> None:
        values = self.evaluate(overrides)
        for key, value in values.items():
            os.environ[str(key)] = "" if value is None else str(value)
        if self.write_back:
            lines = [f"{k}={v}" for k, v in values.items()]
            self.file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
