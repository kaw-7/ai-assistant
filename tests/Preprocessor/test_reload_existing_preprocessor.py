# -*- coding: utf-8 -*-
"""``Preprocessor/ReloadExistingPreprocessor.py`` - skip the AI, reuse the run.

Selected with ``TOOL_PREPROCESSOR = "Reload_Existing"`` to assess the risk of
issues that were already structured by an earlier run.
"""
from __future__ import annotations

import unittest

from tests.support import RecordingAIProvider, TempDirTestCase, captured_stdout, config_values

import config
from Preprocessor.ReloadExistingPreprocessor import ReloadExistingPreprocessor


class ReloadExistingPreprocessorTests(TempDirTestCase):

    def setUp(self):
        super().setUp()
        self.provider = RecordingAIProvider()
        self.preprocessor = ReloadExistingPreprocessor(self.provider)

    def test_returns_the_issues_of_the_earlier_run(self):
        self.write("temp_output_risk.txt", "[[ Description ]]\nfrom before\n")

        with config_values(config,
                           TEMP_OUTPUT_FILE=self.path("temp_output_risk.txt")):
            issues = self.preprocessor.preprocess_file("ignored.txt")

        self.assertEqual(issues, "[[ Description ]]\nfrom before\n")

    def test_does_not_ask_the_ai(self):
        self.write("temp_output_risk.txt", "content")

        with config_values(config,
                           TEMP_OUTPUT_FILE=self.path("temp_output_risk.txt")):
            self.preprocessor.preprocess_file("ignored.txt")

        self.assertEqual(self.provider.call_count, 0)

    def test_ignores_the_release_notes_it_is_given(self):
        self.write("temp_output_risk.txt", "from before")
        self.write("release_notes.txt", "brand new notes")

        with config_values(config,
                           TEMP_OUTPUT_FILE=self.path("temp_output_risk.txt")):
            issues = self.preprocessor.preprocess_file(
                self.path("release_notes.txt"))

        self.assertEqual(issues, "from before")

    def test_stops_the_run_when_there_is_nothing_to_reload(self):
        with config_values(config, TEMP_OUTPUT_FILE=self.path("never_run.txt")):
            with captured_stdout() as printed:
                with self.assertRaises(SystemExit):
                    self.preprocessor.preprocess_file("ignored.txt")

        self.assertIn("reload of existing issues", printed.getvalue())


if __name__ == "__main__":
    unittest.main()
