# -*- coding: utf-8 -*-
"""Module 4 - creates the test specification and moves the test cases into it.

This module exists mainly as the worked example of the extension point: it
lives in its own package, needs an extra ``sys.path`` entry and reads a
configuration file of its own - and still only had to be dropped into
``Launcher/modules`` to appear in the launcher.
"""
from __future__ import annotations

from Launcher.core.module_descriptor import RunnableModule

from ._sources import polarion_env_source, testspec_config_source


class TestSpecBuilderModule(RunnableModule):
    """Runs ``PolarionAssistant/test_spec_main.py``."""

    id = "test_spec_builder"
    title = "4. Test specification builder"
    description = (
        "Copies the test specification template into a stand alone document "
        "for the validated tool, then moves the test cases of the validation "
        "plan under the configured heading of the test specification. The "
        "document step can be switched off and a debug run only prints the "
        "documents - both in testspec_config.py."
    )
    order = 40
    # test_spec_main.py imports 'TestSpec.*' and 'Core.*'
    extra_sys_path = ("PolarionAssistant",)
    entry_script = "PolarionAssistant/test_spec_main.py"

    def config_sources(self):
        return [testspec_config_source(), polarion_env_source()]

    def banner(self) -> None:
        import TestSpec.testspec_config as ts_conf

        create = ts_conf.CREATE_TEST_SPEC.lower() == "y"
        debug = ts_conf.DEBUG.lower() == "y"

        if debug:
            print("Mode           : DEBUG - documents are only printed, "
                  "nothing is changed in Polarion")
        print(f"Project        : {ts_conf.PROJECT_ID}")

        if create:
            print(f"Template       : {ts_conf.TEST_SPEC_TEMPLATE}")
            print(f"Document title : {ts_conf.TARGET_TITLE}")

        # the test cases step always runs (moved, or printed in debug mode)
        print(f"Plan document  : {ts_conf.PLAN_DOCU}")
        print(f"Test spec doc  : {ts_conf.TEST_DOCU}")
        print(f"Heading        : {ts_conf.DOC_INPUT_HEADING}")
