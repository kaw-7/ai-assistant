# -*- coding: utf-8 -*-
"""Module 3b - periodic review document and issue import into Polarion."""
from __future__ import annotations

from ._sources import REPORT_PERIODIC, periodic_review_config_source
from .valid_report_builder import ValidReportBuilderModule


class PeriodicReviewBuilderModule(ValidReportBuilderModule):
    """Runs ``PolarionAssistant/valid_report_main.py periodic``.

    The same steps as module 3a, with ``periodic_review_config.py`` instead of
    ``valid_report_config.py``.
    """

    id = "periodic_review_builder"
    title = "3b. Issue import for a periodic review."
    summary = "Risk report → periodic review in Polarion"
    description = (
        "Copies the periodic review template into a stand alone document "
        "for the reviewed tool, then parses the risk report and creates one "
        "Polarion work item per issue under the configured heading of the "
        "target document. The document step can be switched off in "
        "periodic_review_config.py."
    )
    order = 35
    report = REPORT_PERIODIC

    def report_source(self):
        return periodic_review_config_source()
