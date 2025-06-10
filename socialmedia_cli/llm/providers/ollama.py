"""Ollama LLM provider implementation."""
import subprocess
from typing import Dict, Any

from ..base import BaseLLM, register
from ...core.errors import LLMError
from ...core.logging import get_logger

logger = get_logger("llm.ollama")

@register("ollama")
class OllamaLLM(BaseLLM):
    """Ollama LLM provider."""
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Ollama CLI."""
        logger.info(f"Calling Ollama CLI with model={self.model}")
        try:
            result = subprocess.run(
                ["ollama", "run", self.model, prompt],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info("Ollama CLI call successful")
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Ollama error: {e.stderr}")
            raise LLMError(f"Ollama error: {e.stderr}")
        except FileNotFoundError:
            logger.error("Ollama CLI not found. Please install it first.")
            raise LLMError("Ollama CLI not found. Please install it first.") 