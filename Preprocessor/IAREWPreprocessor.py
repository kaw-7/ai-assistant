import csv
import re
import sys
from typing_extensions import override
import traceback

from Preprocessor.AbstractPreprocessor import AbstractPreprocessor
import config

#D:/archive/reviews_ISO62304/IAR/intput_IAREmbdWorkbench.txt
class IAREWPreprocessor(AbstractPreprocessor):

    @override
    def preprocess_file(self, release_notes_file_path):
        print('[1/3] Generating CSV with IAR EW automation script!')
        try:
            return parse_txt_to_csv(txt_file=release_notes_file_path,
                             input_csv=config.CSV_TEMPLATE,
                             output_csv=config.TEMP_OUTPUT_FILE,
                             risk_assesment="to do")
        except Exception:
            print(f"\n[ERROR] An error occurred during csv generation:\n{traceback.format_exc()}")
            sys.exit()

defect_id_regex = re.compile(r"^IDE-\d+")
# defect_id_regex = re.compile(r"Version\s+\d+\.\d+\.\d+\s+IDE-\d+")
# defect_id_regex = re.compile(r"TPB-\d+")
# defect_id_regex = re.compile(r"(^\[TPB-\d+|^\[EWRX-\d+)")


def parse_txt_to_csv(txt_file, input_csv, output_csv, risk_assesment=""):
    # Read the template row from input CSV
    with open(input_csv, 'r', newline='') as fin:
        reader = csv.DictReader(fin)
        template_row = next(reader)
        fieldnames = reader.fieldnames

    # Parse the text file
    rows = []
    with open(txt_file, 'r', encoding='utf-8') as txtin:
        defect_description = ""
        id = ""
        new_id = ""
        for line in txtin:
            stripped = line.strip()
            if (stripped.startswith("- ")):
                continue
            ids = defect_id_regex.findall(stripped)
            if ids:
                idx = stripped.find(']')
                new_id = stripped[stripped.find('[') + 1:idx]

                if (len(id) > 0):
                    row = template_row.copy()
                    row["Defect ID"] = id
                    row["Defect Description"] = defect_description.strip()
                    if (len(risk_assesment) > 0):
                        row["Risk Assessment"] = risk_assesment
                    row["Status"] = "to do"
                    row["Author"] = config.AUTHOR_NAME
                    rows.append(row)
                    defect_description = ""

                id = new_id
                new_id = ""

                if (len(stripped) > idx + 1 and len(stripped[(idx + 1):].strip()) > 0):
                    defect_description = stripped[(idx + 1):].strip()
                else:
                    defect_description = ""

            elif stripped:
                defect_description += (stripped + " ")
        # Add final defect(s)
        if id and defect_description:
            row = template_row.copy()
            row["Defect ID"] = id
            row["Defect Description"] = defect_description.strip()
            if (len(risk_assesment) > 0):
                row["Risk Assessment"] = risk_assesment
            rows.append(row)

    # Write to CSV
    with open(output_csv, 'w', newline='') as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    csv_string = ""
    for row in rows:
        row = ", ".join(f"\"{v}\"" for k, v in row.items())
        csv_string += row + "\n"
    return csv_string

