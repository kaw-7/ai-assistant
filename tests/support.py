# -*- coding: utf-8 -*-
"""Helpers shared by the tests.

The modules of this project read their settings from module level constants of
a configuration file and write their results next to them.  A test therefore
has to do two things before it calls anything: point the configuration at a
temporary folder and hand the module a fake AI provider.  Both are prepared
here so that a test case stays about the behaviour it checks.
"""
from __future__ import annotations

import contextlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Iterable, List, Optional

# tests/support.py -> tests -> <project root>
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from AIProvider.AIProvider import AIProvider  # noqa: E402  (needs sys.path)

_MISSING = object()

#: markup tokens used by both the AI output and the Polarion import
ISSUE_FIELDS = ("Description", "Defect ID", "Defect Description",
                "Source", "Risk Assessment", "Status")


@contextlib.contextmanager
def config_values(module, **values):
    """Temporarily replace module level constants of a configuration module.

    ``config.py`` and friends are imported once and read through attribute
    access, so overriding an attribute is exactly what the launcher does
    before a module starts::

        with config_values(config, TOOL_NAME="X", CHUNK_SIZE=50):
            ...

    Constants that did not exist before are removed again afterwards.
    """
    previous = {key: getattr(module, key, _MISSING) for key in values}
    for key, value in values.items():
        setattr(module, key, value)
    try:
        yield module
    finally:
        for key, old in previous.items():
            if old is _MISSING:
                delattr(module, key)
            else:
                setattr(module, key, old)


@contextlib.contextmanager
def captured_stdout(quiet_stderr: bool = False):
    """Collect everything the module under test prints.

    ``quiet_stderr`` also swallows the standard error stream - the progress
    bars of ``tqdm`` are written there and would otherwise cover the report
    of the test run.
    """
    buffer = io.StringIO()
    original_out, original_err = sys.stdout, sys.stderr
    sys.stdout = buffer
    if quiet_stderr:
        sys.stderr = io.StringIO()
    try:
        yield buffer
    finally:
        sys.stdout = original_out
        sys.stderr = original_err


def issue_markup(description="Some finding",
                 defect_id="ID-1",
                 defect_description="Something was fixed",
                 source="CORRECTION_IN_REL_NOTES",
                 risk_assessment="Detectable behaviour - no risk.",
                 status="No risk",
                 end_marker="[[ END ISSUE ITEM ]]") -> str:
    """One issue item in the markup the AI produces.

    The defaults follow a real ``final_risk_report.txt``, including the
    ``Source`` written as the *name* of the enum entry.
    """
    return (
        f"[[ Description ]]\n{description}\n"
        f"[[ Defect ID ]]\n{defect_id}\n"
        f"[[ Defect Description ]]\n{defect_description}\n"
        f"[[ Source ]]\n{source}\n"
        f"[[ Risk Assessment ]]\n{risk_assessment}\n"
        f"[[ Status ]]\n{status}\n"
        f"{end_marker}\n"
    )


def issues_markup(count: int, **overrides) -> str:
    """``count`` issue items, numbered so they can be told apart."""
    blocks = []
    for index in range(1, count + 1):
        fields = dict(description=f"Finding {index}", defect_id=f"ID-{index}")
        fields.update(overrides)
        blocks.append(issue_markup(**fields))
    return "".join(blocks)


class RecordingAIProvider(AIProvider):
    """AI provider that answers from a list and records what it was asked.

    Every caller in this project invokes ``generate_response(user_input=...)``,
    so the fake accepts that keyword as well as a positional prompt.
    """

    def __init__(self, responses: Optional[Iterable[str]] = None,
                 default: str = "AI ANSWER"):
        self.prompts: List[str] = []
        self.responses: List[str] = list(responses or [])
        self.default = default

    def generate_response(self, user_input: str = "", **kwargs) -> str:
        prompt = user_input or kwargs.get("prompt", "")
        self.prompts.append(prompt)
        if self.responses:
            return self.responses.pop(0)
        return self.default

    @property
    def call_count(self) -> int:
        return len(self.prompts)


#: set it to see everything the modules print, debug lines included::
#:
#:     set VALIREPORT_TESTS_SHOW_OUTPUT=1        (cmd)
#:     $env:VALIREPORT_TESTS_SHOW_OUTPUT = "1"   (PowerShell)
#:
#: ``run_tests.py`` sets it from its SHOW_PRINTS switch.
SHOW_OUTPUT_VARIABLE = "VALIREPORT_TESTS_SHOW_OUTPUT"


def _show_output() -> bool:
    """Read the switch again for every test.

    An IDE keeps the modules of a project loaded between two runs, so the
    variable has to be looked at when a test starts, not when this file was
    imported - ``run_tests.py`` sets it right before it loads the tests.
    """
    return bool(os.environ.get(SHOW_OUTPUT_VARIABLE))


def _debugger_attached() -> bool:
    """True while the tests run under a debugger.

    ``pdb`` and the debuggers of the IDEs write their prompt to ``sys.stdout``
    - the very stream :class:`QuietTestCase` collects.  Capturing it would
    make a breakpoint look like a hanging test, so the capturing steps aside
    as soon as somebody is tracing.
    """
    return sys.gettrace() is not None


class QuietTestCase(unittest.TestCase):
    """Test case that keeps what the modules print out of the test report.

    The modules of this project print freely - progress messages, error
    reports and the odd debug line while something is being looked at.  All of
    it would scroll the result of the run away, so stdout is collected for the
    duration of every test and offered as ``self.printed``.

    A test that wants to *check* a message opens :func:`captured_stdout`
    around the call as usual; it nests.  While debugging, set
    ``VALIREPORT_TESTS_SHOW_OUTPUT=1`` and every print reaches the console
    again.
    """

    def setUp(self) -> None:
        super().setUp()
        if _show_output() or _debugger_attached():
            self.printed = io.StringIO()
            return
        quiet = captured_stdout()
        self.printed = quiet.__enter__()
        self.addCleanup(quiet.__exit__, None, None, None)


class TempDirTestCase(QuietTestCase):
    """Test case with a temporary folder of its own.

    Nothing a test writes may end up in ``output/`` - the folder of the real
    runs - so every path handed to a module under test comes from here.
    """

    def setUp(self) -> None:
        super().setUp()
        holder = tempfile.TemporaryDirectory(prefix="valireport_tests_")
        self.addCleanup(holder.cleanup)
        self.tmp_path = Path(holder.name)

    # --- files --------------------------------------------------------------
    def path(self, *parts: str) -> str:
        """Absolute path inside the temporary folder, as a plain string."""
        return str(self.tmp_path.joinpath(*parts))

    def write(self, name: str, text: str, encoding: str = "utf-8") -> str:
        target = self.tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding=encoding)
        return str(target)

    def read(self, name: str, encoding: str = "utf-8") -> str:
        return (self.tmp_path / name).read_text(encoding=encoding)
