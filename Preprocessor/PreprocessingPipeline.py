from Preprocessor.AIPreprocessor import AIPreprocessor
from Preprocessor.TextChunkerPreprocessor import TextChunkerPreprocessor
import shutil

import config

class PreprocessingPipeline:
    def __init__(self, chunk_preprocessor: TextChunkerPreprocessor, ai_preprocessor: AIPreprocessor):
        self.chunk_preprocessor = chunk_preprocessor
        self.ai_preprocessor = ai_preprocessor
        self.structured_issues = ""
        
    def Start(self):
                    
        with open(config.TEMP_OUTPUT_FILE, mode="w", encoding="utf-8") as f:
            f.write("")
        
        if config.USE_PREPROCESS_CHUNKING.lower() == "n":
            self.structured_issues = self.ai_preprocessor.preprocess_file(config.TOOL_RELEASE_NOTES)
            return
        #else:
        shutil.copyfile(config.TOOL_RELEASE_NOTES, config.TEMP_REL_NOTES)
        with open(config.TEMP_CHUNK_FILE, "w", encoding='utf-8') as f:
            f.write("")
            
        while True:
            self.chunk_preprocessor.preprocess_file(config.TEMP_REL_NOTES)
            self.structured_issues += "\r\n"
            self.structured_issues += self.ai_preprocessor.preprocess_file(config.TEMP_CHUNK_FILE)
            if(self.chunk_preprocessor.End()):
                break
    
    def getIssues(self):
        return self.structured_issues
            