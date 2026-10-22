# -*- coding: utf-8 -*-
"""Configuration sources shared by the runnable modules.

Files starting with an underscore are ignored by the module registry, so this
is a plain helper module.

Each factory returns a *fresh* source object - the launcher fills the parsed
defaults into the field descriptors, so they must not be shared between calls.
Everything declared here is only cosmetic: constants that are not listed still
show up in the editor under "Other settings", they simply get a plain text box.

One source per configuration *file*, one configuration file per module: the AI
assistant (``config.py``) and the validation report module
(``PolarionAssistant/ValidReport/valid_report_config.py``) no longer share anything.
"""
from __future__ import annotations

from Launcher.core.config_fields import ConfigField, FieldKind
from Launcher.core.config_sources import EnvFileConfigSource, PyModuleConfigSource
from Launcher.core.project import project_path

# --- source ids (also the keys inside launcher_settings.json) ---------------
MAIN_CONFIG = "main_config"
UI_CONFIG = "ui_config"
POLARION_ENV = "polarion_env"
TESTSPEC_CONFIG = "testspec_config"
VALID_REPORT_CONFIG = "valid_report_config"
PERIODIC_REVIEW_CONFIG = "periodic_review_config"

#: argument of valid_report_main.py: which report document is worked on
REPORT_INITIAL = "initial"
REPORT_PERIODIC = "periodic"

YES_NO = ("y", "n")

SECTION_TOOL = "Validated tool"
SECTION_AI = "AI processing"
SECTION_INSTRUCTIONS = "Instruction files"
SECTION_OUTPUT = "Generated files"
SECTION_POLARION = "Polarion"
SECTION_MARKUP = "Issue markup"
SECTION_FILES = "Files"
SECTION_STEPS = "Steps"


# besides letters and digits - anything else in a document id ('/' opens a new
# Polarion space) has to be reworked before a run
DOCUMENT_ID_EXTRA_CHARS = " _-"


def _document_id_problem(value: str) -> str:
    bad = sorted({c for c in value if not (c.isalnum() or c in DOCUMENT_ID_EXTRA_CHARS)})
    if not bad:
        return ""
    return (f"The document id contains {' '.join(repr(c) for c in bad)} - only letters, "
            "digits, spaces, '_' and '-' are allowed. Rework the tool name or the "
            "document title, or switch Override on and modify the id.")


def _document_id_field() -> ConfigField:
    """TARGET_NAME_ID - the name the document is created under in Polarion."""
    return ConfigField("TARGET_NAME_ID", "Document id", section=SECTION_POLARION,
                       check=_document_id_problem)


def _preprocessor_field() -> ConfigField:
    """The choices are the values of ``PreprocessorType`` - the enum main.py
    matches on - so a new preprocessor shows up here by itself."""
    try:
        # imported here: the module imports config.py, which must not stop
        # the launcher from starting when it is broken
        from Preprocessor.AbstractPreprocessor import PreprocessorType
    except Exception:
        # no list at all rather than one that may be stale
        return ConfigField("TOOL_PREPROCESSOR", "Preprocessor", section=SECTION_TOOL)
    return ConfigField("TOOL_PREPROCESSOR", "Preprocessor",
                       kind=FieldKind.CHOICE, section=SECTION_TOOL,
                       choices=tuple(member.value for member in PreprocessorType))


