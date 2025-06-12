"""Groq LLM provider implementation."""
import json
from typing import Dict, Any

import requests

from ..base import BaseLLM, register
from ...core.config import get_api_key, get_config_value
from ...core.errors import LLMError
from ...core.logging import get_logger

logger = get_logger("llm.groq")

@register("groq")
class GroqLLM(BaseLLM):
    """Groq LLM provider."""
    
    def __init__(self, model: str, **kwargs):
        super().__init__(model, **kwargs)
        self.api_key = get_api_key("groq")
        if not self.api_key:
            logger.error("GROQ_API_KEY not found in environment or config")
            raise LLMError("GROQ_API_KEY not found in environment or config")
        
        self.api_url = get_config_value('llm.providers.groq.api_url')
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Groq API."""
        messages = [{"role": "user", "content": prompt}]
        
        data = {
            "model": self.model,
            "messages": messages,
            **kwargs
        }
        
        logger.info(f"Calling Groq API with model={self.model}")
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            logger.info("Groq API call successful")
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise LLMError(f"Groq API error: {str(e)}") 