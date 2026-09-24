# -*- coding: utf-8 -*-
"""``Preprocessor/AbstractPreprocessor.py`` - the shared base behaviour."""
from __future__ import annotations

import os
import unittest

from tests.support import TempDirTestCase, captured_stdout

from Preprocessor.AbstractPreprocessor import AbstractPreprocessor, PreprocessorType


class _Preprocessor(AbstractPreprocessor):
    """Smallest possible implementation of the contract."""

    def preprocess_file(self, release_notes_file_path: str) -> str:
        return ""


class PreprocessorTypeTests(unittest.TestCase):
    """``config.TOOL_PREPROCESSOR`` is turned into one of these."""

    def test_the_values_of_the_configuration_file(self):
        self.assertEqual(PreprocessorType("AI"), PreprocessorType.AI)
        self.assertEqual(PreprocessorType("IAR_EmbeddedWorkbench"),
                         PreprocessorType.IAR_EmbeddedWorkbench)
        self.assertEqual(PreprocessorType("Reload_Existing"),
                         PreprocessorType.RELOAD)

    def test_an_unknown_preprocessor_is_rejected(self):
        # main.py falls back to the AI preprocessor, but only for a value
        # that is a PreprocessorType at all
        with self.assertRaises(ValueError):
            PreprocessorType("something else")


class ContractTests(unittest.TestCase):

    def test_a_preprocessor_has_to_implement_preprocess_file(self):
        class Incomplete(AbstractPreprocessor):
            pass

        with self.assertRaises(TypeError):
            Incomplete()


class SaveOutputTests(TempDirTestCase):
    """Every preprocessor writes its result through this method."""

    def setUp(self):
        super().setUp()
        self.preprocessor = _Preprocessor()

    def test_writes_the_text_to_the_file(self):
        target = self.path("result.txt")

        self.preprocessor.save_output("the answer", target)

        self.assertEqual(self.read("result.txt"), "the answer")

    def test_creates_the_output_folder(self):
        target = self.path("output", "Axivion7.4", "result.txt")

        self.preprocessor.save_output("the answer", target)

        self.assertTrue(os.path.exists(target))

    def test_replaces_the_previous_content_by_default(self):
        target = self.path("result.txt")
        self.preprocessor.save_output("first", target)

        self.preprocessor.save_output("second", target)

        self.assertEqual(self.read("result.txt"), "second")

    def test_appends_when_asked_to(self):
        # the AI preprocessor appends the answer of every chunk
        target = self.path("result.txt")
        self.preprocessor.save_output("first", target)

        self.preprocessor.save_output("second", target, "a")

        self.assertEqual(self.read("result.txt"), "firstsecond")

    def test_keeps_the_emojis_and_umlauts_of_the_ai_answer(self):
        target = self.path("result.txt")

        self.preprocessor.save_output("✅ Größe", target)

        self.assertEqual(self.read("result.txt"), "✅ Größe")


class CheckCharactersTests(unittest.TestCase):
    """The warning about release notes that are not plain text."""

    def setUp(self):
        self.preprocessor = _Preprocessor()

    def test_says_nothing_about_ordinary_release_notes(self):
        with captured_stdout() as printed:
            self.preprocessor.check_characters("A bug was fixed.\r\n\tIndented\n")

        self.assertEqual(printed.getvalue(), "")

    def test_reports_the_position_of_a_nul_character(self):
        with captured_stdout() as printed:
            self.preprocessor.check_characters("abc\x00def")

        self.assertIn("first NUL at: 3", printed.getvalue())

    def test_reports_other_control_characters(self):
        with captured_stdout() as printed:
            self.preprocessor.check_characters("abc\x07def")

        self.assertIn("has non-printable", printed.getvalue())


if __name__ == "__main__":
    unittest.main()