def main_config_source() -> PyModuleConfigSource:
    """``config.py`` - the issue formatter and the AI risk assessment."""
    return PyModuleConfigSource(
        source_id=MAIN_CONFIG,
        title="AI assistant configuration (config.py)",
        module_name="config",
        file_path=project_path("config.py"),
        description=(
            "Release notes of the validated tool, the AI steps and the files "
            "they write. Entries written as f-strings are recomputed from the "
            "values above them."
        ),
        field_specs=[
            # --- validated tool ---
            ConfigField("tool_folder", "Tool folder", section=SECTION_TOOL,
                        help="Sub folder of input/releaseNotes and output/"),
            ConfigField("TOOL_NAME", "Tool name", section=SECTION_TOOL),
            ConfigField("TOOL_VERSION_START", "Version from", section=SECTION_TOOL),
            ConfigField("TOOL_VERSION_END", "Version to", section=SECTION_TOOL),
            _preprocessor_field(),
            ConfigField("TOOL_RELEASE_NOTES", "Release notes file",
                        kind=FieldKind.FILE, section=SECTION_TOOL),
            ConfigField("REF_PATH", "Reference report", kind=FieldKind.FILE,
                        section=SECTION_TOOL),
            ConfigField("REF_PATH2_OPT", "2nd reference report (optional)",
                        kind=FieldKind.FILE, section=SECTION_TOOL,
                        help="Leave empty to use only the reference report."),

            # --- AI processing ---
            ConfigField("PROCEED_WITH_AI_RISK_ASSESSMENT",
                        "Proceed with the AI risk assessment",
                        kind=FieldKind.CHOICE, choices=YES_NO, section=SECTION_AI),
            ConfigField("USE_PREPROCESS_CHUNKING", "Chunk before preprocessing",
                        kind=FieldKind.CHOICE, choices=YES_NO, section=SECTION_AI),
            ConfigField("MAX_COUNT_OF_ISSUES_PROCESSED_AT_ONCE_BY_AI",
                        "Issues per AI request", kind=FieldKind.INT,
                        section=SECTION_AI),
            ConfigField("CHUNK_SIZE", "Chunk size", kind=FieldKind.INT,
                        section=SECTION_AI),
            ConfigField("CHUNK_DELIMITER", "Chunk delimiter", section=SECTION_AI),

            # --- instructions ---
            ConfigField("INSTRUCTIONS_PATH", "Issue creation instructions",
                        kind=FieldKind.FILE, section=SECTION_INSTRUCTIONS),
            ConfigField("INSTRUCTIONS_CHUNKING_PATH", "Chunking instructions",
                        kind=FieldKind.FILE, section=SECTION_INSTRUCTIONS),
            ConfigField("RISK_INSTRUCTIONS_PATH", "Risk assessment instructions",
                        kind=FieldKind.FILE, section=SECTION_INSTRUCTIONS),
            ConfigField("RISK_SUMMARY_INSTRUCTIONS_PATH", "Risk summary instructions",
                        kind=FieldKind.FILE, section=SECTION_INSTRUCTIONS),
            ConfigField("CSV_TEMPLATE", "CSV template", kind=FieldKind.FILE,
                        section=SECTION_INSTRUCTIONS),

            # --- generated files ---
            ConfigField("TEMP_REL_NOTES", "Preprocessed release notes",
                        kind=FieldKind.FILE, section=SECTION_OUTPUT),
            ConfigField("TEMP_CHUNK_FILE", "Chunk file", kind=FieldKind.FILE,
                        section=SECTION_OUTPUT),
            ConfigField("TEMP_OUTPUT_FILE", "Structured issues",
                        kind=FieldKind.FILE, section=SECTION_OUTPUT),
            ConfigField("CONTEXT_FILE", "AI context file", kind=FieldKind.FILE,
                        section=SECTION_OUTPUT),
            ConfigField("RISK_ASSESSMENT_OUTPUT_FILE", "Final risk report",
                        kind=FieldKind.FILE, section=SECTION_OUTPUT),
            ConfigField("RISK_ASSESSMENT_OUTPUT_FILE_BACK_UP", "Risk report backup",
                        kind=FieldKind.FILE, section=SECTION_OUTPUT),
            ConfigField("RISK_SUMMARY_OUTPUT_FILE", "Risk summary report",
                        kind=FieldKind.FILE, section=SECTION_OUTPUT),

            # --- markup ---
            ConfigField("ISSUE_END_MARKER", "Issue end marker", section=SECTION_MARKUP),
        ],
        # not a setting, just a helper object created inside config.py
        ignore=("path", "Path"),
    )


def valid_report_config_source() -> PyModuleConfigSource:
    """``PolarionAssistant/ValidReport/valid_report_config.py`` - module 3a."""
    return _report_config_source(VALID_REPORT_CONFIG, "Validation report")


def periodic_review_config_source() -> PyModuleConfigSource:
    """``PolarionAssistant/ValidReport/periodic_review_config.py`` - module 3b."""
    return _report_config_source(PERIODIC_REVIEW_CONFIG, "Periodic review")


def _report_config_source(file_stem: str, title: str) -> PyModuleConfigSource:
    """A configuration file of a report document; the source id is the file name.

    One file for both steps: the document created from the template is the
    document the issues are imported into.
    """
    return PyModuleConfigSource(
        source_id=file_stem,
        title=f"{title} configuration ({file_stem}.py)",
        module_name=f"PolarionAssistant.ValidReport.{file_stem}",
        file_path=project_path("PolarionAssistant", "ValidReport", f"{file_stem}.py"),
        description=(
            "Steps run by valid_report_main.py, the target document shared by "
            "both steps, the risk report the issues are read from and the "
            "template the document is created from. 'Tool folder' has to name "
            "the same output folder as the AI assistant."
        ),
        # ValidReportBuilder is also reachable through 'ValidReport.*'
        aliases=(f"ValidReport.{file_stem}",),
        field_specs=[
            ConfigField("BUILD_VALID_REPORT", f"Build the {title.lower()}",
                        kind=FieldKind.CHOICE, choices=YES_NO, section=SECTION_STEPS),

            ConfigField("TOOL_NAME", "Tool name", section=SECTION_POLARION),
            ConfigField("TARGET_TITLE", "Document title", section=SECTION_POLARION),
            _document_id_field(),
            ConfigField("DOC_NAME", "Target document", section=SECTION_POLARION),
            ConfigField("DOC_INPUT_HEADING", "Target heading", section=SECTION_POLARION),
            ConfigField("VALID_REPORT_TEMPLATE", "Template document",
                        section=SECTION_POLARION),
            ConfigField("TARGET_LOCATION", "Target space", section=SECTION_POLARION,
                        editable=False,
                        help="Read only - change it in the configuration file."),

            ConfigField("tool_folder", "Tool folder", section=SECTION_FILES,
                        help="Sub folder of output/, as in config.py"),
            ConfigField("ISSUE_INPUT_FILE", "Issues to import",
                        kind=FieldKind.FILE, section=SECTION_FILES),
        ],
        section_default="Placeholders",
    )


