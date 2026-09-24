# tests

Unit tests for the modules of the tool validation assistant. One folder per
package, mirroring the project:

```
tests/
├── support.py                # helpers every test may use
├── AIProvider/               # the contract of the AI back ends
├── Preprocessor/             # release notes -> structured issue markup
├── RiskAssessment/           # structured issues -> risk report
├── PolarionAssistant/        # risk report -> Polarion work items
└── UI/                       # the issue viewer file format
```

The launcher is not covered yet.

## Running them

```bash
python -m unittest discover -s tests -t .        # everything, from the project root
python -m unittest tests.UI.test_issue_serializer          # one module
python -m unittest tests.Preprocessor.test_text_chunker_preprocessor.DelimiterTests
```

Only the standard library is needed - `unittest`, no pytest. The whole run
takes about two seconds and touches neither the network nor `output/`:

* **no server** - the Polarion tests drive fake documents and work items, so
  nothing is created in `TOV`;
* **no AI** - `RecordingAIProvider` answers from a list and records what it
  was asked, so no request is paid for;
* **no file of the project** - every module under test is pointed at a
  temporary folder through its configuration before it runs.

`pytest` also runs these tests unchanged if it is installed.

## The report of `run_tests.py`

`run_tests.py` prints more than the dots of `python -m unittest`: the tests
grouped under their class, the time each one took, and at the end a summary,
the slowest tests and - for a test that did not pass - the traceback with the
local variables of every frame plus what the module printed while it failed.

```
tests.PolarionAssistant.test_issue_parser.FixSourceTests
  ok          0.7 ms  test_a_polarion_id_is_kept
  FAIL        0.6 ms  test_the_name_of_an_entry_is_not_recognised
  skipped     0.0 ms  test_something_skipped
           reason: needs a Polarion session
...
    expected = <IssueSource.CORRECTION_IN_REL_NOTES: 'fixedInNewerVersion'>
    issue = IssueDTO(..., source=<IssueSource.KNOWN_PROBLEM_BY_VENDOR: 'knownBug'>, ...)
AssertionError: ...
======================================================================
what the module printed while it failed
======================================================================
    CORRECTION_IN_REL_NOTES
======================================================================
summary
======================================================================
  ran         144
  passed      144
  time        28.039 s
```

The switches at the top of the file:

| | |
|---|---|
| `TARGET` | module, class or single test; `""` runs everything |
| `VERBOSITY` | `2` lists every test, `1` prints one dot per test |
| `SHOW_PRINTS` | lets the modules print into the console while they pass too |
| `SHOW_LOCALS` | local variables in the traceback of a failure |
| `SLOWEST` | how many of the slowest tests to list, `0` for none |
| `REPORT_FILE` | writes the whole report into that file as well |

## Debugging with them

A test is the cheapest way into a debugger: it reaches the interesting line in
a few milliseconds, with no AI request and no Polarion session in between.

**Spyder** - Spyder starts the file that is open in the editor, so open
`run_tests.py` in the project root, set `TARGET` to what should run and press
**Ctrl+F5** (*Debug file*). The breakpoint goes into the module under test.
Starting a test file itself does not work: Spyder puts the folder of that file
on `sys.path`, not the project root, and `from tests.support import ...` then
fails - `run_tests.py` is there to set the root up first.

> `ModuleNotFoundError: No module named 'tests.PolarionAssistant'` means
> python found *another* `tests` package - the console of an IDE keeps the
> `sys.path` and the modules of everything that ran in it before.
> `run_tests.py` puts the project root in front and drops the stale package,
> and says which one it found if that is still not enough.

**PyCharm** - open the test file, click the green arrow in the gutter next to
the class or the method and pick *Debug*. Put the breakpoint in the module
under test (`PolarionAssistant/Core/IssueParser.py`, not in the test) and the
run configuration that appears is reusable.

**VS Code** - `Testing` in the side bar, *Configure Python Tests* ->
*unittest* -> `tests` -> `test_*.py`, then use the debug arrow next to a test.
Or `.vscode/launch.json`:

```json
{ "name": "debug one test", "type": "debugpy", "request": "launch",
  "module": "unittest", "cwd": "${workspaceFolder}",
  "args": ["tests.PolarionAssistant.test_issue_parser.FixSourceTests"] }
```

