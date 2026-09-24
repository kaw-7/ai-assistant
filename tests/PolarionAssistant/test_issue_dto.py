# -*- coding: utf-8 -*-
"""``PolarionAssistant/Model`` - the issue object and its Polarion ids."""
from __future__ import annotations

import unittest

from tests.support import PROJECT_ROOT  # noqa: F401  (puts the root on sys.path)

from PolarionAssistant.Model.DAO.IssueFields import IssueSource, IssueStatus
from PolarionAssistant.Model.IssueDTO import IssueDTO, SourceDTO


class IssueFieldsTests(unittest.TestCase):
    """The ids written into Polarion - changing one breaks every import."""

    def test_status_ids(self):
        self.assertEqual(IssueStatus.RISK.value, "risk_exists")
        self.assertEqual(IssueStatus.NO_RISK.value, "no_risk")
        self.assertEqual(IssueStatus.NOT_EVALUATED.value, "not_evaluated")

    def test_source_ids(self):
        self.assertEqual(IssueSource.KNOWN_PROBLEM_BY_VENDOR.value, "knownBug")
        self.assertEqual(IssueSource.KNOWN_PROBLEM_3RD_PARTY.value, "3rdPartyBug")
        self.assertEqual(IssueSource.CORRECTION_IN_REL_NOTES.value,
                         "fixedInNewerVersion")
        self.assertEqual(IssueSource.KNOWN_PROBLEM_IN_NEWER_VERS.value,
                         "knownBugNewerVersion")
        self.assertEqual(IssueSource.OCCURED_AT_OTTOBOCK.value, "ottobock")
        self.assertEqual(IssueSource.OTHER_SOURCE.value, "otherSource")

    def test_an_entry_compares_equal_to_its_id(self):
        # IssueParser relies on this when it checks a value it just parsed
        self.assertEqual(IssueStatus.NO_RISK, "no_risk")
        self.assertIn("fixedInNewerVersion", set(IssueSource))


class IssueDTOTests(unittest.TestCase):
    """The object handed over to the Polarion work item factory."""

    def test_a_new_issue_carries_the_words_the_ai_writes(self):
        # an issue starts in the vocabulary of the report, not in the one of
        # Polarion - IssueParser translates it when the report is read
        issue = IssueDTO()

        self.assertEqual(issue.source, SourceDTO.KNOWN_PROBLEM_BY_VENDOR.value)
        self.assertEqual(issue.status, "NOT_EVALUATED")
        self.assertEqual(issue.description, "")
        self.assertIsNone(issue.defect_id)

    def test_the_fields_are_plain_strings(self):
        # IssueDAOFactory hands them to Polarion as they are, without .value
        issue = IssueDTO()

        self.assertIs(type(issue.source), str)
        self.assertIs(type(issue.status), str)

    def test_the_author_is_filled_in_by_the_importer(self):
        issue = IssueDTO(defect_id="ID-1")

        self.assertIsNone(issue.author_name)
        self.assertIsNone(issue.author_email)
        self.assertIsNone(issue.polarion_username)

    def test_printing_an_issue_shows_its_id_status_and_source(self):
        issue = IssueDTO(defect_id="BAUHAUS-1",
                         description="short one",
                         status=IssueStatus.RISK,
                         source=IssueSource.CORRECTION_IN_REL_NOTES,
                         risk_assessment="assessed")

        text = str(issue)

        self.assertIn("BAUHAUS-1", text)
        self.assertIn("RISK_EXISTS", text)
        self.assertIn("Fixed in newer version", text)  # readable source

    def test_printing_shortens_a_long_description(self):
        issue = IssueDTO(description="x" * 200, risk_assessment="y" * 200)

        text = str(issue)

        self.assertIn("x" * 100 + "...", text)
        self.assertIn("y" * 120 + "...", text)


if __name__ == "__main__":
    unittest.main()
