
import os
import sys
from google import genai
from google.genai.errors import ClientError
from typing_extensions import override
from dotenv import load_dotenv, find_dotenv

from AIProvider.AIProvider import AIProvider
from AIProvider.AIContext import AIContext

import httpx

import config

class GeminiProvider(AIProvider, AIContext):
    def __init__(self):
        key = self._get_key_from_env()
        self.client = genai.Client(api_key=key)
        self.context = ""

    @override
    def generate_response(self, user_input: str) -> str:
        self.client.models
        try:
            
            self.save_question(user_input)
            # for debug: save context
            with open(config.CONTEXT_FILE, "w", encoding="utf-8") as f:
                f.write(self.context)
                
            response = self.client.models.generate_content(
                model= "gemini-2.5-flash", #config.MODEL_NAME,
                contents=user_input,
            )
            self.save_response(response.text)
            return response.text
        except httpx.ConnectTimeout as e:
            print(f"Connect timed out: {e}")
            sys.exit(1)
        except httpx.ReadTimeout as e:
            print(f"Read timed out: {e}")
            sys.exit(1)
        except httpx.TimeoutException as e:
            print(f"Some HTTPX timeout happened: {e}")
            sys.exit(1)
        except ClientError as e:
            print(f"Some ClientError happened: {e}")
            sys.exit(1)
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