import PolarionAssistant.ValidReport.valid_report_config as vr_conf
# the importer uses 'PolarionAssistant.*' imports - needs the project root on sys.path
from PolarionAssistant.ValidReport.PolarionIssueImporter import PolarionIssueImporter

import traceback
import time
import sys

if __name__ == "__main__":
    start = time.perf_counter()
    try:
        if vr_conf.BUILD_VALID_REPORT.lower() == "y":
            from ValidReport.ValidReportBuilder import ValidReportBuilder
            builder = ValidReportBuilder()
            builder.createFinalDoc()

        importer = PolarionIssueImporter()
        importer.ImportIssuesInPolarion()
    except Exception:
        full_error = traceback.format_exc()
        print(f"❌ Error during Validation report creation: {full_error}")
        sys.exit(1)

    total = time.perf_counter() - start
    print(f"⏱️ Total working time for the polarion assistant: {total:.3f} seconds")
