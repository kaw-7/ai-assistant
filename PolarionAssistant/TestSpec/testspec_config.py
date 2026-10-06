# Test specification config - document creation and test cases import

# --- STEPS run by test_spec_main.py ('y' / 'n') ---
CREATE_TEST_SPEC = 'y'  # create the test spec document from the template
DEBUG = 'n'# do not modify in polarion- only display document info

TOOL_NAME = "Emulator Framework"
TARGET_TITLE = f"Test Specification to {TOOL_NAME}"
TARGET_NAME_ID = TARGET_TITLE.replace('.', '_')


PLAN_DOCU = f"wiki/Validation Plans/Validation Plan {TOOL_NAME.replace('.', '_')}"
TARGET_LOCATION = "Testing"
TEST_DOCU = f"wiki/{TARGET_LOCATION}/{TARGET_NAME_ID}"
TEST_SPEC_TEMPLATE = f'wiki/{TARGET_LOCATION}/_Template Tool Requirement Test Specification _Toolname_'

PROJECT_ID = 'TOV'
DOC_INPUT_HEADING = "Requirements to the Operational Qualification"

# TARGET_PROJECT_ID = "ToolValidation"

LINK_ROLE = None

PLACEHOLDER = r'<span style="color: #FF0000;">[toolname]</span>'
PLACEHOLDER_DOCSTATUS = r'<Toolname> <Version>'
VALI_PLAN_EXCLUDED_HEADINGS = {"Requirements to the Installation", "Requirements to the Performance Qualification"}