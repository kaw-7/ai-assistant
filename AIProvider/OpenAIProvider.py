import os
import sys
import openai
from dotenv import load_dotenv, find_dotenv
from typing_extensions import override
from AIProvider.AIProvider import AIProvider
from AIProvider.AIContext import AIContext

import config

class OpenAIProvider(AIProvider, AIContext):
    def __init__(self):
        key = self._get_key_from_env()
        openai.api_key = key
        self.context = ""

    @override
    def generate_response(self, user_input: str) -> str:
        try:
            self.save_question(user_input)
            # Request completion from OpenAI API (you can modify the model and other parameters as needed)
            response = openai.completions.create(
                model=config.MODEL_NAME,  # Ensure the model name is defined in config
                prompt=user_input
            )
            ai_response = response.choices[0].text.strip()

            # Save the response
            self.save_response(ai_response)

            return ai_response

        except openai.OpenAIError as e:
            print(f"OpenAIError error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            sys.exit(1)

    @override
    def save_question(self, question_to_ai: str):
        self.context += "============= User Question: =============\n"
        self.context += question_to_ai
        self.context += "\n============= User Question end ==========\n"

    @override
    def save_response(self, ai_response: str):
        self.context += "============= AI Response: ===============\n"
        self.context += ai_response
        self.context += "\n============= AI Response end ============\n"

    @override
    def retrieve_context(self) -> str:
        return self.context

    # Retrieve the API key safely from the environment
    def _get_key_from_env(self):
        load_dotenv(find_dotenv())  # Load environment variables
        my_api_key = os.getenv("OPENAI_API_KEY")  # Get OpenAI API key from .env
        if not my_api_key:
            raise ValueError("API Key not found. Please check your .env file.")
        return my_api_key