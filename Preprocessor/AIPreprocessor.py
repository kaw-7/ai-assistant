import os
import sys
import config
import traceback
from typing_extensions import override
from string import Template

from Preprocessor.AbstractPreprocessor import AbstractPreprocessor

class AIPreprocessor(AbstractPreprocessor):
    
    def __init__(self, ai_provider):
        self.ai_engine = ai_provider
        
    @override
    def preprocess_file(self, release_notes_file_path):

        if not os.path.exists(release_notes_file_path):
            print(f"[ERROR] Input file not found: {release_notes_file_path}")
            sys.exit(1)

        try:
            user_input = self.generate_input(release_notes_file_path)
            if not user_input:
                return

            print("\nUser input was generated! Query is now running...")

            ai_response = self.ai_engine.generate_response(user_input=user_input)
            # --- SAVE OUTPUT ---
            self.save_output(ai_response, config.TEMP_OUTPUT_FILE, "a")
            print("Output saved!\n")
            
            return ai_response
        except Exception:
            print(f"\n[ERROR] An error occurred:\n{traceback.format_exc()}")
            sys.exit()

    def generate_input(self, release_notes_file_path):
        user_input = ""
        print("[1/3] Generating structured markup with AI")
        try:
            # --- PREPARE PROMPT ---
            # Read files (using 'with' ensures they close automatically)
            if not os.path.exists(config.INSTRUCTIONS_PATH):
                print(f"[ERROR] Instruction file not found: {config.INSTRUCTIONS_PATH}")
                return user_input

            with open(config.INSTRUCTIONS_PATH, "r", encoding="utf-8") as f:
                template = Template(f.read())
            with open(release_notes_file_path, "r", encoding="utf-8", errors="replace") as f:
                release_notes = f.read()
                self.check_characters(release_notes)

            instructions = template.safe_substitute(
                tool_name=config.TOOL_NAME, 
                vstart=config.TOOL_VERSION_START,
                vend=config.TOOL_VERSION_END)
            
            print("Tool name: ", config.TOOL_NAME, ", validated version: ", config.TOOL_VERSION_START,
                  ", last version: ", config.TOOL_VERSION_END)

            user_input = (
                f"{instructions}\n\n"
                f"--- START OF RELEASE NOTES ---\n"
                f"{release_notes}\n"
                f"--- END OF RELEASE NOTES ---"
            )
        except Exception:
            print(f"\n[ERROR] An error occurred:\n{traceback.format_exc()}")
            return user_input

        return user_input
