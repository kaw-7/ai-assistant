from ValidReport.ValidReportBuilder import ValidReportBuilder

import traceback
import sys

if __name__ == "__main__":
    try:
        builder = ValidReportBuilder()
        builder.createFinalDoc()
    except Exception:
        full_error = traceback.format_exc()
        print(f"❌ Error during Test specification creation: {full_error}")
        sys.exit(1)# -*- coding: utf-8 -*-

