"""Configuration management for socialmedia-cli."""
import os
from pathlib import Path
from typing import Optional

import tomli

CONFIG_DIR = Path.home() / ".socialmedia_cli"
CONFIG_FILE = CONFIG_DIR / "config.toml"

def ensure_config_dir():
    """Ensure the config directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_config() -> dict:
    """Load configuration from TOML file and environment variables."""
    config = {}
    
    # Load from TOML if exists
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "rb") as f:
            config = tomli.load(f)
    
    # Override with environment variables
    env_prefix = "SOCIALMEDIA_CLI_"
    for key, value in os.environ.items():
        if key.startswith(env_prefix):
            config_key = key[len(env_prefix):].lower()
            config[config_key] = value
    
    return config

def get_api_key(provider: str) -> Optional[str]:
    """Get API key for a specific provider."""
    config = load_config()
    return config.get(f"{provider}_api_key") or os.environ.get(f"{provider.upper()}_API_KEY") 