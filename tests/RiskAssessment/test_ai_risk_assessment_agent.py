# -*- coding: utf-8 -*-
"""``RiskAssessment/AIRiskAssessmentAgent.py`` - assessing the issues.

The agent sends the structured issues to the AI in batches of
``MAX_COUNT_OF_ISSUES_PROCESSED_AT_ONCE_BY_AI`` and appends every answer to
the risk report.  The batching is the part worth testing - it decides which
issues are seen by the AI at all.
"""
from __future__ import annotations

import unittest
from unittest import mock

from tests.support import (
    RecordingAIProvider,
    TempDirTestCase,
    captured_stdout,
    config_values,
    issues_markup,
)

import config
from RiskAssessment.AIRiskAssessmentAgent import AIRiskAssessmentAgent

END = "[[ END ISSUE ITEM ]]"


class BatchingTests(unittest.TestCase):
    """``_get_up_to_nth`` - how many issues go into one request."""

    def setUp(self):
        self.agent = AIRiskAssessmentAgent(RecordingAIProvider())
        self.text = "".join(f"issue {i}{END}" for i in range(1, 6))

    def test_takes_exactly_n_issues(self):
        position, batch = self.agent._get_up_to_nth(self.text, END, 2, 0)

        self.assertEqual(batch.count(END), 2)
        self.assertIn("issue 1", batch)
        self.assertIn("issue 2", batch)
        self.assertNotIn("issue 3", batch)

    def test_continues_where_the_last_batch_stopped(self):
        position, _ = self.agent._get_up_to_nth(self.text, END, 2, 0)

        _, batch = self.agent._get_up_to_nth(self.text, END, 2, position)

        self.assertIn("issue 3", batch)
        self.assertIn("issue 4", batch)
        self.assertNotIn("issue 2", batch)

    def test_the_last_batch_holds_what_is_left(self):
        position, _ = self.agent._get_up_to_nth(self.text, END, 4, 0)

        position, batch = self.agent._get_up_to_nth(self.text, END, 4, position)

        self.assertEqual(position, -1)
        self.assertIn("issue 5", batch)

    def test_asking_for_more_issues_than_there_are_returns_all_of_them(self):
        position, batch = self.agent._get_up_to_nth(self.text, END, 99, 0)

        self.assertEqual(position, -1)
        self.assertEqual(batch, self.text)

    def test_nothing_is_left_behind_the_end_of_the_text(self):
        position, batch = self.agent._get_up_to_nth(self.text, END, 2,
                                                    len(self.text))

        self.assertEqual(position, -1)
        self.assertEqual(batch, "")


class CountingTests(unittest.TestCase):
    """``_get_total_occurances`` - the length of the progress bar."""

    def setUp(self):
        self.agent = AIRiskAssessmentAgent(RecordingAIProvider())

    def test_counts_the_issues_of_a_report(self):
        self.assertEqual(
            self.agent._get_total_occurances(issues_markup(7), END), 7)

    def test_text_without_an_issue_counts_zero(self):
        self.assertEqual(self.agent._get_total_occurances("no issue here", END), 0)

    def test_nothing_to_count_is_not_an_error(self):
        self.assertEqual(self.agent._get_total_occurances(None, END), 0)


