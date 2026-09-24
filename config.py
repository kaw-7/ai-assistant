# --- VALIDATED TOOL SETTINGS ---
TOOL_PREPROCESSOR = "Reload_Existing"    #"AI", "IAR_EmbeddedWorkbench", "Reload_Existing" - default is AI, Reload_Existing - skip preprocessor

tool_folder = "VectorCAST25_26/SP4" 
TOOL_RELEASE_NOTES = f"input/releaseNotes/{tool_folder}/release_notes_vc2026_SP4.txt" # f"input/releaseNotes/{tool_folder}/rn0094-stm32cubemx-release-6170-stmicroelectronics.txt" 
TOOL_NAME = "VectorCAST 2025 SP3" # NUnit "Microchip MPLAB X30 compiler"
TOOL_VERSION_START = "2026 SP4"
TOOL_VERSION_END = "2026 SP4"

MAX_COUNT_OF_ISSUES_PROCESSED_AT_ONCE_BY_AI = 10

SKIP_ENTIRE_AI = "y" #None "y" "n"
PROCEED_WITH_AI_RISK_ASSESSMENT = "y" #None "y" "n"`
USE_PREPROCESS_CHUNKING = "n"

# --- IO PATH SETTINGS ---
INSTRUCTIONS_CHUNKING_PATH = "input/tool_vali_chunking.txt" #tool_vali_create_csv
INSTRUCTIONS_PATH = "input/tool_vali_create_simple_issues_markup.txt" #tool_vali_create_csv
RISK_INSTRUCTIONS_PATH = "input/tool_vali_risk_assessment_markup.txt" #tool_vali_risk_assessment
RISK_SUMMARY_INSTRUCTIONS_PATH = "input/tool_vali_risk_summary.txt"

REF_PATH = f"input/VC24_Axivion_gold_standard.txt" #"reconstructed_vector_cast_24_gold_standard.csv"

from pathlib import Path
path = Path(f"output/{tool_folder}")
path.mkdir(parents=True, exist_ok=True)
TEMP_REL_NOTES = f"output/{tool_folder}/temp_rel_notes.txt"
TEMP_CHUNK_FILE = f"output/{tool_folder}/temp_chunk.txt"
TEMP_OUTPUT_FILE = f"output/{tool_folder}/temp_output_risk.txt"
CONTEXT_FILE = f"output/{tool_folder}/temp_context.txt"
RISK_ASSESSMENT_OUTPUT_FILE = f"output/{tool_folder}/final_risk_report.txt"
# RISK_ASSESSMENT_OUTPUT_FILE = f"output/EA_16_17/final_risk_report.txt"
RISK_ASSESSMENT_OUTPUT_FILE_BACK_UP = f"output/{tool_folder}/final_risk_report.bck"
RISK_SUMMARY_OUTPUT_FILE = f"output/{tool_folder}/risk_summary_report.txt"
CSV_TEMPLATE = "input/template.csv"

# --- AI MODEL SETTINGS ---
# MODEL_NAME = "gpt-5.4-mini"  "gemini-2.5-flash"

# --- miscellaneous --- 
ISSUE_END_MARKER = "[[ END ISSUE ITEM ]]"

CHUNK_DELIMITER = "[[ =cut= ]]"
CHUNK_SIZE = 10000

# UI config save files
ISSUES_FILE = "output/{tool_folder}/final_risk_report.txt"
ISSUES_BACKUP_FILE = "output/{tool_folder}/final_risk_report.bck"

# POLARION CONFIGURATION
DOC_NAME = "wiki/Validation Reports/Validation Report VectorCAST 2026 SP3"
DOC_INPUT_HEADING = "Known Issues" #currently it has to be a heading

PROJECT_ID = 'TOV'  # e.g., 'MYPROJECT', 'Python'

ISSUE_MARKER_BEG = "[["
ISSUE_MARKER_END = "]]"

ISSUE_INPUT_FILE = RISK_ASSESSMENT_OUTPUT_FILE



