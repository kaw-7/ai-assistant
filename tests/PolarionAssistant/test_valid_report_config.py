# -*- coding: utf-8 -*-
"""One configuration file per module: who reads which file.

``config.py`` used to hold the settings of the AI assistant *and* of the
Polarion import.  The validation report module (document creation and issue
import) now has ``PolarionAssistant/ValidReport/valid_report_config.py`` of its
own.  The Polarion project id and the issue markup, the same for every Polarion
document, are in ``PolarionAssistant/Core/core_config.py``.  These tests keep
the files complete and compatible - a key that goes missing here is an
``AttributeError`` in the middle of a run against the server.
"""
from __future__ import annotations

import unittest

from tests.support import PROJECT_ROOT  # noqa: F401  (puts the root on sys.path)

import config
import PolarionAssistant.Core.core_config as CoreConf
import PolarionAssistant.ValidReport.periodic_review_config as PRConf
import PolarionAssistant.ValidReport.valid_report_config as PConf

#: what the import path reads from the document configuration - PolarionIssueImporter
IMPORTER_KEYS = (
    "DOC_NAME",
    "DOC_INPUT_HEADING",
    "ISSUE_INPUT_FILE",
)

#: what PolarionIssueImporter, ValidReportBuilder, IssueParser and
#: IssueDAOFactory read from core_config.py
CORE_KEYS = (
    "PROJECT_ID",
    "ISSUE_MARKER_BEG",
    "ISSUE_MARKER_END",
    "ISSUE_END_MARKER",
)

#: everything valid_report_main.py and ValidReportBuilder read
DOC_CREATION_KEYS = (
    "BUILD_VALID_REPORT",
    "TOOL_NAME",
    "VALID_REPORT_TEMPLATE",
    "TARGET_LOCATION",
    "TARGET_NAME_ID",
    "TARGET_TITLE",
    "PLACEHOLDER",
)

#: everything main.py and the preprocessors read from config.py
AI_ASSISTANT_KEYS = (
    "TOOL_PREPROCESSOR",
    "tool_folder",
    "TOOL_RELEASE_NOTES",
    "TOOL_NAME",
    "TOOL_VERSION_START",
    "TOOL_VERSION_END",
    "MAX_COUNT_OF_ISSUES_PROCESSED_AT_ONCE_BY_AI",
    "PROCEED_WITH_AI_RISK_ASSESSMENT",
    "USE_PREPROCESS_CHUNKING",
    "INSTRUCTIONS_PATH",
    "INSTRUCTIONS_CHUNKING_PATH",
    "RISK_INSTRUCTIONS_PATH",
    "RISK_SUMMARY_INSTRUCTIONS_PATH",
    "REF_PATH",
    "REF_PATH2_OPT",
    "TEMP_REL_NOTES",
    "TEMP_CHUNK_FILE",
    "TEMP_OUTPUT_FILE",
    "CONTEXT_FILE",
    "RISK_ASSESSMENT_OUTPUT_FILE",
    "RISK_ASSESSMENT_OUTPUT_FILE_BACK_UP",
    "RISK_SUMMARY_OUTPUT_FILE",
    "CSV_TEMPLATE",
    "ISSUE_END_MARKER",
    "CHUNK_DELIMITER",
    "CHUNK_SIZE",
)


class ValidReportConfigTests(unittest.TestCase):
    """``PolarionAssistant/ValidReport/valid_report_config.py``."""

    def test_holds_every_value_the_import_reads(self):
        for key in IMPORTER_KEYS:
            with self.subTest(key=key):
                self.assertTrue(hasattr(PConf, key),
                                f"valid_report_config.py has no {key}")

    def test_holds_every_value_the_document_creation_reads(self):
        for key in DOC_CREATION_KEYS:
            with self.subTest(key=key):
                self.assertTrue(hasattr(PConf, key),
                                f"valid_report_config.py has no {key}")

    def test_the_document_step_is_yes_or_no(self):
        self.assertIn(PConf.BUILD_VALID_REPORT.lower(), ("y", "n"))

    def test_the_import_targets_the_created_document(self):
        # the document step creates TARGET_NAME_ID in TARGET_LOCATION, the
        # import opens DOC_NAME - both have to be the same document
        self.assertEqual(PConf.DOC_NAME,
                         f"wiki/{PConf.TARGET_LOCATION}/{PConf.TARGET_NAME_ID}")
        self.assertFalse(hasattr(PConf, "VALID_REPORT_DOCU"),
                         "VALID_REPORT_DOCU was merged into DOC_NAME")

    def test_the_input_file_follows_the_tool_folder(self):
        self.assertIn(PConf.tool_folder, PConf.ISSUE_INPUT_FILE)
        self.assertTrue(PConf.ISSUE_INPUT_FILE.startswith("output/"))

    def test_the_document_is_addressed_by_name_and_heading(self):
        self.assertTrue(PConf.DOC_NAME)
        self.assertTrue(PConf.DOC_INPUT_HEADING)


