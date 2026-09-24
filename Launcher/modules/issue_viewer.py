# -*- coding: utf-8 -*-
"""Module 2 - the issue viewer window."""
from __future__ import annotations

from pathlib import Path

from Launcher.core.module_descriptor import RunnableModule
from Launcher.core.project import PROJECT_ROOT

from ._sources import ui_config_source


class IssueViewerModule(RunnableModule):
    """Runs ``UI/main.py`` - the tkinter viewer of a generated risk report."""

    id = "issue_viewer"
    title = "2. Issue viewer"
    description = (
        "Shows the issues of a risk report, lets them be filtered and edited "
        "and writes the changes back into the report file. A backup is created "
        "before the window opens."
    )
    order = 20
    opens_window = True
    # UI/main.py imports 'App', 'IssueSerializer' and 'ui_config' as top level
    # modules - it is normally started from inside the UI folder
    extra_sys_path = ("UI",)
    entry_script = "UI/main.py"

    def banner(self) -> None:
        import UI.ui_config as ui_conf

        issues_file = self._resolve(ui_conf.ISSUES_FILE)
        if not issues_file.exists():
            raise FileNotFoundError(
                f"The issues file does not exist: {issues_file}\n"
                "Run the issue formatter first or correct 'Issues file'."
            )
        print(f"Issues file : {issues_file}")
        print(f"Backup file : {self._resolve(ui_conf.ISSUES_BACKUP_FILE)}")

    def config_sources(self):
        return [ui_config_source()]

    @staticmethod
    def _resolve(raw_path: str) -> Path:
        """Find a file configured either from the project root or from ``UI/``.

        ``UI/ui_config.py`` was written to be started from inside the ``UI``
        folder, so its paths may look like ``../output/...``.  The launcher
        runs everything from the project root - try both.
        """
        candidate = Path(raw_path)
        if candidate.is_absolute():
            return candidate
        from_root = (PROJECT_ROOT / candidate).resolve()
        if from_root.exists():
            return from_root
        from_ui = (PROJECT_ROOT / "UI" / candidate).resolve()
        if from_ui.exists():
            return from_ui
        return from_root
