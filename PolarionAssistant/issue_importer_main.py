import sys
import config
from PolarionAssistant.PolarionIssueImporter import PolarionIssueImporter
# import csv_to_xlsx
import time

   
if __name__ == "__main__":
    
    polarion_start = time.perf_counter()    
    importer = PolarionIssueImporter()
    importer.ImportIssuesInPolarion()
    polarion_total = time.perf_counter() - polarion_start
    
    print(f"⏱️ Total working time for the polarion assistant: {(polarion_total):.3f} seconds")
    #csv_to_xlsx.convert()
    
