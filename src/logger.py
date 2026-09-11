import logging
import sys

from src.config import CONSOLE_LOGGING, LOG_LEVEL

# Set of valid standard logging levels to prevent lookup injection or type errors
VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


def get_logger(name: str) -> logging.Logger:
    """Returns a configured logger instance with standardized formatting."""
    logger = logging.getLogger(name)

    # Restrict and validate log levels
    level_str = LOG_LEVEL if LOG_LEVEL in VALID_LOG_LEVELS else "INFO"
    numeric_level = getattr(logging, level_str)
    logger.setLevel(numeric_level)

    # Avoid adding duplicate handlers if the logger has already been initialized
    if not logger.handlers:
        if CONSOLE_LOGGING:
            handler = logging.StreamHandler(sys.stderr)
            handler.setLevel(numeric_level)

            # Formatting: [YYYY-MM-DD HH:MM:SS] [LEVEL] [MODULE] - MESSAGE
            formatter = logging.Formatter(
                fmt="[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        else:
            logger.addHandler(logging.NullHandler())

    # Prevent propagating to root logger to avoid duplicate output if root is configured elsewhere
    logger.propagate = False

    return logger
