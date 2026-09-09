# -*- coding: utf-8 -*-
"""Contract every runnable module has to fulfil.

Adding a new module to the launcher means dropping one file into
``Launcher/modules/`` that contains a :class:`RunnableModule` subclass::

    class MyModule(RunnableModule):
        id = "my_module"
        title = "My module"
        description = "What it does."
        order = 40

        def config_sources(self):
            return [PyModuleConfigSource("my_conf", "My settings",
                                         "my_package.my_config",
                                         project_path("my_package", "my_config.py"))]

        def run(self):
            from my_package.entry import do_work
            do_work()

The registry picks it up automatically - no registration list to maintain.

``run()`` is executed in a separate python process (see
``Launcher.child_main``) after the configuration overrides have been applied,
so it can freely print, block, open its own Tk window or call ``sys.exit``.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Sequence

from .config_sources import ConfigSource


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

    def config_sources(self) -> List[ConfigSource]:
        """Configuration back ends this module reads.

        Two modules may return the same source id - the settings are then
        genuinely shared, exactly like ``config.py`` is shared today.
        """
        return []

    @abstractmethod
    def run(self) -> None:
        """Do the work.  Executed in the child process."""

    # --- convenience --------------------------------------------------------
    def label(self) -> str:
        return self.title or self.id

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<RunnableModule {self.id}>"
