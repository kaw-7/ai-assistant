import sys
import traceback
from typing_extensions import override

from Preprocessor.AbstractPreprocessor import AbstractPreprocessor
import config


class ReloadExistingPreprocessor(AbstractPreprocessor):
    
    def __init__(self, ai_provider):
        self.ai_engine = ai_provider
        
    @override
    def preprocess_file(self, release_notes_file_path):
        try:
            with open(config.TEMP_OUTPUT_FILE, "r", encoding="utf-8", errors="replace") as f:
                ai_response = f.read()
            
            return ai_response
        except Exception:
            print(f"\n[ERROR] An error during reload of existing issues occurred:\n{traceback.format_exc()}")
            sys.exit()