"""
LLM module for LLM Judge Framework.
Contains clients for interacting with various LLM providers.
"""

from src.llm.openai_client import OpenAIClient
from src.llm.azure_openai_client import AzureOpenAIClient
from src.utils.logger import Logger

__all__ = [
    'OpenAIClient',
    'AzureOpenAIClient'
]