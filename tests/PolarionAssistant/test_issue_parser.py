# -*- coding: utf-8 -*-
"""``PolarionAssistant/Core/IssueParser.py`` - risk report -> IssueDTO."""
from __future__ import annotations

import unittest

from tests.support import (
    QuietTestCase,
    TempDirTestCase,
    captured_stdout,
    config_values,
    issue_markup,
    issues_markup,
)

import PolarionAssistant.issue_importer_config as PConf
from PolarionAssistant.Core.IssueParser import IssueParser
from PolarionAssistant.Model.DAO.IssueFields import IssueSource, IssueStatus
from PolarionAssistant.Model.IssueDTO import SourceDTO, StatusDTO


class ParseMarkdownToDtoTests(QuietTestCase):
    """The markup the AI wrote turned into the objects Polarion is fed with."""

    def test_reads_every_field_into_the_dto(self):
        issues = IssueParser.parse_markdown_to_dto(issue_markup(
            description="Linkname conflicts",
            defect_id="BAUHAUS-30348",
            defect_description="bugfix: avoid conflicts",
            risk_assessment="Detectable tool behaviour - no risk.",
            status="No risk",
        ))

        self.assertEqual(len(issues), 1)
        issue = issues[0]
        self.assertEqual(issue.description, "Linkname conflicts")
        self.assertEqual(issue.defect_id, "BAUHAUS-30348")
        self.assertEqual(issue.defect_description, "bugfix: avoid conflicts")
        self.assertEqual(issue.risk_assessment,
                         "Detectable tool behaviour - no risk.")

    def test_reads_all_issues_of_a_report(self):
        issues = IssueParser.parse_markdown_to_dto(issues_markup(4))

        self.assertEqual([i.defect_id for i in issues],
                         ["ID-1", "ID-2", "ID-3", "ID-4"])

    def test_a_multi_line_risk_assessment_stays_whole(self):
        issues = IssueParser.parse_markdown_to_dto(issue_markup(
            risk_assessment="First paragraph.\n\nSecond paragraph."))

        self.assertEqual(issues[0].risk_assessment,
                         "First paragraph.\n\nSecond paragraph.")

    def test_text_without_any_field_gives_no_issue(self):
        self.assertEqual(IssueParser.parse_markdown_to_dto(""), [])
        self.assertEqual(
            IssueParser.parse_markdown_to_dto("I could not find any issue."), [])


class FixStatusTests(QuietTestCase):
    """``[[ Status ]]`` translated from the words of the report into Polarion.

    Like the source, with one difference: the risk instructions ask the AI for
    free text ("Risk Exists" / "No risk"), so the words of :class:`StatusDTO`
    are tried first and the regular expressions catch the rest.
    """

    @staticmethod
    def _status_of(written: str) -> str:
        return IssueParser.parse_markdown_to_dto(
            issue_markup(status=written))[0].status

    def test_every_word_of_the_report_becomes_its_polarion_id(self):
        for word in StatusDTO:
            with self.subTest(status=word.value):
                self.assertEqual(self._status_of(word.value),
                                 IssueStatus[word.name].value)

    def test_a_bare_risk_is_not_downgraded(self):
        # neither 'no.?risk' nor 'risk.?exist' matches "RISK" - without the
        # words of the report an issue with a risk was filed as unassessed
        self.assertEqual(self._status_of("RISK"), "risk_exists")

    def test_no_risk_is_recognised_however_it_is_written(self):
        for written in ("No risk", "no_risk", "No Risk found", "NO-RISK"):
            with self.subTest(written=written):
                self.assertEqual(self._status_of(written), IssueStatus.NO_RISK)

    def test_an_existing_risk_is_recognised_however_it_is_written(self):
        for written in ("Risk exists", "risk_exists", "RISK EXISTS"):
            with self.subTest(written=written):
                self.assertEqual(self._status_of(written), IssueStatus.RISK)

    def test_anything_else_is_left_for_a_human(self):
        for written in ("maybe", "to do", "high"):
            with self.subTest(written=written):
                self.assertEqual(self._status_of(written),
                                 IssueStatus.NOT_EVALUATED)

    def test_a_value_that_is_already_a_polarion_id_is_kept(self):
        self.assertEqual(self._status_of(IssueStatus.NOT_EVALUATED.value),
                         "not_evaluated")

    def test_the_word_the_ai_writes_for_an_unassessed_issue(self):
        self.assertEqual(self._status_of("NOT_EVALUATED"), "not_evaluated")

    def test_the_result_is_a_plain_string(self):
        self.assertIs(type(self._status_of("No risk")), str)


