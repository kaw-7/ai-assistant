import sys
import config
from AIProvider.GeminiProvider import GeminiProvider
from Preprocessor.AbstractPreprocessor import PreprocessorType 
from Preprocessor.AIPreprocessor import AIPreprocessor 
from Preprocessor.IAREWPreprocessor import IAREWPreprocessor
from Preprocessor.ReloadExistingPreprocessor import ReloadExistingPreprocessor
from RiskAssessment.AIRiskAssessmentAgent import AIRiskAssessmentAgent
from RiskAssessment.AIRiskSummary import AIRiskSummary
from PolarionAssistant.Polarion import polarionImport
# import csv_to_xlsx
import time

#"D:/archive/reviews_ISO62304/Microchip/XC16Toolchain/Release Notes for MPLAB XC16 C Compiler v2.10_bug_fixes.htm"
#D:/archive/reviews_ISO62304/IAR/intput_IAREmbdWorkbench.txt
def AskUser(question):
    while True:
        line = input(question + " - Y/N (y/n):")
        if line.lower() == "y":
            return True
            
        if line.lower() == "n":  
            return False
        
def ai_engine():
    if(AskUser("Skip entire AI procedure")):
        return
    release_notes_file_path = config.TOOL_RELEASE_NOTES
    ai_provider = GeminiProvider()
    
    match PreprocessorType(config.TOOL_PREPROCESSOR):
        case PreprocessorType.IAR_EmbeddedWorkbench:
            preprocessor = IAREWPreprocessor()
        case PreprocessorType.RELOAD:
            preprocessor = ReloadExistingPreprocessor(ai_provider)
        case _:
            preprocessor = AIPreprocessor(ai_provider)
            
    structured_issues = preprocessor.preprocess_file(release_notes_file_path)
    # print(structured_issues)
    # sys.exit()
    if(not AskUser("Proceed with AI risk assessment")):
        return
    ai_processor = AIRiskAssessmentAgent(ai_provider)
    ai_processor.process_issues(input_data_content=structured_issues)
    
    # ai_summary = AIRiskSummary(ai_provider)
    # ai_summary.generate_summary()

   
if __name__ == "__main__":
    
    ai_start = time.perf_counter()
    ai_engine()
    ai_total = time.perf_counter() - ai_start
    print(f"⏱️ AI time to complete: {(ai_total):.3f} seconds")
    
    if(not AskUser("Proceed with polarion import")):
        sys.exit(0)
    
    polarion_start = time.perf_counter()
    polarionImport()
    polarion_total = time.perf_counter() - polarion_start
       

    print(f"⏱️ Total PROGRAM (polarion + ai) time: {(ai_total + polarion_total):.3f} seconds")
    #csv_to_xlsx.convert()
    