def ui_config_source() -> PyModuleConfigSource:
    """``UI/ui_config.py`` - the issue viewer keeps its own settings."""
    return PyModuleConfigSource(
        source_id=UI_CONFIG,
        title="Issue viewer configuration (UI/ui_config.py)",
        module_name="UI.ui_config",
        file_path=project_path("UI", "ui_config.py"),
        description="Look and feel of the issue viewer and the file it opens.",
        # UI/main.py reads the very same file as a top level module
        aliases=("ui_config",),
        field_specs=[
            ConfigField("ISSUES_FILE", "Issues file", kind=FieldKind.FILE,
                        section=SECTION_FILES,
                        help="Relative to the project root."),
            ConfigField("ISSUES_BACKUP_FILE", "Backup file", kind=FieldKind.FILE,
                        section=SECTION_FILES),
            ConfigField("GEOMETRY", "Window size", section="Appearance"),
            ConfigField("FONT", "Font", section="Appearance"),
            ConfigField("FONT_SIZE", "Font size", kind=FieldKind.INT,
                        section="Appearance"),
        ],
        section_default="Labels and tokens",
    )


def polarion_env_source() -> EnvFileConfigSource:
    """``.polarion.env`` - server credentials used by every Polarion module."""
    return EnvFileConfigSource(
        source_id=POLARION_ENV,
        title="Polarion server (.polarion.env)",
        file_path=project_path(".polarion.env"),
        description="Applied as environment variables, the file stays untouched.",
        field_specs=[
            ConfigField("POLARION_URL", "Server URL", section="Connection"),
            ConfigField("POLARION_USER", "User", section="Connection"),
            ConfigField("POLARION_PASS", "Password", section="Connection",
                        secret=True, persist=False,
                        help="Kept for this launcher session only, never saved."),
        ],
    )


def testspec_config_source() -> PyModuleConfigSource:
    """``PolarionAssistant/TestSpec/testspec_config.py``."""
    return PyModuleConfigSource(
        source_id=TESTSPEC_CONFIG,
        title="Test specification configuration (testspec_config.py)",
        module_name="TestSpec.testspec_config",
        file_path=project_path("PolarionAssistant", "TestSpec", "testspec_config.py"),
        description=(
            "Steps run by test_spec_main.py, the template the test specification "
            "is created from and the documents the test cases are moved "
            "between. With 'Debug only' set to 'y' nothing is changed in "
            "Polarion - the documents are only printed."
        ),
        field_specs=[
            ConfigField("CREATE_TEST_SPEC", "Create the test specification",
                        kind=FieldKind.CHOICE, choices=YES_NO, section=SECTION_STEPS),
            ConfigField("DEBUG", "Debug only (no changes in Polarion)",
                        kind=FieldKind.CHOICE, choices=YES_NO, section=SECTION_STEPS),

            ConfigField("PROJECT_ID", "Polarion project id", section=SECTION_POLARION),
            ConfigField("TOOL_NAME", "Tool name", section=SECTION_POLARION),
            ConfigField("TARGET_TITLE", "Document title", section=SECTION_POLARION),
            _document_id_field(),
            ConfigField("PLAN_DOCU", "Validation plan document", section=SECTION_POLARION),
            ConfigField("TEST_DOCU", "Test specification document",
                        section=SECTION_POLARION),
            ConfigField("DOC_INPUT_HEADING", "Target heading", section=SECTION_POLARION),
            ConfigField("TEST_SPEC_TEMPLATE", "Template document",
                        section=SECTION_POLARION),
            ConfigField("TARGET_LOCATION", "Target space", section=SECTION_POLARION,
                        editable=False,
                        help="Read only - change it in the configuration file."),
        ],
        # a set - a text box would turn it into a string and 'in' would then
        # match substrings of the heading titles; edit it in the file
        ignore=("VALI_PLAN_EXCLUDED_HEADINGS",),
        section_default="Placeholders",
    )
