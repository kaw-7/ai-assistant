# -*- coding: utf-8 -*-
"""The configuration split: who reads which file.

``config.py`` used to hold the settings of the AI assistant *and* of the
Polarion import.  The import now has
``PolarionAssistant/issue_importer_config.py`` of its own.  These tests keep
the two files complete and compatible - a key that goes missing here is an
``AttributeError`` in the middle of a run against the server.
"""
from __future__ import annotations

import unittest

from tests.support import PROJECT_ROOT  # noqa: F401  (puts the root on sys.path)

import config
import PolarionAssistant.issue_importer_config as PConf

#: everything the import path reads - PolarionIssueImporter, IssueParser
#: and IssueDAOFactory
IMPORTER_KEYS = (
    "PROJECT_ID",
    "DOC_NAME",
    "DOC_INPUT_HEADING",
    "ISSUE_INPUT_FILE",
    "ISSUE_MARKER_BEG",
    "ISSUE_MARKER_END",
    "ISSUE_END_MARKER",
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


class IssueImporterConfigTests(unittest.TestCase):
    """``PolarionAssistant/issue_importer_config.py``."""

    def test_holds_every_value_the_import_reads(self):
        for key in IMPORTER_KEYS:
            with self.subTest(key=key):
                self.assertTrue(hasattr(PConf, key),
                                f"issue_importer_config.py has no {key}")

    def test_the_input_file_follows_the_tool_folder(self):
        self.assertIn(PConf.tool_folder, PConf.ISSUE_INPUT_FILE)
        self.assertTrue(PConf.ISSUE_INPUT_FILE.startswith("output/"))

    def test_the_markers_are_not_empty(self):
        for key in ("ISSUE_MARKER_BEG", "ISSUE_MARKER_END", "ISSUE_END_MARKER"):
            with self.subTest(key=key):
                self.assertTrue(str(getattr(PConf, key)).strip())

    def test_the_document_is_addressed_by_project_name_and_heading(self):
        self.assertTrue(PConf.PROJECT_ID)
        self.assertTrue(PConf.DOC_NAME)
        self.assertTrue(PConf.DOC_INPUT_HEADING)


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
        # they moved to issue_importer_config.py - a copy left behind here
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
        self.assertEqual(PConf.ISSUE_END_MARKER, config.ISSUE_END_MARKER)

    def test_the_import_reads_a_file_the_assistant_could_have_written(self):
        # both are 'output/<tool folder>/<name>.txt'; the tool folders may
        # differ on purpose (importing an older run), the shape may not
        self.assertTrue(PConf.ISSUE_INPUT_FILE.startswith("output/"))
        self.assertTrue(config.RISK_ASSESSMENT_OUTPUT_FILE.startswith("output/"))


if __name__ == "__main__":
    unittest.main()
