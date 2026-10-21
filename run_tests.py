# -*- coding: utf-8 -*-
"""Start the tests from an IDE - Spyder, or any editor that runs a file.

Spyder starts the *file* that is open in the editor, not a module path, so
this is the file to open and to start with **Ctrl+F5** ("Debug file").  It
puts the project root on ``sys.path`` and makes it the working directory
first, which a test file started directly would not do.

How to use it:

1. set :data:`TARGET` below to what should run;
2. put the breakpoint into the **module under test** - for example into
   ``PolarionAssistant/Core/IssueParser.py``, not into the test;
3. Ctrl+F5.  ``Debug`` stops at the breakpoint, ``F5`` just runs the tests.

The tests collect what the modules print so that the result of a run stays
readable.  While a debugger is attached that stops by itself; without one,
set :data:`SHOW_PRINTS` to ``True`` to see every ``print`` of the module.
"""
from __future__ import annotations

import os
import sys
import time
import unittest
from pathlib import Path

# --- what to run -----------------------------------------------------------
#: "" runs every test; otherwise a module, a class or a single test:
#:
#:   "tests.PolarionAssistant.test_issue_parser"
#:   "tests.PolarionAssistant.test_issue_parser.FixSourceTests"
#:   "tests.PolarionAssistant.test_issue_parser.FixSourceTests.test_a_polarion_id_is_kept"
TARGET = ""

#: 2 lists every test by name and class, 1 prints one dot per test
VERBOSITY = 2

#: True lets the modules under test print into the console
SHOW_PRINTS = False

#: True adds the local variables of every frame to the traceback of a failure
SHOW_LOCALS = True

#: how many of the slowest tests to list at the end, 0 for none
SLOWEST = 5

#: write the whole report into this file as well, "" for the console only
REPORT_FILE = ""

PROJECT_ROOT = Path(__file__).resolve().parent


def _use_the_project_root() -> None:
    """Make this project the first thing python looks at.

    An IDE console is long lived: it keeps the modules of earlier runs and it
    carries the ``sys.path`` of everything that was started in it before.  Two
    things go wrong then - the project root sits somewhere at the back of
    ``sys.path`` behind another ``tests`` package, and the ``tests`` package of
    an earlier run is still in ``sys.modules``.  Both end as::

        ModuleNotFoundError: No module named 'tests.PolarionAssistant'

    So the root goes to the front, and everything of the test package is
    dropped - which also means the edited test files are read again.
    """
    os.chdir(PROJECT_ROOT)

    root = str(PROJECT_ROOT)
    while root in sys.path:
        sys.path.remove(root)
    sys.path.insert(0, root)

    for name in [n for n in sys.modules
                 if n == "tests" or n.startswith("tests.")]:
        del sys.modules[name]


def _check_the_right_tests_were_found() -> None:
    """Say which ``tests`` package was taken when it is not this one."""
    import tests

    found = Path(getattr(tests, "__file__", "") or
                 next(iter(getattr(tests, "__path__", [""])), ""))
    if PROJECT_ROOT not in found.parents:
        raise ImportError(
            f"python found another 'tests' package: {found}\n"
            f"expected the one in {PROJECT_ROOT}.\n"
            "Restart the console of the IDE and start run_tests.py again."
        )


