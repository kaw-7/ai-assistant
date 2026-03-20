# --- VALIDATED TOOL SETTINGS ---
TOOL_PREPROCESSOR = "AI"    #"AI", "IAR_EmbeddedWorkbench", "Reload_Existing" - default is AI, Reload_Existing - skip preprocessor

TOOL_RELEASE_NOTES = "input/VSCode_rel_notes.txt"
TOOL_NAME = "VSCode" #"Microchip MPLAB X30 compiler"
TOOL_VERSION_START = "1.109"  #"9.2.4"
TOOL_VERSION_END = "1.113"   #"9.4.1"

MAX_COUNT_OF_ISSUES_PROCESSED_AT_ONCE_BY_AI = 3

# --- IO PATH SETTINGS ---
INSTRUCTIONS_PATH = "input/tool_vali_create_simple_issues_markup.txt" #tool_vali_create_csv
RISK_INSTRUCTIONS_PATH = "input/tool_vali_risk_assessment_markup.txt" #tool_vali_risk_assessment
RISK_SUMMARY_INSTRUCTIONS_PATH = "input/tool_vali_risk_summary.txt"

REF_PATH = "input/VC24_Axivion_gold_standard.txt" #reconstructed_vector_cast_24_gold_standard.csv

TEMP_OUTPUT_FILE = "output/temp_output.txt"
CONTEXT_FILE = "output/temp_context.txt"
RISK_ASSESSMENT_OUTPUT_FILE = "output/final_risk_report.txt"
RISK_SUMMARY_OUTPUT_FILE = "output/risk_summary_report.txt"

CSV_TEMPLATE = "input/template.csv"

# --- AI MODEL SETTINGS ---
MODEL_NAME = "gemini-2.5-flash"

# --- miscellaneous --- 
ISSUE_END_MARKER = "[[ END ISSUE ITEM ]]"

FIRST_CSV_COLUMN = "Author"
AUTHOR_NAME = "software_developer"
FINAL_OUTPUT_EXT = "xlsx"

# POLARION CONFIGURATION

DOC_NAME = "Validation Report Test" #"Validation Report Test"
DOC_INPUT_HEADING = "Known Issues" #currently it has to be a heading

PROJECT_ID = 'TOV'  # e.g., 'MYPROJECT', 'Python'

ISSUE_MARKER_BEG = "[["
ISSUE_MARKER_END = "]]"

ISSUE_INPUT_FILE = RISK_ASSESSMENT_OUTPUT_FILE

