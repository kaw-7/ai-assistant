# --- VALIDATED TOOL SETTINGS ---
TOOL_PREPROCESSOR = "AI"    #"AI", "IAR_EmbeddedWorkbench", "Reload_Existing" - default is AI, Reload_Existing - skip preprocessor

tool_folder = "EA"
TOOL_RELEASE_NOTES = f"input/releaseNotes/{tool_folder}/EA.txt" # input/Framework Release _ NUnit Docs.htm  VSCode_rel_notes.txt
TOOL_NAME = "Enterprise Architect 15" # NUnit "Microchip MPLAB X30 compiler"
TOOL_VERSION_START = "15.0" 
TOOL_VERSION_END = "18"   

MAX_COUNT_OF_ISSUES_PROCESSED_AT_ONCE_BY_AI = 10

SKIP_ENTIRE_AI = "y" #None "y" "n"
PROCEED_WITH_AI_RISK_ASSESSMENT = "y" #None "y" "n"`
USE_PREPROCESS_CHUNKING = "n"

# --- IO PATH SETTINGS ---
INSTRUCTIONS_CHUNKING_PATH = "input/tool_vali_chunking.txt" #tool_vali_create_csv
INSTRUCTIONS_PATH = "input/tool_vali_create_simple_issues_markup.txt" #tool_vali_create_csv
RISK_INSTRUCTIONS_PATH = "input/tool_vali_risk_assessment_markup.txt" #tool_vali_risk_assessment
RISK_SUMMARY_INSTRUCTIONS_PATH = "input/tool_vali_risk_summary.txt"

REF_PATH = "input/VC24_Axivion_gold_standard.txt" #reconstructed_vector_cast_24_gold_standard.csv


TEMP_REL_NOTES = f"output/{tool_folder}/temp_rel_notes.txt"
TEMP_CHUNK_FILE = f"output/{tool_folder}/temp_chunk.txt"
TEMP_OUTPUT_FILE = f"output/{tool_folder}/temp_output.txt"
CONTEXT_FILE = f"output/{tool_folder}/temp_context.txt"
RISK_ASSESSMENT_OUTPUT_FILE = f"output/{tool_folder}/final_risk_report.txt"
# RISK_ASSESSMENT_OUTPUT_FILE = f"input/releaseNotes/final_risk_report.txt"
RISK_SUMMARY_OUTPUT_FILE = f"output/{tool_folder}/risk_summary_report.txt"
CSV_TEMPLATE = "input/template.csv"

# --- AI MODEL SETTINGS ---
# MODEL_NAME = "gpt-5.4-mini"  "gemini-2.5-flash"

# --- miscellaneous --- 
ISSUE_END_MARKER = "[[ END ISSUE ITEM ]]"

CHUNK_DELIMITER = "[[ =cut= ]]"
CHUNK_SIZE = 10000

# POLARION CONFIGURATION

DOC_NAME = "wiki/Validation Reports/Validation Report Enterprise Architect v15_0_1514"
DOC_INPUT_HEADING = "Known Issues" #currently it has to be a heading

PROJECT_ID = 'TOV'  # e.g., 'MYPROJECT', 'Python'

ISSUE_MARKER_BEG = "[["
ISSUE_MARKER_END = "]]"

ISSUE_INPUT_FILE = RISK_ASSESSMENT_OUTPUT_FILE

