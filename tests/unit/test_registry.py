"""Unit tests for LLM registry."""
import pytest

from socialmedia_cli.llm.base import BaseLLM, register, get_client

class FakeLLM(BaseLLM):
    """Fake LLM for testing."""
    def generate(self, prompt: str, **kwargs) -> str:
        return "fake response"

def test_register_and_get_client():
    """Test registering and getting an LLM client."""
    # Register fake provider
    register("fake")(FakeLLM)
    
    # Get client
    client = get_client("fake", "test-model")
    
    # Verify
    assert isinstance(client, FakeLLM)
    assert client.model == "test-model"
    assert client.generate("test") == "fake response"

def test_unknown_provider():
    """Test getting an unknown provider."""
    with pytest.raises(ValueError, match="Unknown LLM provider"):
        get_client("unknown", "test-model") 