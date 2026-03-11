import sys
import config
from AIProvider.GeminiProvider import GeminiProvider
from Preprocessor.AbstractPreprocessor import PreprocessorType 
from Preprocessor.AIPreprocessor import AIPreprocessor 
from Preprocessor.IAREWPreprocessor import IAREWPreprocessor
from RiskAssessment.AIRiskAssessmentAgent import AIRiskAssessmentAgent
from RiskAssessment.AIRiskSummary import AIRiskSummary
from PolarionAssistant.Polarion import polarionImport
import csv_to_xlsx
import time

#"D:/archive/reviews_ISO62304/Microchip/XC16Toolchain/Release Notes for MPLAB XC16 C Compiler v2.10_bug_fixes.htm"
#D:/archive/reviews_ISO62304/IAR/intput_IAREmbdWorkbench.txt

def ai_engine():
    release_notes_file_path = config.TOOL_RELEASE_NOTES
    ai_provider = GeminiProvider()

    match PreprocessorType(config.TOOL_PREPROCESSOR):
        case PreprocessorType.IAR_EmbeddedWorkbench:
            preprocessor = IAREWPreprocessor()
        case _:
            preprocessor = AIPreprocessor(ai_provider)
            
    csv_content = preprocessor.preprocess_file(release_notes_file_path)
    # print(csv_content)
    # sys.exit()
    ai_processor = AIRiskAssessmentAgent(ai_provider)
    ai_processor.process_csv(input_data_content=csv_content)
    
    ai_summary = AIRiskSummary(ai_provider)
    ai_summary.generate_summary()

if __name__ == "__main__":
    
    # ai_engine()
    start = time.perf_counter()

    while True:
        line = input("Proceed with polarion import - Y/N (y/n):")
        if line.lower() == "y":
            polarionImport()
            break
        if line.lower() == "n":  
            break

    end = time.perf_counter()
    print(f"Total program time: {(end - start):.3f} seconds")
    #csv_to_xlsx.convert()
    