"""Cerebras LLM provider stub."""
from ..base import BaseLLM, register
from ...core.errors import LLMError
from ...core.logging import get_logger

logger = get_logger("llm.cerebras")

@register("cerebras")
class CerebrasLLM(BaseLLM):
    """Cerebras LLM provider stub."""
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Stub implementation."""
        logger.error("Cerebras provider not implemented yet")
        raise NotImplementedError("Cerebras provider not implemented yet") 