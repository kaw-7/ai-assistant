# -*- coding: utf-8 -*-
"""Discovery of the runnable modules.

Every ``*.py`` file inside ``Launcher/modules`` is imported and scanned for
:class:`RunnableModule` subclasses.  A new module therefore only has to be
dropped into that folder.
"""
from __future__ import annotations

import importlib
import inspect
import pkgutil
import traceback
from typing import Dict, List, Optional

from .module_descriptor import RunnableModule

MODULES_PACKAGE = "Launcher.modules"


class ModuleRegistry:
    """Holds the discovered modules, sorted by ``order`` then ``title``."""

    def __init__(self, package_name: str = MODULES_PACKAGE):
        self.package_name = package_name
        self._modules: List[RunnableModule] = []
        self.errors: List[str] = []

    # --- discovery ----------------------------------------------------------
    def discover(self) -> "ModuleRegistry":
        self._modules = []
        self.errors = []

        package = importlib.import_module(self.package_name)
        for info in pkgutil.iter_modules(package.__path__):
            if info.name.startswith("_"):
                continue
            full_name = f"{self.package_name}.{info.name}"
            try:
                py_module = importlib.import_module(full_name)
            except Exception:
                self.errors.append(f"{full_name}:\n{traceback.format_exc()}")
                continue
            self._collect(py_module)

        self._modules.sort(key=lambda m: (m.order, m.label().lower()))
        return self

    def _collect(self, py_module) -> None:
        for _, obj in inspect.getmembers(py_module, inspect.isclass):
            if not issubclass(obj, RunnableModule) or obj is RunnableModule:
                continue
            if inspect.isabstract(obj):
                continue
            if obj.__module__ != py_module.__name__:
                continue  # imported from somewhere else, not defined here
            if not obj.id:
                self.errors.append(f"{obj.__name__} has no id - skipped")
                continue
            try:
                instance = obj()
            except Exception:
                self.errors.append(f"{obj.__name__}:\n{traceback.format_exc()}")
                continue
            if self.get(instance.id) is not None:
                self.errors.append(f"duplicated module id '{instance.id}' - skipped")
                continue
            self._modules.append(instance)

    # --- access -------------------------------------------------------------
    @property
    def modules(self) -> List[RunnableModule]:
        return list(self._modules)

    def get(self, module_id: str) -> Optional[RunnableModule]:
        for module in self._modules:
            if module.id == module_id:
                return module
        return None

    def sources_by_id(self) -> Dict[str, object]:
        """All configuration sources of all modules, keyed by source id."""
        sources: Dict[str, object] = {}
        for module in self._modules:
            for source in module.config_sources():
                sources.setdefault(source.id, source)
        return sources

    def __len__(self) -> int:
        return len(self._modules)

    def __iter__(self):
        return iter(self._modules)
