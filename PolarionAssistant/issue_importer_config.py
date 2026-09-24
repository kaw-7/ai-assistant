# --- POLARION TARGET DOCUMENT ---
PROJECT_ID = 'TOV'  # e.g., 'MYPROJECT', 'Python'

DOC_NAME = "wiki/Anomaly Reports/Axivion v7_4_6 - Periodic Review - September 2026" # "wiki/Validation Reports/Validation Report VectorCAST 2026 SP3"
DOC_INPUT_HEADING = "Bug Fixes in newer version" # currently it has to be a heading

# --- IO PATH SETTINGS ---
tool_folder = "Axivion7.4"
ISSUE_INPUT_FILE = f"output/{tool_folder}/final_risk_report.txt" # the risk report written by the AI assistant

# --- ISSUE MARKUP ---
# has to match the markup the AI assistant produced in ISSUE_INPUT_FILE
ISSUE_MARKER_BEG = "[["
ISSUE_MARKER_END = "]]"
ISSUE_END_MARKER = "[[ END ISSUE ITEM ]]"
