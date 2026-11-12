# -*- coding: utf-8 -*-
"""Module 3c - periodic review of SOUP (software of unknown provenance)."""
from __future__ import annotations

from ._sources import REPORT_PERIODIC_SOUP, periodic_review_soup_config_source
from .valid_report_builder import ValidReportBuilderModule


class PeriodicReviewSoupBuilderModule(ValidReportBuilderModule):
    """Runs ``PolarionAssistant/valid_report_main.py periodic_soup``.

    The same steps as module 3b, with ``periodic_review_soup_config.py``
    instead of ``periodic_review_config.py``.
    """

    id = "periodic_review_soup_builder"
    title = "3c. Issue import for a periodic review SOUP."
    summary = "Risk report → SOUP periodic review in Polarion"
    description = (
        "Periodic review for software of unknown provenance (SOUP). Copies "
        "the periodic review template into a stand alone document for the "
        "reviewed software, then parses the risk report and creates one "
        "Polarion work item per issue under the configured heading of the "
        "target document. The document step can be switched off in "
        "periodic_review_soup_config.py."
    )
    order = 37
    report = REPORT_PERIODIC_SOUP

    def report_source(self):
        return periodic_review_soup_config_source()
