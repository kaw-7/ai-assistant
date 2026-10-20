# -*- coding: utf-8 -*-
"""``UI/IssueModel.py`` - status, title and search of the issue viewer."""
from __future__ import annotations

import unittest

import UI.ui_config as uiConf
from UI import IssueModel as model


def _item(**fields):
    names = {
        "description": uiConf.DESCRIPTION,
        "defect_id": uiConf.DEFECT_ID,
        "defect_description": uiConf.DEFECT_DESCRIPTION,
        "status": uiConf.STATUS,
    }
    return {names[key]: value for key, value in fields.items()}


class StatusTests(unittest.TestCase):

    def test_reads_the_spellings_found_in_the_reports(self):
        cases = {
            "No Risk": model.NO_RISK,
            "NO RISK": model.NO_RISK,
            "No risk.": model.NO_RISK,
            "No RIsk.": model.NO_RISK,
            "NO_RISK": model.NO_RISK,
            "Risk exists": model.RISK_EXISTS,
            "RISK EXISTS": model.RISK_EXISTS,
            "Risk Exists": model.RISK_EXISTS,
            "RISK": model.RISK_EXISTS,
            "Risk": model.RISK_EXISTS,
            "NOT_EVALUATED": model.NOT_EVALUATED,
            "not evaluated": model.NOT_EVALUATED,
        }
        for text, expected in cases.items():
            with self.subTest(status=text):
                self.assertEqual(model.status_key(_item(status=text)), expected)

    def test_missing_or_unknown_status_is_not_evaluated(self):
        self.assertEqual(model.status_key({}), model.NOT_EVALUATED)
        self.assertEqual(model.status_key(_item(status="")), model.NOT_EVALUATED)
        self.assertEqual(model.status_key(_item(status="maybe")), model.NOT_EVALUATED)

    def test_set_status_writes_the_configured_spelling(self):
        item = _item(status="NO RISK")
        model.set_status(item, model.RISK_EXISTS)
        self.assertEqual(item[uiConf.STATUS], uiConf.RISK_EXISTS)
        self.assertEqual(model.status_key(item), model.RISK_EXISTS)

    def test_set_status_adds_a_missing_status(self):
        item = _item(description="x")
        model.set_status(item, model.NO_RISK)
        self.assertEqual(item[uiConf.STATUS], uiConf.NO_RISK)


class TitleAndKindTests(unittest.TestCase):

    def test_title_is_the_description(self):
        item = _item(description="Crash in importer\nsecond line",
                     defect_description="bugfix: Fixed crash")
        self.assertEqual(model.title(item), "Crash in importer\nsecond line")
        self.assertEqual(model.kind(item), "Bug fix")

    def test_marker_keeps_its_description_as_title(self):
        item = _item(description="MARKER! This is an improvement/update/upgrade/etc",
                     defect_description="new: Native Rhapsody importer")
        self.assertTrue(model.is_marker(item))
        self.assertEqual(model.title(item),
                         "MARKER! This is an improvement/update/upgrade/etc")
        self.assertEqual(model.kind(item), "New feature")

    def test_marker_without_prefix_is_an_improvement(self):
        item = _item(description="MARKER! improvement",
                     defect_description="Faster startup")
        self.assertEqual(model.title(item), "MARKER! improvement")
        self.assertEqual(model.kind(item), "Improvement")

    def test_unknown_prefix_gives_no_kind(self):
        item = _item(description="Wrong value",
                     defect_description="Phenomenon: the value is wrong")
        self.assertEqual(model.kind(item), "")

    def test_empty_issue_has_a_placeholder_title(self):
        self.assertEqual(model.title({}), "(no description)")


class IdsAndSearchTests(unittest.TestCase):

    def test_splits_several_ids(self):
        item = _item(defect_id="BAUHAUS-28810, BAUHAUS-30395")
        self.assertEqual(model.defect_ids(item), ["BAUHAUS-28810", "BAUHAUS-30395"])
        self.assertEqual(model.defect_ids({}), [])

    def test_search_looks_at_id_title_and_defect_description(self):
        item = _item(description="Crash in importer", defect_id="BAUHAUS-30321",
                     defect_description="bugfix: many workers")
        self.assertTrue(model.matches_query(item, ""))
        self.assertTrue(model.matches_query(item, "30321"))
        self.assertTrue(model.matches_query(item, "CRASH"))
        self.assertTrue(model.matches_query(item, "workers"))
        self.assertFalse(model.matches_query(item, "linker"))


if __name__ == "__main__":
    unittest.main()
