# -*- coding: utf-8 -*-
"""``PolarionAssistant/TestSpec/testspec_config.py`` - module 4.

test_spec_main.py, the builders and the debuggers read the file through
attribute access - a key that goes missing here is an ``AttributeError`` in
the middle of a run against the server.
"""
from __future__ import annotations

import unittest

from tests.support import PROJECT_ROOT  # noqa: F401  (puts the root on sys.path)

import PolarionAssistant.TestSpec.testspec_config as ts_conf

#: everything test_spec_main.py, TestSpecBuilder, TestCaseBuilder and the
#: debuggers read
TESTSPEC_KEYS = (
    "CREATE_TEST_SPEC",
    "DEBUG",
    "PROJECT_ID",
    "TOOL_NAME",
    "TARGET_LOCATION",
    "TARGET_NAME_ID",
    "TARGET_TITLE",
    "PLAN_DOCU",
    "TEST_DOCU",
    "TEST_SPEC_TEMPLATE",
    "DOC_INPUT_HEADING",
    "LINK_ROLE",
    "PLACEHOLDER",
    "PLACEHOLDER_DOCSTATUS",
    "VALI_PLAN_EXCLUDED_HEADINGS",
)


class TestSpecConfigTests(unittest.TestCase):

    def test_holds_every_value_the_module_reads(self):
        for key in TESTSPEC_KEYS:
            with self.subTest(key=key):
                self.assertTrue(hasattr(ts_conf, key),
                                f"testspec_config.py has no {key}")

    def test_the_steps_are_yes_or_no(self):
        for key in ("CREATE_TEST_SPEC", "DEBUG"):
            with self.subTest(key=key):
                self.assertIn(getattr(ts_conf, key).lower(), ("y", "n"))

    def test_the_excluded_headings_are_a_collection(self):
        # a plain string would make 'title in ...' match substrings
        self.assertNotIsInstance(ts_conf.VALI_PLAN_EXCLUDED_HEADINGS, str)


if __name__ == "__main__":
    unittest.main()
