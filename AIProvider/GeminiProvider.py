import config
import os
from google import genai
from typing_extensions import override
from dotenv import load_dotenv, find_dotenv

from AIProvider.AIProvider import AIProvider
from AIProvider.AIContext import AIContext


class GeminiProvider(AIProvider, AIContext):
    def __init__(self):
        key = self._get_key_from_env()
        self.client = genai.Client(api_key=key)
        self.context = ""

    @override
    def generate_response(self, user_input: str) -> str:
        self.client.models
        response = self.client.models.generate_content(
            model=config.MODEL_NAME,
            contents=user_input,
        )

        self.save_question(user_input)
        self.save_response(response.text)
        return response.text

    @override
    def save_question(self, question_to_ai: str):
        self.context +=   "============= User Question: =============\n"
        self.context += question_to_ai
        self.context += "\n============= User Question end ==========\n"

    @override
    def save_response(self, ai_response: str):
        self.context +=   "============= AI Response: ===============\n"
        self.context += ai_response
        self.context += "\n============= AI Response end ============\n"

    @override
    def retrieve_context(self) -> str:
        return self.context

    # Retrieve the key safely from the environment
    def _get_key_from_env(self):
        # Load the environment variables right here
        load_dotenv(find_dotenv())
        # retrieve the key
        my_api_key = os.getenv("GEMINI_API_KEY")
        # Check if key was found (good for debugging)
        if not my_api_key:
            raise ValueError("API Key not found. Please check your .env file.")

        return my_api_key