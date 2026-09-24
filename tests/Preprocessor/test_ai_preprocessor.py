# -*- coding: utf-8 -*-
"""``Preprocessor/AIPreprocessor.py`` - release notes -> structured markup.

``AIPreprocessor.__init__`` empties ``config.TEMP_OUTPUT_FILE``, so every test
points that constant into its temporary folder *before* building one.
"""
from __future__ import annotations

import unittest

from tests.support import RecordingAIProvider, TempDirTestCase, captured_stdout, config_values

import config
from Preprocessor.AIPreprocessor import AIPreprocessor


class AIPreprocessorTestCase(TempDirTestCase):

    def setUp(self):
        super().setUp()
        self.provider = RecordingAIProvider(
            ["[[ Description ]]\nstructured\n[[ END ISSUE ITEM ]]"])
        self.instructions = self.write(
            "instructions.txt",
            "Assess $tool_name from version $vstart to version $vend.")
        self.overrides = config_values(
            config,
            INSTRUCTIONS_PATH=self.instructions,
            TEMP_OUTPUT_FILE=self.path("temp_output_risk.txt"),
            TOOL_NAME="Axivion 7.4",
            TOOL_VERSION_START="7.10.3",
            TOOL_VERSION_END="7.12.4",
        )
        self.overrides.__enter__()
        self.addCleanup(self.overrides.__exit__, None, None, None)
        with captured_stdout():
            self.preprocessor = AIPreprocessor(self.provider)


class GenerateInputTests(AIPreprocessorTestCase):
    """The prompt built from the instructions and the release notes."""

    def test_fills_the_tool_and_the_versions_into_the_instructions(self):
        notes = self.write("notes.txt", "Release notes of the tool")

        with captured_stdout():
            prompt = self.preprocessor.generate_input(notes)

        self.assertIn("Assess Axivion 7.4 from version 7.10.3 to version 7.12.4",
                      prompt)

    def test_hands_the_release_notes_over_between_markers(self):
        notes = self.write("notes.txt", "Release notes of the tool")

        with captured_stdout():
            prompt = self.preprocessor.generate_input(notes)

        self.assertIn("--- START OF RELEASE NOTES ---", prompt)
        self.assertIn("Release notes of the tool", prompt)
        self.assertIn("--- END OF RELEASE NOTES ---", prompt)

    def test_a_placeholder_without_a_value_is_left_alone(self):
        # safe_substitute: an unknown $name must not kill the run
        self.write("instructions.txt", "Assess $tool_name, see $unknown_name.")
        notes = self.write("notes.txt", "notes")

        with captured_stdout():
            prompt = self.preprocessor.generate_input(notes)

        self.assertIn("$unknown_name", prompt)

    def test_missing_instructions_give_no_prompt(self):
        with config_values(config, INSTRUCTIONS_PATH=self.path("gone.txt")):
            with captured_stdout() as printed:
                prompt = self.preprocessor.generate_input(
                    self.write("notes.txt", "notes"))

        self.assertEqual(prompt, "")
        self.assertIn("Instruction file not found", printed.getvalue())


class PreprocessFileTests(AIPreprocessorTestCase):
    """Asking the AI and keeping its answer."""

    def test_returns_what_the_ai_answered(self):
        notes = self.write("notes.txt", "Release notes")

        with captured_stdout():
            answer = self.preprocessor.preprocess_file(notes)

        self.assertEqual(answer,
                         "[[ Description ]]\nstructured\n[[ END ISSUE ITEM ]]")

    def test_saves_the_answer_for_the_risk_assessment(self):
        notes = self.write("notes.txt", "Release notes")

        with captured_stdout():
            self.preprocessor.preprocess_file(notes)

        self.assertIn("structured", self.read("temp_output_risk.txt"))

    def test_appends_the_answer_of_every_chunk(self):
        self.provider.responses = ["first answer", "second answer"]
        notes = self.write("notes.txt", "Release notes")

        with captured_stdout():
            self.preprocessor.preprocess_file(notes)
            self.preprocessor.preprocess_file(notes)

        written = self.read("temp_output_risk.txt")
        self.assertIn("first answer", written)
        self.assertIn("second answer", written)

    def test_the_output_file_starts_empty(self):
        self.write("temp_output_risk.txt", "result of an earlier run")

        with captured_stdout():
            AIPreprocessor(self.provider)

        self.assertEqual(self.read("temp_output_risk.txt"), "")

    def test_a_missing_release_notes_file_stops_the_run(self):
        with captured_stdout() as printed:
            with self.assertRaises(SystemExit) as exit_code:
                self.preprocessor.preprocess_file(self.path("not_there.txt"))

        self.assertEqual(exit_code.exception.code, 1)
        self.assertIn("not found", printed.getvalue())

    def test_the_ai_is_not_called_when_the_prompt_is_empty(self):
        notes = self.write("notes.txt", "Release notes")

        with config_values(config, INSTRUCTIONS_PATH=self.path("gone.txt")):
            with captured_stdout():
                answer = self.preprocessor.preprocess_file(notes)

        self.assertIsNone(answer)
        self.assertEqual(self.provider.call_count, 0)


if __name__ == "__main__":
    unittest.main()
