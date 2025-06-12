"""Configuration management for socialmedia-cli."""
import os
from pathlib import Path
from typing import Optional, Any

import tomli

# Default configuration values
DEFAULT_CONFIG = {
    "auth": {
        "token_path": str(Path.home() / ".socialmedia_cli_tokens.json"),
        "token_mode": "0o600",
        "callback_port": 8000,
        "callback_url": "http://localhost:8000/callback",
        "auth_timeout": 120,
        "polling_interval": 0.1  # 100ms polling interval
    },
    "llm": {
        "default_provider": "groq",
        "default_model": "mixtral-8x7b-internet",
        "providers": {
            "groq": {
                "api_url": "https://api.groq.com/openai/v1/chat/completions"
            }
        }
    },
    "cli": {
        "default_hours": 24,
        "default_tweets": 5,
        "default_chars": 240
    },
    "paths": {
        "config_dir": str(Path.home() / ".socialmedia_cli"),
        "log_dir": str(Path.home() / ".socialmedia_cli" / "logs")
    },
    "logging": {
        "timestamp_format": "%Y-%m-%d %H:%M:%S.%f",
        "log_level": "INFO",
        "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
}

CONFIG_DIR = Path.home() / ".socialmedia_cli"
CONFIG_FILE = CONFIG_DIR / "config.toml"

def ensure_config_dir():
    """Ensure the config directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_config() -> dict:
    """Load configuration from TOML file and environment variables."""
    config = DEFAULT_CONFIG.copy()
    
    # Load from TOML if exists
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "rb") as f:
            file_config = tomli.load(f)
            # Deep merge with defaults
            for section, values in file_config.items():
                if section in config:
                    if isinstance(config[section], dict):
                        config[section].update(values)
                    else:
                        config[section] = values
                else:
                    config[section] = values
    
    # Override with environment variables
    env_prefix = "SOCIALMEDIA_CLI_"
    for key, value in os.environ.items():
        if key.startswith(env_prefix):
            config_key = key[len(env_prefix):].lower()
            # Convert value to appropriate type
            if value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
            elif value.isdigit():
                value = int(value)
            config[config_key] = value
    
    return config

def get_config_value(key_path: str, default: Any = None) -> Any:
    """Get a configuration value using dot notation."""
    config = load_config()
    keys = key_path.split('.')
    value = config
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    return value

def get_api_key(provider: str) -> Optional[str]:
    """Get API key for a specific provider."""
    config = load_config()
    return config.get(f"{provider}_api_key") or os.environ.get(f"{provider.upper()}_API_KEY") 