class PeriodicReviewConfigTests(unittest.TestCase):
    """``PolarionAssistant/ValidReport/periodic_review_config.py``."""

    def test_has_the_same_settings_as_the_validation_report(self):
        def names(module):
            return {name for name in vars(module)
                    if not name.startswith("_") and name.isupper() or name == "tool_folder"}
        self.assertEqual(names(PRConf), names(PConf))

    def test_the_import_targets_the_created_document(self):
        self.assertEqual(PRConf.DOC_NAME,
                         f"wiki/{PRConf.TARGET_LOCATION}/{PRConf.TARGET_NAME_ID}")


class CoreConfigTests(unittest.TestCase):
    """``PolarionAssistant/Core/core_config.py``."""

    def test_holds_the_project_and_the_markup(self):
        for key in CORE_KEYS:
            with self.subTest(key=key):
                self.assertTrue(str(getattr(CoreConf, key)).strip(),
                                f"core_config.py has no {key}")

    def test_the_document_configurations_do_not_repeat_them(self):
        # a copy left in a document configuration would be edited by mistake
        # and silently ignored
        for module in (PConf, PRConf):
            for key in CORE_KEYS:
                with self.subTest(module=module.__name__, key=key):
                    self.assertFalse(hasattr(module, key),
                                     f"{module.__name__} still defines {key}")


class MainConfigTests(unittest.TestCase):
    """``config.py``."""

    def test_holds_every_value_the_ai_assistant_reads(self):
        for key in AI_ASSISTANT_KEYS:
            with self.subTest(key=key):
                self.assertTrue(hasattr(config, key),
                                f"config.py has no {key}")

    def test_the_generated_files_follow_the_tool_folder(self):
        for key in ("TEMP_REL_NOTES", "TEMP_CHUNK_FILE", "TEMP_OUTPUT_FILE",
                    "CONTEXT_FILE", "RISK_ASSESSMENT_OUTPUT_FILE",
                    "RISK_SUMMARY_OUTPUT_FILE"):
            with self.subTest(key=key):
                self.assertIn(config.tool_folder, getattr(config, key))

    def test_the_polarion_settings_are_gone(self):
        # they moved to valid_report_config.py - a copy left behind here
        # would be edited by mistake and silently ignored
        for key in ("DOC_NAME", "DOC_INPUT_HEADING", "ISSUE_INPUT_FILE",
                    "ISSUE_MARKER_BEG", "ISSUE_MARKER_END"):
            with self.subTest(key=key):
                self.assertFalse(hasattr(config, key),
                                 f"config.py still defines {key}")


class BothConfigurationsTests(unittest.TestCase):
    """What the two files still have to agree on."""

    def test_the_end_marker_is_the_same_in_both_files(self):
        # the import parses what the AI assistant wrote - a different end
        # marker means the importer reads one single giant issue
        self.assertEqual(CoreConf.ISSUE_END_MARKER, config.ISSUE_END_MARKER)

    def test_the_import_reads_a_file_the_assistant_could_have_written(self):
        # both are 'output/<tool folder>/<name>.txt'; the tool folders may
        # differ on purpose (importing an older run), the shape may not
        self.assertTrue(PConf.ISSUE_INPUT_FILE.startswith("output/"))
        self.assertTrue(config.RISK_ASSESSMENT_OUTPUT_FILE.startswith("output/"))


if __name__ == "__main__":
    unittest.main()
