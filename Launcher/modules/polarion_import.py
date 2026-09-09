# -*- coding: utf-8 -*-
"""Module 3 - import of the assessed issues into Polarion."""
from __future__ import annotations

from pathlib import Path

from Launcher.core.module_descriptor import RunnableModule
from Launcher.core.project import PROJECT_ROOT

from ._sources import main_config_source, polarion_env_source


class PolarionImportModule(RunnableModule):
    """Creates one Polarion work item per issue of the risk report."""

    id = "polarion_import"
    title = "3. Polarion import"
    description = (
        "Parses the risk report and creates the issues under the configured "
        "heading of the Polarion document. Shares config.py with the issue "
        "formatter - the document, the project and the input file are set there."
    )
    order = 30

    def config_sources(self):
        # the main configuration is shared with the report engine on purpose:
        # both see the same values, whichever module they were edited from
        return [main_config_source(), polarion_env_source()]

    def run(self) -> None:
        import config
        from PolarionAssistant.PolarionIssueImporter import PolarionIssueImporter

        issue_file = Path(config.ISSUE_INPUT_FILE)
        if not issue_file.is_absolute():
            issue_file = PROJECT_ROOT / issue_file
        if not issue_file.exists():
            raise FileNotFoundError(
                f"The issue file does not exist: {issue_file}\n"
                "Run the issue formatter first or correct 'Issues to import'."
            )

        print(f"Project  : {config.PROJECT_ID}")
        print(f"Document : {config.DOC_NAME}")
        print(f"Heading  : {config.DOC_INPUT_HEADING}")
        print(f"Issues   : {issue_file}\n")

        importer = PolarionIssueImporter()
        importer.ImportIssuesInPolarion()
