# the importer uses 'PolarionAssistant.*' imports - needs the project root on sys.path
from PolarionAssistant.ValidReport.PolarionIssueImporter import PolarionIssueImporter

import argparse
import traceback
import time
import sys

REPORT_TYPES = ("initial", "periodic")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Create a Polarion report document and import the issues into it.")
    parser.add_argument("report", nargs="?", default="initial", choices=REPORT_TYPES,
                        help="the report document to work on (default: initial)")
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    print(f"Report: {args.report}")
    if args.report == REPORT_TYPES[0]:
        import PolarionAssistant.ValidReport.valid_report_config as doc_conf
    elif args.report == REPORT_TYPES[1]:
        import PolarionAssistant.ValidReport.periodic_review_config as doc_conf
    else:
        raise("Import doc configuration error!")
    start = time.perf_counter()
    try:
        if doc_conf.BUILD_VALID_REPORT.lower() == "y":
            from ValidReport.ValidReportBuilder import ValidReportBuilder
            builder = ValidReportBuilder(doc_conf)
            builder.createFinalDoc()

        importer = PolarionIssueImporter(doc_conf)
        importer.ImportIssuesInPolarion()
    except Exception:
        full_error = traceback.format_exc()
        print(f"❌ Error during Validation report creation: {full_error}")
        sys.exit(1)

    total = time.perf_counter() - start
    print(f"⏱️ Total working time for the polarion assistant: {total:.3f} seconds")
