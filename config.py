# --- VALIDATED TOOL SETTINGS ---
DO_AI_PROCESSING = True # True or False
TOOL_PREPROCESSOR = "Reload_Existing"    #"AI", "IAR_EmbeddedWorkbench", "Reload_Existing" - default is AI

TOOL_RELEASE_NOTES = "input/Axivion-Suite-ChangeLog-7.11.4.txt"
TOOL_NAME = "Axivion 7.11.2" #"Microchip MPLAB X30 compiler"
TOOL_VERSION_START = "7.11.2"  #"9.2.4"
TOOL_VERSION_END = "7.11.4"   #"9.4.1"

MAX_COUNT_OF_ISSUES_PROCESSED_AT_ONCE_BY_AI = 10

ISSUE_BEGIN_MARKER = "[[ END ISSUE ITEM ]]"


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
FIRST_CSV_COLUMN = "Author"
AUTHOR_NAME = "software_developer"
FINAL_OUTPUT_EXT = "xlsx"

# POLARION CONFIGURATION

DOC_NAME = "Validation Report Axivion 7_11_2" #"Validation Report Test"
DOC_INPUT_HEADING = "Known Issues" #currently it has to be a heading

PROJECT_ID = 'TOV'  # e.g., 'MYPROJECT', 'Python'

ISSUE_MARKER_BEG = "[["
ISSUE_MARKER_END = "]]"

ISSUE_INPUT_FILE = RISK_ASSESSMENT_OUTPUT_FILE

