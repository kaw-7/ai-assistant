import os
import sys
from typing_extensions import override
import traceback

from RiskAssessment.AbstractRiskAssessmentAgent import AbstractRiskAssessmentAgent
import config

class AIRiskAssessmentAgent(AbstractRiskAssessmentAgent):
    
    def __init__(self, ai_provider):
        self.ai_engine = ai_provider
    
    @override
    def process_issues(self, input_data_content):
        """
        Main method to execute the risk assessment step.
        """
        try:
            with open(config.RISK_ASSESSMENT_OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write("") # File is now EMPTY (0 bytes)
                
            print(f"\n Processing issues by count of {config.MAX_COUNT_OF_ISSUES_PROCESSED_AT_ONCE_BY_AI}.")
            
            
            pos = 0
            while(True):
                (pos, input_data_content_partial) = self._get_up_to_nth(
                    input_data_content, 
                    config.ISSUE_END_MARKER, 
                    config.MAX_COUNT_OF_ISSUES_PROCESSED_AT_ONCE_BY_AI, 
                    pos)
                if(input_data_content_partial is None):
                    break
                self._process_issues_partial(input_data_content_partial)
                if(pos == -1 or pos >= len(input_data_content)):
                    break
                
            print(f"\n[2/3] Risk Assessment Complete. Saved to: {config.RISK_ASSESSMENT_OUTPUT_FILE}\n")

        except Exception:
            print(f"\n[ERROR] Pre-Partitioning during risk assessment failed:\n{traceback.format_exc()}")
            sys.exit()
    
    def _process_issues_partial(self, input_data_content):
        """
        Main method to execute the risk assessment step.
        """
        try:
            # Prepare the massive prompt
            user_input = self._generate_input(input_data_content)
            if not user_input:
                print("\n[ERROR] Generation of user input failed!")
                sys.exit()  # Stop if generation failed

            print("Partial Risk Assessment Input generated successfully.")
            print("Sending to Gemini for analysis...")

            # Call AI
            ai_response = self.ai_engine.generate_response(user_input=user_input)

            # Save Output (final_risk_report.txt)
            with open(config.RISK_ASSESSMENT_OUTPUT_FILE, "a", encoding="utf-8") as f:
                f.write(ai_response)

        except Exception:
            print(f"\n[ERROR] Risk Assessment failed:\n{traceback.format_exc()}")
            sys.exit()
            
    def _generate_input(self, input_data_content):
        """
        Combines Instructions, Reference CSVs, and the Input CSV into one prompt.
        """
        user_input = ""
        print("\nPreparing Risk Assessment Context...")

        try:
            # --- CHECK FILES EXISTENCE ---
            # List of files to check before proceeding
            required_files = [
                (config.RISK_INSTRUCTIONS_PATH, "Instructions"),
                (config.REF_PATH, "Reference"),
            ]

            for path, name in required_files:
                if not os.path.exists(path):
                    print(f"[ERROR] {name} file not found at: {path}")
                    return ""

            # --- READ FILES ---
            # We use errors="replace" to be safe with unknown characters in CSVs

            # A. Instructions
            with open(config.RISK_INSTRUCTIONS_PATH, "r", encoding="utf-8") as f:
                instructions_text = f.read()

            # C. Reference File 2 (VC25)
            with open(config.REF_PATH, "r", encoding="utf-8", errors="replace") as f:
                ref_content = f.read()

            # --- CONSTRUCT PROMPT ---
            user_input = (
                f"{instructions_text}\n\n"

                f"--- REFERENCE FILE: {config.REF_PATH} ---\n"
                f"{ref_content}\n"
                f"--- END OF REFERENCE FILE ---\n\n"

                f"--- INPUT DATA STARTS HERE ---\n"
                f"{input_data_content}\n"
                f"--- INPUT DATA ENDS HERE ---"
            )

        except Exception:
            print(f"\n[ERROR] An error occurred during input generation:\n{traceback.format_exc()}")
            return ""

        return user_input
    
    def _get_up_to_nth(self, text, substring, n, start):
        """Get substring up to nth occurrence, or whole string from start if <n occurrences."""
        if(start >= len(text)):
            return (-1, "")
        cur_pos = start
        for i in range(n):
            cur_pos = text.find(substring, cur_pos)
            if cur_pos == -1:
                return (-1, text[start:])  # Not enough occurrences - return whole string
            cur_pos += len(substring)

        # Found nth occurrence, slice up to it
        return (cur_pos, text[start:cur_pos])