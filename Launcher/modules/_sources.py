# -*- coding: utf-8 -*-
"""Configuration sources shared by the runnable modules.

Files starting with an underscore are ignored by the module registry, so this
is a plain helper module.

Each factory returns a *fresh* source object - the launcher fills the parsed
defaults into the field descriptors, so they must not be shared between calls.
Everything declared here is only cosmetic: constants that are not listed still
show up in the editor under "Other settings", they simply get a plain text box.

One source per configuration *file*: since the configuration of the modules was
split, the AI assistant (``config.py``) and the Polarion issue import
(``PolarionAssistant/issue_importer_config.py``) no longer share anything.
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
ISSUE_IMPORTER_CONFIG = "issue_importer_config"
VALID_REPORT_CONFIG = "valid_report_config"

YES_NO = ("y", "n")

SECTION_TOOL = "Validated tool"
SECTION_AI = "AI processing"
SECTION_INSTRUCTIONS = "Instruction files"
SECTION_OUTPUT = "Generated files"
SECTION_DOCUMENT = "Polarion document"
SECTION_MARKUP = "Issue markup"
SECTION_FILES = "Files"


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
            ConfigField("TOOL_PREPROCESSOR", "Preprocessor",
                        kind=FieldKind.CHOICE, section=SECTION_TOOL,
                        choices=("AI", "IAR_EmbeddedWorkbench", "Reload_Existing")),
            ConfigField("TOOL_RELEASE_NOTES", "Release notes file",
                        kind=FieldKind.FILE, section=SECTION_TOOL),
            ConfigField("REF_PATH", "Reference report", kind=FieldKind.FILE,
                        section=SECTION_TOOL),

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


def issue_importer_config_source() -> PyModuleConfigSource:
    """``PolarionAssistant/issue_importer_config.py`` - the Polarion import.

    Own file since the configuration split: the target document and the report
    to read are no longer shared with ``config.py``.
    """
    return PyModuleConfigSource(
        source_id=ISSUE_IMPORTER_CONFIG,
        title="Issue import configuration (issue_importer_config.py)",
        module_name="PolarionAssistant.issue_importer_config",
        file_path=project_path("PolarionAssistant", "issue_importer_config.py"),
        description=(
            "Which document the assessed issues are written to and which risk "
            "report they are read from. Independent of config.py - 'Tool "
            "folder' has to name the same output folder as the AI assistant."
        ),
        field_specs=[
            ConfigField("PROJECT_ID", "Polarion project id", section=SECTION_DOCUMENT),
            ConfigField("DOC_NAME", "Target document", section=SECTION_DOCUMENT),
            ConfigField("DOC_INPUT_HEADING", "Target heading", section=SECTION_DOCUMENT),

            ConfigField("tool_folder", "Tool folder", section=SECTION_FILES,
                        help="Sub folder of output/, as in config.py"),
            ConfigField("ISSUE_INPUT_FILE", "Issues to import",
                        kind=FieldKind.FILE, section=SECTION_FILES),

            ConfigField("ISSUE_MARKER_BEG", "Marker start", section=SECTION_MARKUP),
            ConfigField("ISSUE_MARKER_END", "Marker end", section=SECTION_MARKUP),
            ConfigField("ISSUE_END_MARKER", "Issue end marker", section=SECTION_MARKUP),
        ],
    )


def valid_report_config_source() -> PyModuleConfigSource:
    """``PolarionAssistant/ValidReport/valid_report_config.py``."""
    return PyModuleConfigSource(
        source_id=VALID_REPORT_CONFIG,
        title="Validation report configuration (valid_report_config.py)",
        module_name="ValidReport.valid_report_config",
        file_path=project_path("PolarionAssistant", "ValidReport",
                               "valid_report_config.py"),
        description=(
            "Template and title of the validation report document created in "
            "Polarion. The title and the document name follow the tool name."
        ),
        field_specs=[
            ConfigField("TOOL_NAME", "Tool name", section=SECTION_DOCUMENT),
            ConfigField("PROJECT_ID", "Polarion project id", section=SECTION_DOCUMENT),
            ConfigField("VALID_REPORT_TEMPLATE", "Template document",
                        section=SECTION_DOCUMENT),
            ConfigField("VALID_REPORT_DOCU", "Target document",
                        section=SECTION_DOCUMENT),
            ConfigField("TARGET_LOCATION", "Target space", section=SECTION_DOCUMENT),
            ConfigField("TARGET_TITLE", "Document title", section=SECTION_DOCUMENT),
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
            ConfigField("PADX", "Horizontal padding", kind=FieldKind.INT,
                        section="Appearance"),
            ConfigField("PADY", "Vertical padding", kind=FieldKind.INT,
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
        description="Documents used when the test cases are moved.",
        field_specs=[
            ConfigField("PROJECT_ID", "Polarion project id", section="Documents"),
            ConfigField("PLAN_DOCU", "Validation plan document", section="Documents"),
            ConfigField("TEST_DOCU", "Test specification document", section="Documents"),
            ConfigField("DOC_INPUT_HEADING", "Target heading", section="Documents"),
        ],
        section_default="Documents",
    )
