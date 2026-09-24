# -*- coding: utf-8 -*-
"""``PolarionAssistant/Core/IssueDAOFactory.py`` - one work item per issue.

Creating a work item needs the Zeep types of a live Polarion session, so the
tests cover what can be checked without one: the project the factory works
in, and that a failing server call is swallowed per issue instead of tearing
down the whole import.
"""
from __future__ import annotations

import unittest

from tests.support import captured_stdout, config_values

import PolarionAssistant.issue_importer_config as PConf
from PolarionAssistant.Core.IssueDAOFactory import IssueDAOFactory
from PolarionAssistant.Model.IssueDTO import IssueDTO


class FakeClient:
    """Records the project it was asked for, then refuses to go on."""

    def __init__(self, error="the server said no"):
        self.projects = []
        self.error = error

    def getProject(self, project_id):
        self.projects.append(project_id)
        raise RuntimeError(self.error)


class FakeConnector:
    def __init__(self, client):
        self.client = client


class CreateTests(unittest.TestCase):

    def setUp(self):
        self.client = FakeClient()
        self.connector = FakeConnector(self.client)
        self.issue = IssueDTO(defect_id="ID-1", description="a finding")

    def test_works_in_the_project_of_the_importer_configuration(self):
        with captured_stdout():
            IssueDAOFactory.create(self.connector, self.issue)

        self.assertEqual(self.client.projects, [PConf.PROJECT_ID])

    def test_follows_a_changed_project_id(self):
        with config_values(PConf, PROJECT_ID="OTHER"):
            with captured_stdout():
                IssueDAOFactory.create(self.connector, self.issue)

        self.assertEqual(self.client.projects, ["OTHER"])

    def test_a_failing_issue_returns_nothing_instead_of_raising(self):
        # the importer runs eleven issues in parallel - one broken issue may
        # not stop the other ten
        with captured_stdout():
            created = IssueDAOFactory.create(self.connector, self.issue)

        self.assertIsNone(created)

    def test_the_reason_is_printed(self):
        with captured_stdout() as printed:
            IssueDAOFactory.create(self.connector, self.issue)

        self.assertIn("IssueDAOFactory", printed.getvalue())
        self.assertIn("the server said no", printed.getvalue())


if __name__ == "__main__":
    unittest.main()
