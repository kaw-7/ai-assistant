# Periodic Review config - document creation and issue import
# Same settings as valid_report_config.py, filled for a periodic review.
# Polarion project id and issue markup: PolarionAssistant/Core/core_config.py
from datetime import date

# --- STEPS run by valid_report_main.py ('y' / 'n') ---
BUILD_VALID_REPORT = 'y'  # create the periodic review document from the template

# ============================================================================
# COMMON - used by both steps
# ============================================================================
TOOL_NAME = "IAR Embedded Workbench for ARM (IDE) v8.40.1"

# --- POLARION TARGET DOCUMENT ---
# created by the document step, filled by the issue import
TARGET_LOCATION = "Anomaly Reports"
TARGET_TITLE = f"{TOOL_NAME} Periodic Review - {date.today():%B %Y}"  # the month of the run, e.g. "October 2026"
TARGET_NAME_ID = TARGET_TITLE.replace('.', '_')
DOC_NAME = f"wiki/{TARGET_LOCATION}/{TARGET_NAME_ID}"

# ============================================================================
# ISSUE IMPORT
# ============================================================================
DOC_INPUT_HEADING = "Published Issues and Bugs" # currently it has to be a heading

# --- IO PATH SETTINGS ---
tool_folder = "IAR_EW_8_40_1"
ISSUE_INPUT_FILE = f"output/{tool_folder}/final_risk_report.txt" # the risk report written by the AI assistant

# ============================================================================
# DOCUMENT CREATION
# ============================================================================
VALID_REPORT_TEMPLATE = f'wiki/{TARGET_LOCATION}/_PeriodicReviewTemplate' # wiki/Validation Reports/_ValidationReportTemplate CSV

# TARGET_PROJECT_ID = "ToolValidation"

PLACEHOLDER = r'<span style="color: #FF0000;">[toolname]</span>'
PLACEHOLDER_DOCSTATUS = r'<Toolname> <Version>'
