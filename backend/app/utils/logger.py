"""
Logging configuration for the application
"""

import logging
import sys
import os
from datetime import datetime
from pathlib import Path

# Configure logging formats
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FORMAT_DETAILED = "%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Debug log file path
DEBUG_LOG_FILE = Path(__file__).parent.parent.parent / "debug_log.txt"

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Set up a logger with consistent formatting

    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)

    # Set level to DEBUG to capture everything
    logger.setLevel(logging.DEBUG)

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler (respects user-specified level)
    log_level = getattr(logging, level.upper(), logging.INFO)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Formatter for console
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    # File handler (ALWAYS DEBUG level for forensics)
    try:
        # Ensure parent directory exists
        DEBUG_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(DEBUG_LOG_FILE, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # Detailed formatter for file
        detailed_formatter = logging.Formatter(LOG_FORMAT_DETAILED, DATE_FORMAT)
        file_handler.setFormatter(detailed_formatter)

        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not set up file logging to {DEBUG_LOG_FILE}: {e}", file=sys.stderr)

    return logger


# Default application logger
app_logger = setup_logger("app", "INFO")