class DetailedResult(unittest.TextTestResult):
    """Test result that says a bit more than ``ok`` per line.

    It groups the tests under the class they belong to, times every one of
    them and ends with a summary, the slowest tests and - for a test that did
    not pass - what the module under test printed while it ran.
    """

    def __init__(self, stream, descriptions, verbosity, **kwargs):
        # the base class prints the dots itself, this one does the printing
        super().__init__(stream, descriptions, 0, **kwargs)
        self.detailed = verbosity >= 2
        self.durations_of: list[tuple[str, float]] = []
        self.output_of: dict[str, str] = {}
        self._started_at = 0.0
        self._current_class = None
        self._run_started_at = time.perf_counter()

    # --- the live listing ---------------------------------------------------
    def startTest(self, test):
        self._started_at = time.perf_counter()
        if self.detailed:
            class_name = f"{type(test).__module__}.{type(test).__name__}"
            if class_name != self._current_class:
                self._current_class = class_name
                self.stream.writeln(f"\n{class_name}")
                self.stream.flush()
        super().startTest(test)

    def _finish(self, test, status):
        elapsed = time.perf_counter() - self._started_at
        name = test.id()
        self.durations_of.append((name, elapsed))
        printed = getattr(test, "printed", None)
        if printed is not None and status != "ok":
            self.output_of[name] = printed.getvalue()
        if self.detailed:
            self.stream.writeln(
                f"  {status:<8}{elapsed * 1000:7.1f} ms  "
                f"{name.rsplit('.', 1)[-1]}")
            self.stream.flush()

    def addSuccess(self, test):
        super().addSuccess(test)
        self._finish(test, "ok")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._finish(test, "FAIL")

    def addError(self, test, err):
        super().addError(test, err)
        self._finish(test, "ERROR")

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._finish(test, "skipped")
        if self.detailed:
            self.stream.writeln(f"           reason: {reason}")

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self._finish(test, "expected")

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self._finish(test, "UNEXPECTED")

    # --- the report ---------------------------------------------------------
    def printErrors(self):
        self.stream.writeln()
        super().printErrors()
        self._print_captured_output()
        self._print_summary()

    def _print_captured_output(self):
        interesting = [(name, text) for name, text in self.output_of.items()
                       if text.strip()]
        if not interesting:
            return
        self.stream.writeln(self.separator1)
        self.stream.writeln("what the module printed while it failed")
        self.stream.writeln(self.separator1)
        for name, text in interesting:
            self.stream.writeln(f"\n{name}")
            for line in text.splitlines():
                self.stream.writeln(f"    {line}")

    def _print_summary(self):
        total = time.perf_counter() - self._run_started_at
        failed, errors = len(self.failures), len(self.errors)
        skipped = len(self.skipped)
        passed = self.testsRun - failed - errors - skipped

        self.stream.writeln(self.separator1)
        self.stream.writeln("summary")
        self.stream.writeln(self.separator1)
        for label, value in (("ran", self.testsRun), ("passed", passed),
                             ("failed", failed), ("errors", errors),
                             ("skipped", skipped)):
            if value or label in ("ran", "passed"):
                self.stream.writeln(f"  {label:<10}{value:>5}")
        self.stream.writeln(f"  {'time':<10}{total:>8.3f} s")

        for name, _ in self.failures:
            self.stream.writeln(f"  FAIL   {name.id()}")
        for name, _ in self.errors:
            self.stream.writeln(f"  ERROR  {name.id()}")

        if SLOWEST and self.durations_of:
            slowest = sorted(self.durations_of, key=lambda kv: -kv[1])[:SLOWEST]
            self.stream.writeln(f"\n  slowest {len(slowest)}")
            for name, elapsed in slowest:
                self.stream.writeln(f"    {elapsed * 1000:7.1f} ms  {name}")
        self.stream.flush()


class _Tee:
    """Writes the report to the console and to a file at the same time."""

    def __init__(self, *streams):
        self.streams = streams

    def write(self, text):
        for stream in self.streams:
            stream.write(text)
        return len(text)

    def flush(self):
        for stream in self.streams:
            stream.flush()


def main(target: str = TARGET, verbosity: int = VERBOSITY,
         show_prints: bool = SHOW_PRINTS,
         report_file: str = REPORT_FILE) -> unittest.TestResult:
    """Run ``target`` and return the result.  No ``sys.exit`` - Spyder keeps
    its console."""
    _use_the_project_root()
    _check_the_right_tests_were_found()
    if show_prints:
        os.environ["VALIREPORT_TESTS_SHOW_OUTPUT"] = "1"
    else:
        os.environ.pop("VALIREPORT_TESTS_SHOW_OUTPUT", None)

    loader = unittest.TestLoader()
    if target:
        suite = loader.loadTestsFromName(target)
    else:
        suite = loader.discover(start_dir=str(PROJECT_ROOT / "tests"),
                                top_level_dir=str(PROJECT_ROOT))

    handle = open(report_file, "w", encoding="utf-8") if report_file else None
    stream = _Tee(sys.stdout, handle) if handle else sys.stdout
    try:
        print(f"running {target or 'every test'} "
              f"({suite.countTestCases()} tests) ...", file=stream)
        runner = unittest.TextTestRunner(
            stream=stream,
            verbosity=verbosity,
            resultclass=DetailedResult,
            tb_locals=SHOW_LOCALS,
        )
        return runner.run(suite)
    finally:
        if handle is not None:
            handle.close()
            print(f"\nreport written to {report_file}")


if __name__ == "__main__":
    main()
