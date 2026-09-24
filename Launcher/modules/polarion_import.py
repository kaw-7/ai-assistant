# -*- coding: utf-8 -*-
"""Module 3 - import of the assessed issues into Polarion."""
from __future__ import annotations

from pathlib import Path

from Launcher.core.module_descriptor import RunnableModule
from Launcher.core.project import PROJECT_ROOT

from ._sources import issue_importer_config_source, polarion_env_source


class PolarionImportModule(RunnableModule):
    """Runs ``PolarionAssistant/issue_importer_main.py``."""

    id = "polarion_import"
    title = "3. Polarion import"
    description = (
        "Parses the risk report and creates one Polarion work item per issue "
        "under the configured heading of the target document. Configured by "
        "issue_importer_config.py, no longer by config.py - the risk report to "
        "read is set there as well."
    )
    order = 30
    entry_script = "PolarionAssistant/issue_importer_main.py"

    def config_sources(self):
        return [issue_importer_config_source(), polarion_env_source()]

    def banner(self) -> None:
        import PolarionAssistant.issue_importer_config as conf

        issue_file = Path(conf.ISSUE_INPUT_FILE)
        if not issue_file.is_absolute():
            issue_file = PROJECT_ROOT / issue_file
        if not issue_file.exists():
            raise FileNotFoundError(
                f"The issue file does not exist: {issue_file}\n"
                "Run the issue formatter first or correct 'Issues to import'."
            )

        print(f"Project  : {conf.PROJECT_ID}")
        print(f"Document : {conf.DOC_NAME}")
        print(f"Heading  : {conf.DOC_INPUT_HEADING}")
        print(f"Issues   : {issue_file}")
