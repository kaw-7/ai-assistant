from abc import ABC, abstractmethod
from enum import Enum
import config
import os


class PreprocessorType(Enum):
    AI = "AI"
    IAR_EmbeddedWorkbench = "IAR_EmbeddedWorkbench"
    
class AbstractPreprocessor(ABC):
    """The 'Contract'. Any Preprocessor must have these methods."""

    @abstractmethod
    def preprocess_file(self, release_notes_file_path: str) -> str:
        pass

    def save_output(self, ai_response, file_path):
        folder_path = os.path.dirname(file_path)
        if folder_path:  # Check to make sure we aren't just writing to the root
            os.makedirs(folder_path, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(ai_response)