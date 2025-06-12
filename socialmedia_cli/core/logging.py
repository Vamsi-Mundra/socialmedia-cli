"""Logging configuration for socialmedia-cli."""
import logging
from pathlib import Path
from datetime import datetime, timezone
import time

from .config import CONFIG_DIR, get_config_value

LOG_DIR = CONFIG_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Default timestamp format
DEFAULT_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

class UTCTimeFormatter(logging.Formatter):
    """Custom formatter that converts timestamps to UTC."""
    
    def formatTime(self, record, datefmt=None):
        """Convert the record's timestamp to UTC."""
        ct = datetime.fromtimestamp(record.created, tz=timezone.utc)
        if datefmt:
            return ct.strftime(datefmt)
        else:
            return ct.strftime(DEFAULT_TIMESTAMP_FORMAT)

def get_timestamp_format() -> str:
    """Get the timestamp format from config or use default."""
    return get_config_value('logging.timestamp_format', DEFAULT_TIMESTAMP_FORMAT)

def get_logger(name: str) -> logging.Logger:
    """Get a module-scoped logger that writes to both file and console."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Common formatter for both handlers
        timestamp_format = get_timestamp_format()
        formatter = UTCTimeFormatter(
            '%(asctime)s UTC - %(name)s - %(levelname)s - %(message)s',
            datefmt=timestamp_format
        )
        
        # File handler
        log_file = LOG_DIR / f"{name}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger 