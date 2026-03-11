import sys
import os
import traceback

import config

class AIRiskSummary():
    
    def __init__(self, ai_provider):
        self.ai_engine = ai_provider
        
    def generate_summary(self):
        """
        Main method to execute the risk summarization step.
        """
        try:
            print("[3/3] Generating risk summary")
            # Prepare the massive prompt
            user_input = self.generate_input(self.ai_engine.retrieve_context())
            if not user_input:
                print("\n[ERROR] [3/3] Generation of user input failed!")
                sys.exit()  # Stop if generation failed

            print("\nInput for summarization query was generated successfully.")
            print("Sending to Gemini for analysis...")

            # Call AI
            ai_response = self.ai_engine.generate_response(user_input=user_input)

            # Save Output (final_risk_report.txt)
            with open(config.RISK_SUMMARY_OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write(ai_response)
                
            # for debug: save context
            with open(config.CONTEXT_FILE, "w", encoding="utf-8") as f:
                f.write(self.ai_engine.retrieve_context())

            print(f"\n[3/3] Risk Summary Complete. Saved to: {config.RISK_SUMMARY_OUTPUT_FILE}\n")

        except Exception:
            print(f"\n[ERROR] [3/3] Risk Summary failed:\n{traceback.format_exc()}")
            sys.exit()
        
    def generate_input(self, user_context):
        """
        Combines Instructions and existing context.
        """
        user_input = ""
        print("Preparing Context for the summary...")

        try:
            # --- CHECK FILES EXISTENCE ---
            # List of files to check before proceeding
            required_files = [
                (config.RISK_SUMMARY_INSTRUCTIONS_PATH, "Instructions")
            ]

            for path, name in required_files:
                if not os.path.exists(path):
                    print(f"[ERROR] {name} file not found at: {path}")
                    return ""

            # --- READ FILES ---
            # We use errors="replace" to be safe with unknown characters in CSVs

            # A. Instructions
            with open(config.RISK_SUMMARY_INSTRUCTIONS_PATH, "r", encoding="utf-8") as f:
                instructions_text = f.read()          

            # --- CONSTRUCT PROMPT ---
            user_input = (
                f"{instructions_text}\nExectute the above instructions in the following context:\n\n"
                    
                f"--- CONTEXT: ---\n"
                f"{user_context}\n"
                f"--- END OF CONTEXT ---\n\n"
            )

        except Exception:
            print(f"\n[ERROR] An error occurred during input generation:\n{traceback.format_exc()}")
            return ""

        return user_input