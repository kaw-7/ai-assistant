# Validation Report config - document creation and issue import
# Polarion project id and issue markup: PolarionAssistant/Core/core_config.py
import re

# --- STEPS run by valid_report_main.py ('y' / 'n') ---
BUILD_VALID_REPORT = 'y'  # create the validation report document from the template

# ============================================================================
# COMMON - used by both steps
# ============================================================================
TOOL_NAME = "VectorCAST 2026 SP3"

# --- POLARION TARGET DOCUMENT ---
# created by the document step, filled by the issue import
TARGET_LOCATION = "Validation Reports"
TARGET_TITLE = f"Validation Report {TOOL_NAME}"
TARGET_NAME_ID = re.sub(r'[^\w -]', '_', TARGET_TITLE)  # only letters, digits, ' ', '_' and '-' - a '/' would open a new Polarion space
DOC_NAME = f"wiki/{TARGET_LOCATION}/{TARGET_NAME_ID}"

# ============================================================================
# ISSUE IMPORT
# ============================================================================
DOC_INPUT_HEADING = "Bug Fixes in newer version" # currently it has to be a heading

# --- IO PATH SETTINGS ---
tool_folder = "VectorCAST"
ISSUE_INPUT_FILE = f"output/{tool_folder}/final_risk_report.txt" # the risk report written by the AI assistant

# ============================================================================
# DOCUMENT CREATION
# ============================================================================
VALID_REPORT_TEMPLATE = f'wiki/{TARGET_LOCATION}/_ValidationReportTemplate CSV' # wiki/Anomaly Reports/_PeriodicReviewTemplate

# TARGET_PROJECT_ID = "ToolValidation"

PLACEHOLDER = re.compile(
    r'<span style="color:\s*#[0-9A-Fa-f]{3,8};">'   # 1. color + 2. ;">
    r'[^<]*tool ?name[^<]*'                           # 3. tool.name, dot = optional space
    r'</span>',
    re.IGNORECASE
)

