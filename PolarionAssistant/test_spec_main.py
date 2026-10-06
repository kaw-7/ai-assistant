from TestSpec.TestCaseBuilder import TestCaseBuilder
import TestSpec.testspec_config as ts_conf

import traceback
import time
import sys

if __name__ == "__main__":
    start = time.perf_counter()
    try:
        if ts_conf.CREATE_TEST_SPEC.lower() == "y" and ts_conf.DEBUG.lower() == "n":
            from TestSpec.TestSpecBuilder import TestSpecBuilder
            builder = TestSpecBuilder()
            builder.createFinalDoc()
        if ts_conf.CREATE_TEST_SPEC.lower() == "y" and ts_conf.DEBUG.lower() == "y":
            from TestSpec.TestSpecDebugger import TestSpecDebugger
            testSpec_debugger = TestSpecDebugger()
            testSpec_debugger.PrintDocDetails()
            
        if ts_conf.DEBUG.lower() == "n":
                builder = TestCaseBuilder()
                builder.MoveTestCases()
        else:
            from TestSpec.TestCaseDebugger import TestCaseDebugger
            test_case_debugger = TestCaseDebugger()
            test_case_debugger.PrintDocDetails()


    except Exception:
        full_error = traceback.format_exc()
        print(f"❌ Error during Test specification creation: {full_error}")
        sys.exit(1)
    
    total = time.perf_counter() - start
    print(f"⏱️ Total working time for the test specification polarion assistant: {total:.3f} seconds")
    
    
