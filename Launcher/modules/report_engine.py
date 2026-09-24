# -*- coding: utf-8 -*-
"""Module 1 - issue formatter and AI risk assessment."""
from __future__ import annotations

from Launcher.core.module_descriptor import RunnableModule

from ._sources import main_config_source


class ReportEngineModule(RunnableModule):
    """Runs ``main.py`` - the preprocessing pipeline and the risk assessment agent."""

    id = "report_engine"
    title = "1. Issue formatter and risk assessment"
    description = (
        "Reads the release notes of the validated tool, turns them into "
        "structured issue items and lets the AI assess the risk of every item. "
        "Set 'Proceed with the AI risk assessment' to choose whether the risk "
        "step runs after the preprocessing."
    )
    order = 10
    entry_script = "main.py"

    def config_sources(self):
        return [main_config_source()]

    def banner(self) -> None:
        import config

        print(f"Tool          : {config.TOOL_NAME} "
              f"({config.TOOL_VERSION_START} -> {config.TOOL_VERSION_END})")
        print(f"Release notes : {config.TOOL_RELEASE_NOTES}")
        print(f"Preprocessor  : {config.TOOL_PREPROCESSOR}")
        print(f"Risk report   : {config.RISK_ASSESSMENT_OUTPUT_FILE}")
