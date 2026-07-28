from abc import ABC, abstractmethod
from enum import Enum
import config
import os


class PreprocessorType(Enum):
    AI = "AI"
    IAR_EmbeddedWorkbench = "IAR_EmbeddedWorkbench"
    RELOAD = "Reload_Existing"
    
class AbstractPreprocessor(ABC):
    """The 'Contract'. Any Preprocessor must have these methods."""

    @abstractmethod
    def preprocess_file(self, release_notes_file_path: str) -> str:
        pass

    def save_output(self, ai_response, file_path, opts="w"):
        folder_path = os.path.dirname(file_path)
        if folder_path:  # Check to make sure we aren't just writing to the root
            os.makedirs(folder_path, exist_ok=True)
        with open(file_path, opts, encoding="utf-8") as f:
            f.write(ai_response)
    
    def check_characters(self, release_notes: str):
        pos = release_notes.find("\x00")
        if pos != -1:
            print("first NUL at:", pos)
        flag = any(ord(c) < 32 and c not in "\r\n\t" for c in release_notes)
        if flag:
            print(f"has non-printable: {flag}")