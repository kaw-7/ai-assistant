# -*- coding: utf-8 -*-
"""Start the launcher.

    python -m Launcher.main          (from the project root)
    python Launcher/main.py
"""
from __future__ import annotations

import os
import sys


def _bootstrap() -> None:
    """Work from the project root, whichever way the script was started."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if root not in sys.path:
        sys.path.insert(0, root)
    os.chdir(root)


def main() -> int:
    _bootstrap()

    from Launcher.core.registry import ModuleRegistry
    from Launcher.core.settings_store import SettingsStore
    from Launcher.ui.app import LauncherApp

    registry = ModuleRegistry().discover()
    store = SettingsStore()

    app = LauncherApp(registry=registry, store=store)
    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
