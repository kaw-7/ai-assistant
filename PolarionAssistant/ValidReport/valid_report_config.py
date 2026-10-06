# Validation Report config - document creation and issue import

# --- STEPS run by valid_report_main.py ('y' / 'n') ---
BUILD_VALID_REPORT = 'y'  # create the validation report document from the template

# ============================================================================
# COMMON - used by both steps
# ============================================================================
PROJECT_ID = 'TOV'  # e.g., 'MYPROJECT', 'Python'

TOOL_NAME = "VectorCAST 2026 SP3"

# --- POLARION TARGET DOCUMENT ---
# created by the document step, filled by the issue import
TARGET_LOCATION = "Validation Reports"
TARGET_TITLE = f"Validation Report {TOOL_NAME}"
TARGET_NAME_ID = TARGET_TITLE.replace('.', '_')
DOC_NAME = f"wiki/{TARGET_LOCATION}/{TARGET_NAME_ID}"

# ============================================================================
# ISSUE IMPORT
# ============================================================================
DOC_INPUT_HEADING = "Bug Fixes in newer version" # currently it has to be a heading

# --- IO PATH SETTINGS ---
tool_folder = "Axivion7.4"
ISSUE_INPUT_FILE = f"output/{tool_folder}/final_risk_report.txt" # the risk report written by the AI assistant

# --- ISSUE MARKUP ---
# has to match the markup the AI assistant produced in ISSUE_INPUT_FILE
ISSUE_MARKER_BEG = "[["
ISSUE_MARKER_END = "]]"
ISSUE_END_MARKER = "[[ END ISSUE ITEM ]]"

# ============================================================================
# DOCUMENT CREATION
# ============================================================================
VALID_REPORT_TEMPLATE = 'wiki/Validation Reports/_ValidationReportTemplate CSV'

# TARGET_PROJECT_ID = "ToolValidation"
LINK_ROLE = None

PLACEHOLDER = r'<span style="color: #FF0000;">[toolname]</span>'
PLACEHOLDER_DOCSTATUS = r'<Toolname> <Version>'
