# -*- coding: utf-8 -*-
"""``UI/IssueSerializer.py`` - markup <-> issue cards, and the backup file."""
from __future__ import annotations

import unittest

from tests.support import TempDirTestCase, issue_markup, issues_markup

import UI.ui_config as uiConf
from UI.IssueSerializer import (
    createIssuesBackUp,
    issueCards_to_markup,
    markup_to_issueCards,
)


class MarkupToIssueCardsTests(unittest.TestCase):
    """Reading the AI output into the dictionaries the viewer works with."""

    def test_reads_every_field_of_an_issue(self):
        cards = markup_to_issueCards(issue_markup(
            description="Linkname conflicts",
            defect_id="BAUHAUS-30348",
            defect_description="bugfix: avoid conflicts",
            source="CORRECTION_IN_REL_NOTES",
            risk_assessment="Detectable tool behaviour - no risk.",
            status="No risk",
        ))

        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0], {
            "Description": "Linkname conflicts",
            "Defect ID": "BAUHAUS-30348",
            "Defect Description": "bugfix: avoid conflicts",
            "Source": "CORRECTION_IN_REL_NOTES",
            "Risk Assessment": "Detectable tool behaviour - no risk.",
            "Status": "No risk",
        })

    def test_reads_several_issues_in_order(self):
        cards = markup_to_issueCards(issues_markup(3))

        self.assertEqual([card["Defect ID"] for card in cards],
                         ["ID-1", "ID-2", "ID-3"])

    def test_keeps_the_line_breaks_of_a_multi_line_value(self):
        cards = markup_to_issueCards(
            "[[ Risk Assessment ]]\nfirst line\nsecond line\n"
            "[[ END ISSUE ITEM ]]\n"
        )

        self.assertEqual(cards[0]["Risk Assessment"], "first line\nsecond line")

    def test_ignores_what_the_ai_wrote_before_the_first_field(self):
        # the real reports start with a ``` fence and a sentence or two
        cards = markup_to_issueCards(
            "```\nHere are the issues:\n" + issue_markup(defect_id="ID-7")
        )

        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0]["Defect ID"], "ID-7")

    def test_an_unterminated_issue_is_dropped(self):
        # no [[ END ISSUE ITEM ]] - the card never reaches the list
        cards = markup_to_issueCards("[[ Description ]]\nhalf an issue\n")

        self.assertEqual(cards, [])

    def test_empty_text_gives_no_issue(self):
        self.assertEqual(markup_to_issueCards(""), [])
        self.assertEqual(markup_to_issueCards("   \n  \n"), [])


class IssueCardsToMarkupTests(TempDirTestCase):
    """Writing the edited cards back into the report file."""

    def test_writes_a_file_that_can_be_read_back_unchanged(self):
        original = markup_to_issueCards(issues_markup(2))
        out_file = self.path("round_trip.txt")

        issueCards_to_markup(original, out_file=out_file)

        self.assertEqual(markup_to_issueCards(self.read("round_trip.txt")),
                         original)

    def test_uses_the_configured_tokens(self):
        out_file = self.path("tokens.txt")

        issueCards_to_markup([{"Description": "text"}], out_file=out_file)

        written = self.read("tokens.txt")
        self.assertIn(f"{uiConf.TOKEN_BEG} Description {uiConf.TOKEN_END}", written)
        self.assertIn(f"{uiConf.TOKEN_BEG} {uiConf.END_ISSUE_TOKEN} "
                      f"{uiConf.TOKEN_END}", written)


class CreateIssuesBackUpTests(TempDirTestCase):
    """The copy taken before the viewer is allowed to change the report."""

    def test_copies_the_report_into_the_backup_file(self):
        text = issues_markup(2)
        issues = self.write("report.txt", text)
        backup = self.path("report.bck")

        createIssuesBackUp(issues, backup)

        self.assertEqual(self.read("report.bck"), text)

    def test_overwrites_an_older_backup(self):
        issues = self.write("report.txt", "new content")
        self.write("report.bck", "content of an earlier run")

        createIssuesBackUp(issues, self.path("report.bck"))

        self.assertEqual(self.read("report.bck"), "new content")

    def test_a_missing_report_gives_an_empty_backup(self):
        # opened in a+ mode: the report is created instead of raising
        issues = self.path("does_not_exist.txt")

        createIssuesBackUp(issues, self.path("report.bck"))

        self.assertEqual(self.read("report.bck"), "")


if __name__ == "__main__":
    unittest.main()
