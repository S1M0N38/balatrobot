"""Utility functions for balatrobot.

This module provides shared utilities including logging configuration.
"""

import logging
import sys
from pathlib import Path


def setup_logging(
    level: str = "INFO",
    format_string: str | None = None,
    include_timestamp: bool = True,
) -> logging.Logger:
    """Configure logging for the balatrobot package.

    Sets up both console and file logging. Console logging uses the specified level,
    while file logging always uses DEBUG level and writes to balatrobot.log in the
    project root directory.

    Args:
        level: Logging level for console output (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        format_string: Custom format string for log messages.
        include_timestamp: Whether to include timestamp in log format.

    Returns:
        Configured logger instance for balatrobot.

    Raises:
        ValueError: If an invalid logging level is provided.
    """
    # Validate logging level
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {level}")

    # Create logger for balatrobot package
    logger = logging.getLogger("balatrobot")
    # Set logger to DEBUG level so it can capture all messages
    # Individual handlers will filter based on their own levels
    logger.setLevel(logging.DEBUG)

    # Remove existing handlers to avoid duplicate logs
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Set format
    if format_string is None:
        if include_timestamp:
            format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        else:
            format_string = "%(name)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(format_string)

    # Create console handler with user-specified level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Create file handler that always logs DEBUG level to balatrobot.log
    # Find the project root directory (where pyproject.toml is located)
    current_dir = Path(__file__).parent
    while current_dir != current_dir.parent:
        if (current_dir / "pyproject.toml").exists():
            break
        current_dir = current_dir.parent

    log_file_path = current_dir / "balatrobot.log"

    file_handler = logging.FileHandler(log_file_path, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """Get a logger instance for balatrobot.

    Args:
        name: Optional name for the logger. If None, returns the main balatrobot logger.

    Returns:
        Logger instance.
    """
    if name is None:
        return logging.getLogger("balatrobot")
    else:
        return logging.getLogger(f"balatrobot.{name}")


def configure_bot_logging(log_level: str = "INFO") -> None:
    """Configure logging specifically for bot instances.

    This is a convenience function that sets up logging with bot-appropriate defaults.

    Args:
        log_level: The logging level to use.
    """
    setup_logging(
        level=log_level,
        format_string="%(asctime)s - Bot - %(levelname)s - %(message)s",
        include_timestamp=True,
    )