class FixSourceTests(QuietTestCase):
    """``[[ Source ]]`` translated from the words of the report into Polarion.

    The AI writes the vocabulary of :class:`SourceDTO`
    (``CORRECTION_IN_REL_NOTES``), Polarion stores the ids of
    :class:`IssueSource` (``fixedInNewerVersion``).
    """

    @staticmethod
    def _source_of(written: str) -> str:
        return IssueParser.parse_markdown_to_dto(
            issue_markup(source=written))[0].source

    def test_every_word_of_the_report_becomes_its_polarion_id(self):
        for word in SourceDTO:
            with self.subTest(source=word.value):
                self.assertEqual(self._source_of(word.value),
                                 IssueSource[word.name].value)

    def test_the_correction_of_a_release_note_keeps_its_meaning(self):
        # the whole point of the two vocabularies: this used to end up as
        # 'knownBug' for every issue of a report
        self.assertEqual(self._source_of("CORRECTION_IN_REL_NOTES"),
                         "fixedInNewerVersion")

    def test_everything_else_falls_back_to_a_bug_known_by_the_vendor(self):
        self.assertEqual(self._source_of("something else"), "knownBug")

    def test_a_polarion_id_is_taken_as_it_is(self):
        # a report that went through the import once already carries the ids
        for member in IssueSource:
            with self.subTest(source=member.value):
                self.assertEqual(self._source_of(member.value), member.value)

    def test_the_result_is_a_plain_string(self):
        # IssueDAOFactory passes it to Polarion without .value
        self.assertIs(type(self._source_of("OTHER_SOURCE")), str)
        self.assertIs(type(self._source_of("something else")), str)


class PreprocessInitialStringIssuesTests(QuietTestCase):
    """Cutting the AI chatter around the markup away."""

    def test_keeps_only_what_lies_between_the_outer_markers(self):
        parser = IssueParser()
        parser.issues_as_string = (
            "```\nHere are the issues:\n"
            + issue_markup(defect_id="ID-1")
            + "\nI hope this helps.\n"
        )

        parser.preprocess_initial_string_issues()

        self.assertTrue(parser.issues_as_string.startswith(PConf.ISSUE_MARKER_BEG))
        self.assertTrue(parser.issues_as_string.endswith(PConf.ISSUE_MARKER_END))
        self.assertNotIn("I hope this helps", parser.issues_as_string)

    def test_text_without_markers_is_left_alone(self):
        parser = IssueParser()
        parser.issues_as_string = "no markup at all"

        with captured_stdout() as printed:
            parser.preprocess_initial_string_issues()
        self.assertIn("Markers not found", printed.getvalue())

        self.assertEqual(parser.issues_as_string, "no markup at all")

    def test_nothing_read_yet_is_not_an_error(self):
        parser = IssueParser()

        parser.preprocess_initial_string_issues()  # must not raise

        self.assertIsNone(parser.issues_as_string)


class ReadFileTests(TempDirTestCase):
    """The whole way from the report on disk to the parsed issues."""

    def test_reads_and_parses_a_report(self):
        report = self.write("final_risk_report.txt",
                            "```\n" + issues_markup(3) + "```\n")

        parser = IssueParser(report)
        parser.read_file()

        self.assertEqual([i.defect_id for i in parser.issues],
                         ["ID-1", "ID-2", "ID-3"])

    def test_a_missing_file_is_reported_instead_of_raising(self):
        parser = IssueParser(self.path("not_there.txt"))

        with captured_stdout() as printed:
            parser.read_file()  # the importer prints and keeps going

        self.assertIn("IssueParser", printed.getvalue())
        self.assertEqual(parser.issues, [])

    def test_without_a_file_nothing_happens(self):
        parser = IssueParser()

        parser.read_file()

        self.assertEqual(parser.issues, [])

    def test_the_end_marker_comes_from_the_importer_configuration(self):
        report = self.write("report.txt",
                            issues_markup(2, end_marker="<<STOP>>"))

        with config_values(PConf, ISSUE_END_MARKER="<<STOP>>"):
            parser = IssueParser(report)
            parser.read_file()

        self.assertEqual(len(parser.issues), 2)


if __name__ == "__main__":
    unittest.main()
