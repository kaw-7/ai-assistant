# -*- coding: utf-8 -*-
"""Location of the project on disk.

Everything the launcher touches is addressed relative to the repository root so
that the launcher behaves the same no matter from where it was started.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Launcher/core/project.py -> Launcher/core -> Launcher -> <project root>
PROJECT_ROOT = Path(__file__).resolve().parents[2]

SETTINGS_FILE = PROJECT_ROOT / "Launcher" / "launcher_settings.json"


def project_path(*parts: str) -> Path:
    """Absolute path of a file inside the project."""
    return PROJECT_ROOT.joinpath(*parts)


def ensure_project_root_on_path() -> None:
    """Make ``import config`` and friends work regardless of the caller."""
    root = str(PROJECT_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)


def use_project_root_as_cwd() -> None:
    """The existing modules use relative paths - keep the root as the cwd."""
    os.chdir(PROJECT_ROOT)
