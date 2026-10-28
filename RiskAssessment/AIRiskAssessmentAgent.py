import os
import sys
from typing_extensions import override
import traceback
from tqdm import tqdm
import time

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
            # to do: add possibility to start from an existing position in an existing risk assessment file
            # the open "w" have to be optional and the pos param should be properly set.
            with open(config.RISK_ASSESSMENT_OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write("") # File is now EMPTY (0 bytes)
                
            print(f"\n  Processing issues by count of {config.MAX_COUNT_OF_ISSUES_PROCESSED_AT_ONCE_BY_AI}.")
            print("\n  [Loop] Generating Partial Risk Assessment Input and sending to AI for analysis....:")
            
            pos = 0
            total_n = self._get_total_occurances(input_data_content, config.ISSUE_END_MARKER)
            t = tqdm(total=total_n, desc="    ")
            t.update(pos)
            while(True):
                (pos, input_data_content_partial) = self._get_up_to_nth(
                    input_data_content, 
                    config.ISSUE_END_MARKER, 
                    config.MAX_COUNT_OF_ISSUES_PROCESSED_AT_ONCE_BY_AI, 
                    pos)
                
                t.update(config.MAX_COUNT_OF_ISSUES_PROCESSED_AT_ONCE_BY_AI)
                # to do: remove this sleep after a better upper tier payment method
                time.sleep(1)
                if(input_data_content_partial is None):
                    break
                self._process_issues_in_chunks(input_data_content_partial)
                if(pos == -1 or pos >= len(input_data_content)):
                    break
            t.close()
            print(f"\n✅ [2/2] Risk Assessment Complete and saved to: {config.RISK_ASSESSMENT_OUTPUT_FILE}\n")

        except Exception:
            print(f"\n❌ [ERROR] Pre-Partitioning during risk assessment failed:\n{traceback.format_exc()}")
            sys.exit(1)
    
    def _process_issues_in_chunks(self, input_data_content):
        """
        Main method to execute the risk assessment step.
        """
        try:
            # Prepare the massive prompt
            user_input = self._generate_input(input_data_content)
            if not user_input:
                print("\n[ERROR] Generation of user input failed!")
                sys.exit(1)  # Stop if generation failed

            # Call AI
            ai_response = self.ai_engine.generate_response(user_input=user_input)

            # Save Output (final_risk_report.txt)
            with open(config.RISK_ASSESSMENT_OUTPUT_FILE, "a", encoding="utf-8") as f:
                f.write(ai_response + "\n")
                

        except Exception:
            print(f"\n❌ [ERROR] Risk Assessment failed:\n{traceback.format_exc()}")
            sys.exit(1)
            
    def _generate_input(self, input_data_content):
        """
        Combines Instructions, Reference CSVs, and the Input CSV into one prompt.
        """
        user_input = ""

        try:
            # --- CHECK FILES EXISTENCE ---
            # List of files to check before proceeding
            required_files = [
                (config.RISK_INSTRUCTIONS_PATH, "Instructions"),
                (config.REF_PATH, "Reference"),
                (config.REF_PATH2_OPT, "2ndReference")
            ]

            for path, name in required_files:
                if not path and name=="2ndReference":
                    continue
                if not os.path.exists(path):
                    print(f"[ERROR] {name} file not found at: {path}")
                    return ""

            # --- READ FILES ---
            # We use errors="replace" to be safe with unknown characters in CSVs

            # A. Instructions
            with open(config.RISK_INSTRUCTIONS_PATH, "r", encoding="utf-8") as f:
                instructions_text = f.read()

            # B. Reference File
            with open(config.REF_PATH, "r", encoding="utf-8", errors="replace") as f:
                ref_content = f.read()
            
            # C. Reference File 2 (optional)
            optional_ref_input = self._create_input_for_2nd_ref()
                    
            # --- CONSTRUCT PROMPT ---
            user_input = (
                f"{instructions_text}\n\n"

                f"--- REFERENCE FILE: {config.REF_PATH} ---\n"
                f"{ref_content}\n"
                f"--- END OF REFERENCE FILE ---\n\n"
                f"{optional_ref_input}"
                
                f"--- INPUT DATA STARTS HERE ---\n"
                f"{input_data_content}\n"
                f"--- INPUT DATA ENDS HERE ---"
            )

        except Exception:
            print(f"\n❌ [ERROR] An error occurred during input generation:\n{traceback.format_exc()}")
            return ""

        return user_input
    
    def _get_up_to_nth(self, text, substring, n, start):
        """Get substring up to nth occurrence or whole string, from start if less than n occurrences."""
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
    
    def _get_total_occurances(self, text, substring):
        """Get total occurances of substring inside text."""
        if(text is None):
            return 0
        counter = 0
        cur_pos = 0
        while(True):
            cur_pos = text.find(substring, cur_pos)
            if cur_pos == -1:
                return counter
            cur_pos += len(substring)
            counter += 1
        
        raise Exception("❌ Could not find total count of issues!") 
    
    def _create_input_for_2nd_ref(self):
        optional_ref_input = ""
        if config.REF_PATH2_OPT:
            # C. Reference File 2 which is optional
            with open(config.REF_PATH2_OPT, "r", encoding="utf-8", errors="replace") as f2:
                ref_content_opt = f2.read()
                
                optional_ref_input = (
                    f"--- 2nd REFERENCE FILE: {config.REF_PATH2_OPT} ---\n"
                    f"{ref_content_opt}\n"
                    f"--- END OF 2ND REFERENCE FILE ---\n\n"
                )
        return optional_ref_input
        