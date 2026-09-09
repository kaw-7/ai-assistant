# -*- coding: utf-8 -*-
"""Module 2 - the issue viewer window."""
from __future__ import annotations

from pathlib import Path

from Launcher.core.module_descriptor import RunnableModule
from Launcher.core.project import PROJECT_ROOT

from ._sources import ui_config_source


def _resolve(raw_path: str) -> Path:
    """Find a file configured either from the project root or from ``UI/``.

    ``UI/ui_config.py`` was written to be started from inside the ``UI``
    folder, so its paths may look like ``../output/...``.  The launcher runs
    everything from the project root - try both.
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


class IssueViewerModule(RunnableModule):
    """Opens the tkinter viewer on an already generated risk report."""

    id = "issue_viewer"
    title = "2. Issue viewer"
    description = (
        "Shows the issues of a risk report, lets them be filtered and edited "
        "and writes the changes back into the report file. A backup is created "
        "before the window opens."
    )
    order = 20
    opens_window = True

    def config_sources(self):
        return [ui_config_source()]

    def run(self) -> None:
        import UI.ui_config as ui_conf
        from UI.App import App
        from UI.IssueSerializer import createIssuesBackUp, markup_to_issueCards

        issues_file = _resolve(ui_conf.ISSUES_FILE)
        backup_file = _resolve(ui_conf.ISSUES_BACKUP_FILE)
        print(f"Issues file : {issues_file}")
        print(f"Backup file : {backup_file}")

        if not issues_file.exists():
            raise FileNotFoundError(
                f"The issues file does not exist: {issues_file}\n"
                "Run the issue formatter first or correct 'Issues file'."
            )

        text = issues_file.read_text(encoding="utf-8")
        issues = markup_to_issueCards(text)
        if not issues:
            print("No issue item was found in the file - nothing to show.")
            return

        print(f"{len(issues)} issue(s) loaded, opening the viewer ...")
        backup_file.parent.mkdir(parents=True, exist_ok=True)
        createIssuesBackUp(str(issues_file), str(backup_file))

        app = App(issues, str(issues_file))
        app.mainloop()
        print("Viewer closed.")