class GenerateInputTests(TempDirTestCase):
    """The prompt built from the instructions, the reference and the issues."""

    def setUp(self):
        super().setUp()
        self.agent = AIRiskAssessmentAgent(RecordingAIProvider())
        self.overrides = config_values(
            config,
            RISK_INSTRUCTIONS_PATH=self.write("instructions.txt",
                                              "Assess every issue."),
            REF_PATH=self.write("reference.txt", "An earlier report."),
        )
        self.overrides.__enter__()
        self.addCleanup(self.overrides.__exit__, None, None, None)

    def test_contains_instructions_reference_and_issues(self):
        prompt = self.agent._generate_input("[[ Description ]]\nthe issue")

        self.assertIn("Assess every issue.", prompt)
        self.assertIn("An earlier report.", prompt)
        self.assertIn("the issue", prompt)

    def test_marks_where_the_input_data_starts_and_ends(self):
        prompt = self.agent._generate_input("the issues")

        self.assertIn("--- INPUT DATA STARTS HERE ---", prompt)
        self.assertIn("--- INPUT DATA ENDS HERE ---", prompt)

    def test_missing_instructions_give_no_prompt(self):
        with config_values(config,
                           RISK_INSTRUCTIONS_PATH=self.path("gone.txt")):
            with captured_stdout() as printed:
                prompt = self.agent._generate_input("the issues")

        self.assertEqual(prompt, "")
        self.assertIn("Instructions file not found", printed.getvalue())

    def test_a_missing_reference_report_gives_no_prompt(self):
        with config_values(config, REF_PATH=self.path("gone.txt")):
            with captured_stdout() as printed:
                prompt = self.agent._generate_input("the issues")

        self.assertEqual(prompt, "")
        self.assertIn("Reference file not found", printed.getvalue())


class ProcessIssuesTests(TempDirTestCase):
    """The whole assessment run against a fake AI."""

    def setUp(self):
        super().setUp()
        self.provider = RecordingAIProvider(default="[[ Status ]]\nNo risk")
        self.agent = AIRiskAssessmentAgent(self.provider)
        self.overrides = config_values(
            config,
            RISK_INSTRUCTIONS_PATH=self.write("instructions.txt", "Assess."),
            REF_PATH=self.write("reference.txt", "Reference."),
            RISK_ASSESSMENT_OUTPUT_FILE=self.path("final_risk_report.txt"),
            ISSUE_END_MARKER=END,
            MAX_COUNT_OF_ISSUES_PROCESSED_AT_ONCE_BY_AI=2,
        )
        self.overrides.__enter__()
        self.addCleanup(self.overrides.__exit__, None, None, None)
        # the agent waits a second between two requests to stay inside the
        # rate limit of the paid plan - the tests do not have to
        sleep = mock.patch("RiskAssessment.AIRiskAssessmentAgent.time.sleep")
        sleep.start()
        self.addCleanup(sleep.stop)

    def assess(self, report: str) -> None:
        with captured_stdout(quiet_stderr=True):
            self.agent.process_issues(report)

    def test_sends_the_issues_in_batches(self):
        # four issues, two per request
        self.assess(issues_markup(4).rstrip())

        self.assertEqual(self.provider.call_count, 2)

    def test_a_trailing_newline_costs_one_empty_request(self):
        # the report written by the preprocessor ends with a newline behind
        # the last end marker; the loop sees a rest and asks the AI about it
        self.assess(issues_markup(4))

        self.assertEqual(self.provider.call_count, 3)
        self.assertNotIn("Finding", self.provider.prompts[-1]
                         .split("--- INPUT DATA STARTS HERE ---")[-1])

    def test_every_issue_reaches_the_ai_once(self):
        self.assess(issues_markup(5))

        asked = "".join(self.provider.prompts)
        for index in range(1, 6):
            with self.subTest(issue=index):
                self.assertEqual(asked.count(f"Finding {index}"), 1)

    def test_writes_every_answer_into_the_risk_report(self):
        self.provider.responses = ["first answer", "second answer"]

        self.assess(issues_markup(4).rstrip())

        written = self.read("final_risk_report.txt")
        self.assertIn("first answer", written)
        self.assertIn("second answer", written)

    def test_starts_from_an_empty_report(self):
        self.write("final_risk_report.txt", "report of an earlier run")

        self.assess(issues_markup(1))

        self.assertNotIn("earlier run", self.read("final_risk_report.txt"))

    def test_a_single_batch_is_enough_for_a_short_report(self):
        self.assess(issues_markup(1).rstrip())

        self.assertEqual(self.provider.call_count, 1)


if __name__ == "__main__":
    unittest.main()
