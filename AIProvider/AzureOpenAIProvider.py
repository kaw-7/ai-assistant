import os
from typing_extensions import override
from dotenv import load_dotenv, find_dotenv
from openai import AzureOpenAI
import httpx

from AIProvider.AIProvider import AIProvider
from AIProvider.AIContext import AIContext
import config

class AzureOpenAIProvider(AIProvider, AIContext):
    def __init__(self):
        key = self._get_key_from_env()
        api_version = "2024-12-01-preview"
        endpoint = "https://toolvaldationaianalyser.openai.azure.com/"
        self.client = AzureOpenAI(
            api_version=api_version,
            azure_endpoint=endpoint,
            api_key=key
        ) #"gpt-5.4-mini"
        self.context = ""

    @override
    def generate_response(self, user_input: str) -> str:
        self.save_question(user_input)
        
        granular_timeout = httpx.Timeout(
            timeout=600.0,  # Total maximum time
            connect=5.0,   # Max time to establish connection
            read=450.0,     # Max time to wait for the next chunk of data
            write=20.0     # Max time to send the request
        )
        response = self.client.with_options(timeout=granular_timeout).chat.completions.create(
            model="gpt-5.4-mini",  # e.g., "llama-3.1-sonar-large-128k-online" config.MODEL_NAME
            messages=[{"role": "user", "content": user_input}],
            reasoning_effort="high",
            stream=False
        )
        self._print_token_usage(response)

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

    # Retrieve the API key safely from the environment
    def _get_key_from_env(self):
        load_dotenv(find_dotenv())  # Load environment variables
        my_api_key = os.getenv("AZURE_API_KEY")  # Get OpenAI API key from .env
        if not my_api_key:
            raise ValueError("API Key not found. Please check your .env file.")
        return my_api_key
    
    def _print_token_usage(self, response):
        usage = response.usage  # Usage object (if provided by the API)

        context_tokens = usage.prompt_tokens       # input token
        output_tokens  = usage.completion_tokens   # output tokens
        print("context_tokens:", context_tokens)
        print("output_tokens:", output_tokens)