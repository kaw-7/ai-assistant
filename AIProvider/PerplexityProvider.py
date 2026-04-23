import os
import config
from typing_extensions import override
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
from AIProvider.AIProvider import AIProvider
from AIProvider.AIContext import AIContext

class PerplexityProvider(AIProvider, AIContext):
    def __init__(self):
        key = self._get_key_from_env()
        # Perplexity API uses OpenAI-compatible client
        self.client = OpenAI(
            api_key=key,
            base_url="https://api.perplexity.ai"
        )
        self.context = ""

    @override
    def generate_response(self, user_input: str) -> str:
        self.save_question(user_input)
        
        response = self.client.chat.completions.create(
            model=config.MODEL_NAME,  # e.g., "llama-3.1-sonar-large-128k-online"
            messages=[{"role": "user", "content": user_input}],
            stream=False
        )
        
        response_text = response.choices[0].message.content
        
        self.save_response(response_text)
        return response_text

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

    def _get_key_from_env(self):
        load_dotenv(find_dotenv())
        my_api_key = os.getenv("PERPLEXITY_API_KEY")  # Note: different env var name
        if not my_api_key:
            raise ValueError("Perplexity API Key not found. Please check your .env file for PERPLEXITY_API_KEY.")
        return my_api_key
