# -*- coding: utf-8 -*-
"""Contract every runnable module has to fulfil.

Adding a new module to the launcher means dropping one file into
``Launcher/modules/`` that contains a :class:`RunnableModule` subclass::

    class MyModule(RunnableModule):
        id = "my_module"
        title = "My module"
        description = "What it does."
        order = 40
        entry_script = "my_package/my_main.py"

        def config_sources(self):
            return [PyModuleConfigSource("my_conf", "My settings",
                                         "my_package.my_config",
                                         project_path("my_package", "my_config.py"))]

The registry picks it up automatically - no registration list to maintain.

A descriptor does **not** contain a copy of the module code.  It points at the
file that already holds the ``if __name__ == "__main__":`` block and that file
is executed as ``__main__`` by :meth:`RunnableModule.run`, so changing a main
never means changing the launcher.

Everything happens in a separate python process (see ``Launcher.child_main``)
after the configuration overrides have been applied, so a module may freely
print, block, open its own Tk window or call ``sys.exit``.
"""
from __future__ import annotations

import runpy
import sys
from abc import ABC
from typing import List, Sequence

from .config_sources import ConfigSource
from .project import PROJECT_ROOT


class RunnableModule(ABC):
    """One entry of the launcher module list."""

    #: stable identifier, also used as key in the settings file
    id: str = ""
    #: text shown in the module list
    title: str = ""
    #: one or two sentences shown above the configuration editor
    description: str = ""
    #: sort order inside the module list (lower comes first)
    order: int = 100
    #: extra directories (relative to the project root) added to sys.path
    extra_sys_path: Sequence[str] = ()
    #: True when the module opens its own window - only affects the hint text
    opens_window: bool = False

    #: file holding the ``__main__`` block of the module, relative to the
    #: project root - ``"main.py"``, ``"PolarionAssistant/test_spec_main.py"``
    entry_script: str = ""
    #: alternative to ``entry_script``: an importable name run as ``__main__``
    entry_module: str = ""

    def config_sources(self) -> List[ConfigSource]:
        """Configuration back ends this module reads.

        Two modules may return the same source id - the settings are then
        genuinely shared.  Modules that own their configuration file return
        their own id and stay independent.
        """
        return []

    def banner(self) -> None:
        """Print what the module is about to work on.

        Called just before the entry point.  Meant for a handful of
        ``print`` statements reading the configuration - never for logic that
        belongs into the module itself.
        """

    def run(self) -> None:
        """Execute the real entry point of the module.

        The ``__main__`` block of :attr:`entry_script` / :attr:`entry_module`
        is executed as if the file had been started with ``python <file>``.
        Override this only for a module that has no main of its own.
        """
        self.banner()
        argv = sys.argv
        try:
            if self.entry_module:
                sys.argv = [self.entry_module]
                runpy.run_module(self.entry_module, run_name="__main__",
                                 alter_sys=True)
            elif self.entry_script:
                script = str(PROJECT_ROOT / self.entry_script)
                sys.argv = [script]
                runpy.run_path(script, run_name="__main__")
            else:
                raise NotImplementedError(
                    f"module '{self.id}' declares neither entry_script nor "
                    f"entry_module and does not override run()"
                )
        finally:
            sys.argv = argv

    # --- convenience --------------------------------------------------------
    def label(self) -> str:
        return self.title or self.id

    def entry_point(self) -> str:
        """Human readable entry point, shown by the child process."""
        return self.entry_module or self.entry_script or f"{type(self).__name__}.run()"

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<RunnableModule {self.id}>"
