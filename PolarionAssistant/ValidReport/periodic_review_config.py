# Periodic Review config - document creation and issue import
# Same settings as valid_report_config.py, filled for a periodic review.
# Polarion project id and issue markup: PolarionAssistant/Core/core_config.py
import re
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
TARGET_NAME_ID = re.sub(r'[^\w -]', '_', TARGET_TITLE)  # only letters, digits, ' ', '_' and '-' - a '/' would open a new Polarion space
DOC_NAME = f"wiki/{TARGET_LOCATION}/{TARGET_NAME_ID}"

# ============================================================================
# ISSUE IMPORT
# ============================================================================
# currently it has to be a heading
DOC_INPUT_HEADING = "Bug Fixes in newer version" # Published Issues and Bugs

# --- IO PATH SETTINGS ---
tool_folder = "IAR_EW_8_40_1"
ISSUE_INPUT_FILE = f"output/{tool_folder}/final_risk_report.txt" # the risk report written by the AI assistant

# ============================================================================
# DOCUMENT CREATION
# ============================================================================
VALID_REPORT_TEMPLATE = f'wiki/{TARGET_LOCATION}/_PeriodicReviewTemplate' # wiki/Validation Reports/_ValidationReportTemplate CSV

# TARGET_PROJECT_ID = "ToolValidation"
PLACEHOLDER = re.compile(
    r'<span style="color:\s*#[0-9A-Fa-f]{3,8};">'   # 1. color + 2. ;">
    r'[^<]*tool ?name[^<]*'                           # 3. tool.name, dot = optional space
    r'</span>',
    re.IGNORECASE
)