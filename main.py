import sys
import config
from AIProvider.GeminiProvider import GeminiProvider
from AIProvider.AzureOpenAIProvider import AzureOpenAIProvider
from Preprocessor.AbstractPreprocessor import PreprocessorType 
from Preprocessor.AIPreprocessor import AIPreprocessor 
from Preprocessor.IAREWPreprocessor import IAREWPreprocessor
from Preprocessor.ReloadExistingPreprocessor import ReloadExistingPreprocessor
from Preprocessor.PreprocessingPipeline import PreprocessingPipeline
from Preprocessor.TextChunkerPreprocessor import TextChunkerPreprocessor
from RiskAssessment.AIRiskAssessmentAgent import AIRiskAssessmentAgent
from RiskAssessment.AIRiskSummary import AIRiskSummary
from PolarionAssistant.PolarionIssueImporter import PolarionIssueImporter
# import csv_to_xlsx
import time
from UI.IssueFormatter import formatIssues
from UI.App import App

#"D:/archive/reviews_ISO62304/Microchip/XC16Toolchain/Release Notes for MPLAB XC16 C Compiler v2.10_bug_fixes.htm"
#D:/archive/reviews_ISO62304/IAR/intput_IAREmbdWorkbench.txt

# TO DO create a UI module with a predefined UI inteface e.g. with AskUser metod
def AskUser(question, answer=None):
    if(type(answer) is str and answer.lower() == "y"):
        return True
    if(type(answer) is str and answer.lower() == "n"):
        return False

    while True:
        line = input(question + " - Y/N (y/n):")
        if line.lower() == "y":
            return True
            
        if line.lower() == "n":  
            return False
        
def ai_engine():
    if(AskUser("Skip entire AI procedure", config.SKIP_ENTIRE_AI)):
        return
    
    # todo: create an AI factory class for the ai_provider variable
    ai_provider = GeminiProvider() #GeminiProvider() AzureOpenAIProvider()
    
    match PreprocessorType(config.TOOL_PREPROCESSOR):
        case PreprocessorType.IAR_EmbeddedWorkbench:
            preprocessor = IAREWPreprocessor()
        case PreprocessorType.RELOAD:
            preprocessor = ReloadExistingPreprocessor(ai_provider)
        case _:
            preprocessor = AIPreprocessor(ai_provider)
    
    preprocessorPipeline = PreprocessingPipeline(TextChunkerPreprocessor(ai_provider), preprocessor)
    preprocessorPipeline.Start()
    # structured_issues = preprocessor.preprocess_file(release_notes_file_path)
    with open(config.TEMP_OUTPUT_FILE, mode="r", encoding="utf-8") as f:
        structured_issues = f.read()
    # print(structured_issues)
    # sys.exit()
    if(not AskUser("Proceed with AI risk assessment", config.PROCEED_WITH_AI_RISK_ASSESSMENT)):
        return
    ai_processor = AIRiskAssessmentAgent(ai_provider)
    ai_processor.process_issues(input_data_content=structured_issues)
    
    #ai_summary = AIRiskSummary(ai_provider)
    #ai_summary.generate_summary()

   
if __name__ == "__main__":
    
    ai_start = time.perf_counter()
    ai_engine()
    ai_total = time.perf_counter() - ai_start
    print(f"⏱️ AI time to complete: {(ai_total):.3f} seconds")
    
    file_path = config.TEMP_OUTPUT_FILE
    if config.PROCEED_WITH_AI_RISK_ASSESSMENT.lower() == "y":
        file_path = config.RISK_ASSESSMENT_OUTPUT_FILE
        
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
        issuesForDisplay = formatIssues(text)
        app = App(issuesForDisplay)
        app.mainloop()
        
    if(not AskUser("Proceed with polarion import")):
        sys.exit(0)
    
    polarion_start = time.perf_counter()    
    importer = PolarionIssueImporter()
    importer.ImportIssuesInPolarion()
    polarion_total = time.perf_counter() - polarion_start
    
    print(f"⏱️ Total PROGRAM (polarion + ai) time: {(ai_total + polarion_total):.3f} seconds")
    #csv_to_xlsx.convert()
    
