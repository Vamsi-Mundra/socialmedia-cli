"""Custom exceptions for socialmedia-cli."""

class SocialMediaError(Exception):
    """Base exception for all socialmedia-cli errors."""
    pass

class ConfigError(SocialMediaError):
    """Configuration related errors."""
    pass

class LLMError(SocialMediaError):
    """LLM provider related errors."""
    pass

class CollectorError(SocialMediaError):
    """Data collection related errors."""
    pass

class WriterError(SocialMediaError):
    """Content writing related errors."""
    pass

class PipelineError(SocialMediaError):
    """Pipeline execution related errors."""
    pass 