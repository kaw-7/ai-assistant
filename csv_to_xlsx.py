import io
import pandas as pd
from pathlib import Path

import config
def strip_csv():
    try:
        csv_string = ""
        found = False
        with open(config.RISK_ASSESSMENT_OUTPUT_FILE, 'r+', encoding='utf-8') as txtin:
            for line in txtin:
                if(found == True and (line.find(config.AUTHOR_NAME, 0, len(config.AUTHOR_NAME)+1) == -1)):
                    break
                if((line.find(config.FIRST_CSV_COLUMN,0) != -1) or found):
                    csv_string += line
                    found = True

        # print(csv_string)
        return csv_string
        
    except Exception as e:
        print(f"\n[ERROR] An error occurred during csv strip:\n{e}")
        return ""
        
# Reading the csv file
def convert():
    stripped_csv = strip_csv()
    if(not stripped_csv):
        print("\nFailed to strip the csv, no xlsx will be produced!")
        return
    
    try:        
        df_new = pd.read_csv(stripped_csv)
        # saving xlsx file
        filepath = Path(config.RISK_ASSESSMENT_OUTPUT_FILE)
        new_path = filepath.with_suffix(".xlsx")
        # print(new_path)  # example.md
        excelWriter = pd.ExcelWriter(new_path)
        df_new.to_excel(excelWriter, index=False)
        
        excelWriter.close()
    except Exception as e:
        print(f"\n[ERROR] An error occurred during csv to xlsx conversion:\n{e}")

# convert()
