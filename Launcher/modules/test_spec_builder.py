# -*- coding: utf-8 -*-
"""Module 4 - moves the test cases of a validation plan into a test spec.

This module exists mainly as the worked example of the extension point: it
lives in its own package, needs an extra ``sys.path`` entry and reads a
configuration file of its own - and still only had to be dropped into
``Launcher/modules`` to appear in the launcher.
"""
from __future__ import annotations

from Launcher.core.module_descriptor import RunnableModule

from ._sources import polarion_env_source, testspec_config_source


class TestSpecBuilderModule(RunnableModule):
    """Runs ``TestCaseBuilder.MoveTestCases()``."""

    id = "test_spec_builder"
    title = "4. Test specification builder"
    description = (
        "Copies the test cases of the validation plan document into the test "
        "specification document of the same Polarion project."
    )
    order = 40
    # TestCaseBuilder imports 'TestSpec.*' and 'Core.*'
    extra_sys_path = ("PolarionAssistant",)

    def config_sources(self):
        return [testspec_config_source(), polarion_env_source()]

    def run(self) -> None:
        import TestSpec.testspec_config as ts_conf
        from TestSpec.TestCaseBuilder import TestCaseBuilder

        print(f"Project        : {ts_conf.PROJECT_ID}")
        print(f"Plan document  : {ts_conf.PLAN_DOCU}")
        print(f"Test spec doc  : {ts_conf.TEST_DOCU}\n")

        builder = TestCaseBuilder()
        builder.MoveTestCases()
