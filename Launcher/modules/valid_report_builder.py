# -*- coding: utf-8 -*-
"""Module 3 - validation report document and issue import into Polarion."""
from __future__ import annotations

from pathlib import Path

from Launcher.core.module_descriptor import RunnableModule
from Launcher.core.project import PROJECT_ROOT

from ._sources import polarion_env_source, valid_report_config_source


class ValidReportBuilderModule(RunnableModule):
    """Runs ``PolarionAssistant/valid_report_main.py``."""

    id = "valid_report_builder"
    title = "3. Issue import with possible document creation."
    description = (
        "Copies the validation report template into a stand alone document "
        "for the validated tool, then parses the risk report and creates one "
        "Polarion work item per issue under the configured heading of the "
        "target document. The document step can be switched off in "
        "valid_report_config.py."
    )
    order = 30
    # valid_report_main.py imports 'ValidReport.*' and 'Core.*'
    extra_sys_path = ("PolarionAssistant",)
    entry_script = "PolarionAssistant/valid_report_main.py"

    def config_sources(self):
        return [valid_report_config_source(), polarion_env_source()]

    def banner(self) -> None:
        import PolarionAssistant.ValidReport.valid_report_config as conf

        print(f"Project        : {conf.PROJECT_ID}")
        print(f"Document       : {conf.DOC_NAME}")

        if conf.BUILD_VALID_REPORT.lower() == "y":
            print(f"Template       : {conf.VALID_REPORT_TEMPLATE}")
            print(f"Document title : {conf.TARGET_TITLE}")

        # the issue import always runs
        issue_file = Path(conf.ISSUE_INPUT_FILE)
        if not issue_file.is_absolute():
            issue_file = PROJECT_ROOT / issue_file
        if not issue_file.exists():
            raise FileNotFoundError(
                f"The issue file does not exist: {issue_file}\n"
                "Run the issue formatter first or correct 'Issues to import'."
            )

        print(f"Heading        : {conf.DOC_INPUT_HEADING}")
        print(f"Issues         : {issue_file}")
