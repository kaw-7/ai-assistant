from TestSpec.TestCaseBuilder import TestCaseBuilder
from TestSpec.TestSpecBuilder import TestSpecBuilder
from TestSpec.TestCaseDebugger import TestCaseDebugger
from TestSpec.TestSpecDebugger import TestSpecDebugger

import traceback
import sys

if __name__ == "__main__":
    try:
    #    debugger = TestSpecDebugger()
    #    debugger.PrintDocDetails()
    #    testspec_builder = TestSpecBuilder()
    #    testspec_builder.createFinalDoc()
        builder = TestCaseBuilder()
        builder.MoveTestCases()
    except Exception:
        full_error = traceback.format_exc()
        print(f"❌ Error during Test specification creation: {full_error}")
        sys.exit(1)
    
    