**Visual Studio** - *Test Explorer* finds the `unittest` tests once the
project's *Test Framework* is set to `unittest` in the project properties;
right click a test -> *Debug*.

**Without an IDE** - `pdb` takes the same module path:

```bash
python -m pdb -m unittest tests.PolarionAssistant.test_issue_parser.FixSourceTests
(Pdb) b PolarionAssistant/Core/IssueParser.py:113
(Pdb) c
(Pdb) p issue.source, type(issue.source)
```

or drop a `breakpoint()` into the module under test and run the test as usual.

`QuietTestCase` steps aside while a debugger is attached (`sys.gettrace()`),
so breakpoint prompts and prints reach the console instead of the capture
buffer. Without a debugger, `VALIREPORT_TESTS_SHOW_OUTPUT=1` does the same.

## Writing one

`tests/support.py` holds what the tests share:

| | |
|---|---|
| `QuietTestCase` | collects what the module prints, so a debug line does not scroll the result of the run away |
| `TempDirTestCase` | the same, plus a temporary folder and `path()`, `write()`, `read()` |
| `config_values(module, **values)` | replaces constants of a configuration module for the duration of a `with` block - exactly what the launcher does before a run |
| `RecordingAIProvider` | an `AIProvider` that answers from a list and keeps the prompts |
| `captured_stdout()` | collects what the module prints; `quiet_stderr=True` also swallows the `tqdm` progress bars |
| `issue_markup()` / `issues_markup(n)` | issue items in the markup the AI produces, shaped like a real `final_risk_report.txt` |

A test that lets a module write has to redirect the configuration first, or
it overwrites the real report:

```python
with config_values(config, RISK_ASSESSMENT_OUTPUT_FILE=self.path("report.txt")):
    agent.process_issues(issues_markup(4))
```

## What the tests found

Four things the tests record as today's behaviour rather than as the intended
one. None of them is changed by the tests - they are listed here so that a
test that starts failing after a fix is understood as the fix working.

1. ~~**Every imported issue becomes a vendor bug.**~~ **Fixed.** The two
   vocabularies are separate now: `SourceDTO` / `StatusDTO` hold the words the
   AI writes into the report (`CORRECTION_IN_REL_NOTES`, `NOT_EVALUATED`),
   `IssueSource` / `IssueStatus` the ids Polarion stores
   (`fixedInNewerVersion`, `not_evaluated`), and the two `_fix_*` methods
   translate between them by name. A value that is already an id is taken as
   it is, and everything reaches Polarion as a plain string - no `.value` is
   read off an issue field any more.
   *`tests/PolarionAssistant/test_issue_parser.py::FixSourceTests`,
   `::FixStatusTests`*

2. **The last defect of an IAR file is filled in differently.**
   `parse_txt_to_csv` writes the author and the status for every defect but
   the last one - that row is built by a second, shorter piece of code and
   reaches the CSV with both columns empty.
   *`tests/Preprocessor/test_iarew_preprocessor.py::ParseTxtToCsvTests`*

3. **The IAR defect pattern and the code around it disagree.**
   `defect_id_regex` is anchored at the start of the line (`^IDE-\d+`) while
   the lines are then cut at `[` and `]`, so only `IDE-1] text` is read and
   the bracketed form `[IDE-1] text` is skipped altogether.
   *`tests/Preprocessor/test_iarew_preprocessor.py::DefectIdRegexTests`*

4. **One AI request per run is wasted.**
   The risk agent walks the report by end marker; the newline behind the last
   marker counts as a rest, so a last request is sent that contains no issue.
   *`tests/RiskAssessment/test_ai_risk_assessment_agent.py::ProcessIssuesTests`*

## What is not covered

* the launcher (`Launcher/`) - asked for separately;
* everything that only talks to Polarion: `PolarionConnector`, the work item
  creation inside `IssueDAOFactory.create`, `TestCaseBuilder`,
  `ValidReportBuilder`.  Their pure parts (`PolarionWorker._ModifyItems`,
  `ItemUtil.find_heading_item_by_name`) are tested with fake documents;
* the tkinter windows (`UI/App.py`, `UI/IssueCard.py`) - only the file format
  they read and write is covered;
* the concrete AI providers - only that they fulfil the contract and take the
  `user_input` argument their callers pass.
