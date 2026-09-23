# Validation Report config
TOOL_NAME = "VectorCAST 2026 SP3"
TARGET_TITLE = f"Validation Report {TOOL_NAME}"
TARGET_NAME_ID = TARGET_TITLE.replace('.', '_')


VALID_REPORT_DOCU = f"wiki/Validation Reports/Validation Report {TOOL_NAME.replace('.', '_')}"
VALID_REPORT_TEMPLATE = 'wiki/Validation Reports/_ValidationReportTemplate CSV'

PROJECT_ID = 'TOV'

# TARGET_PROJECT_ID = "ToolValidation"
TARGET_LOCATION = "Validation Reports"
LINK_ROLE = None

PLACEHOLDER = r'<span style="color: #FF0000;">[toolname]</span>'
PLACEHOLDER_DOCSTATUS = r'<Toolname> <Version>'