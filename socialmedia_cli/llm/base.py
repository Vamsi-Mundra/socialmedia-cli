"""Base LLM abstraction layer."""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Type

_REGISTRY: Dict[str, Type['BaseLLM']] = {}

class BaseLLM(ABC):
    """Base class for LLM providers."""
    
    def __init__(self, model: str, **kwargs):
        self.model = model
        self.kwargs = kwargs
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt."""
        pass
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate text from a chat history."""
        # Default implementation converts chat to prompt
        prompt = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
        return self.generate(prompt, **kwargs)

def register(name: str):
    """Decorator to register an LLM provider."""
    def decorator(cls: Type[BaseLLM]) -> Type[BaseLLM]:
        _REGISTRY[name] = cls
        return cls
    return decorator

def get_client(provider: str, model: str, **kwargs) -> BaseLLM:
    """Get an LLM client instance."""
    if provider not in _REGISTRY:
        raise ValueError(f"Unknown LLM provider: {provider}")
    return _REGISTRY[provider](model=model, **kwargs) 