# -*- coding: utf-8 -*-
"""``Preprocessor/IAREWPreprocessor.py`` - the release notes of IAR EW.

Selected with ``TOOL_PREPROCESSOR = "IAR_EmbeddedWorkbench"``.  It needs no AI:
the defects are read with a regular expression and written into a copy of the
CSV template.

Two things this file makes visible, see ``tests/README.md``:

* the defect id pattern is anchored at the start of the line (``^IDE-\\d+``)
  while the code around it cuts the id out of ``[...]`` brackets - only lines
  like ``IDE-1] text`` are read, ``[IDE-1] text`` is skipped;
* the author and the status are filled in for every defect but the last one,
  which reaches the CSV with both columns empty.
"""
from __future__ import annotations

import unittest

from tests.support import TempDirTestCase, captured_stdout, config_values

import config
from Preprocessor.IAREWPreprocessor import (
    IAREWPreprocessor,
    defect_id_regex,
    parse_txt_to_csv,
)

TEMPLATE = ("Defect ID,Defect Description,Risk Assessment,Status,Author\n"
            ",,,,\n")


class DefectIdRegexTests(unittest.TestCase):
    """Which lines are taken for the beginning of a defect."""

    def test_a_line_starting_with_the_id_is_read(self):
        self.assertEqual(defect_id_regex.findall("IDE-1234 some text"),
                         ["IDE-1234"])

    def test_a_bracketed_id_is_not_read(self):
        self.assertEqual(defect_id_regex.findall("[IDE-1234] some text"), [])

    def test_an_id_in_the_middle_of_a_line_is_not_read(self):
        self.assertEqual(defect_id_regex.findall("Version 9.30 IDE-1234"), [])


class ParseTxtToCsvTests(TempDirTestCase):
    """The CSV built from the release notes and the template."""

    def setUp(self):
        super().setUp()
        self.template = self.write("template.csv", TEMPLATE)
        self.out_csv = self.path("out.csv")

    def parse(self, notes: str, risk_assesment: str = "") -> str:
        return parse_txt_to_csv(txt_file=self.write("notes.txt", notes),
                                input_csv=self.template,
                                output_csv=self.out_csv,
                                risk_assesment=risk_assesment)

    def test_keeps_the_columns_of_the_template(self):
        self.parse("IDE-1] a defect\n")

        self.assertTrue(self.read("out.csv").startswith(
            "Defect ID,Defect Description,Risk Assessment,Status,Author"))

    def test_reads_the_id_and_the_description_of_a_defect(self):
        self.parse("IDE-1] the description\n")

        rows = self.read("out.csv").splitlines()
        self.assertEqual(rows[1], "IDE-1,the description,,,")

    def test_continues_the_description_over_the_following_lines(self):
        self.parse("IDE-1] first part\nsecond part\nthird part\n")

        # the piece taken from the id line is stripped, so it runs into the
        # next line without a blank - the following lines are separated
        self.assertIn("first partsecond part third part", self.read("out.csv"))

    def test_skips_the_bullet_lines_of_the_release_notes(self):
        self.parse("IDE-1] the description\n- a bullet point\n")

        self.assertNotIn("bullet", self.read("out.csv"))

    def test_fills_the_risk_assessment_column_when_one_is_given(self):
        self.parse("IDE-1] the description\n", risk_assesment="to do")

        self.assertIn("to do", self.read("out.csv"))

    def test_release_notes_without_a_defect_give_only_the_header(self):
        returned = self.parse("Nothing that looks like a defect id.\n")

        self.assertEqual(returned, "")
        self.assertEqual(len(self.read("out.csv").strip().splitlines()), 1)

    def test_returns_the_rows_as_text_for_the_risk_assessment(self):
        returned = self.parse("IDE-1] the description\n")

        self.assertEqual(returned.strip(), '"IDE-1", "the description", "", "", ""')

    def test_reads_every_defect_of_the_release_notes(self):
        self.parse("IDE-1] first defect\nIDE-2] second defect\n")

        rows = self.read("out.csv").splitlines()
        self.assertEqual(rows[1], "IDE-1,first defect,,to do,author")
        self.assertEqual(rows[2], "IDE-2,second defect,,,")

    def test_the_last_defect_gets_neither_status_nor_author(self):
        # the final row is built by a second, shorter piece of code that
        # fills in neither column
        self.parse("IDE-1] first defect\nIDE-2] last defect\n")

        last = self.read("out.csv").splitlines()[-1]
        self.assertTrue(last.endswith(",,"), last)


class PreprocessFileTests(TempDirTestCase):
    """The preprocessor around ``parse_txt_to_csv``."""

    def setUp(self):
        super().setUp()
        self.preprocessor = IAREWPreprocessor()
        self.overrides = config_values(
            config,
            CSV_TEMPLATE=self.write("template.csv", TEMPLATE),
            TEMP_OUTPUT_FILE=self.path("temp_output_risk.txt"),
        )
        self.overrides.__enter__()
        self.addCleanup(self.overrides.__exit__, None, None, None)

    def test_writes_the_defects_into_the_output_file(self):
        notes = self.write("notes.txt", "IDE-1] the description\n")

        with captured_stdout():
            returned = self.preprocessor.preprocess_file(notes)

        self.assertIn("IDE-1", returned)
        self.assertIn("IDE-1", self.read("temp_output_risk.txt"))

    def test_marks_the_defects_as_to_do(self):
        notes = self.write("notes.txt", "IDE-1] the description\n")

        with captured_stdout():
            self.preprocessor.preprocess_file(notes)

        self.assertIn("to do", self.read("temp_output_risk.txt"))

    def test_a_missing_template_stops_the_run(self):
        notes = self.write("notes.txt", "IDE-1] the description\n")

        with config_values(config, CSV_TEMPLATE=self.path("gone.csv")):
            with captured_stdout() as printed:
                with self.assertRaises(SystemExit):
                    self.preprocessor.preprocess_file(notes)

        self.assertIn("csv generation", printed.getvalue())


if __name__ == "__main__":
    unittest.main()
