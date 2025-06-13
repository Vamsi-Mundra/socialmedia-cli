"""LLM module initialization."""
from .base import get_client, register, BaseLLM
from .providers.openai import OpenAILLM

__all__ = ['get_client', 'register', 'BaseLLM', 'OpenAILLM']
