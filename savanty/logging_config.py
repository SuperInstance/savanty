"""Logging configuration for Savanty."""

import logging
import os
import sys


def setup_logging() -> logging.Logger:
    """Configure logging for the application.

    Returns:
        Configured logger for the savanty package.
    """
    log_level = os.getenv("SAVANTY_LOG_LEVEL", "INFO").upper()
    log_format = os.getenv(
        "SAVANTY_LOG_FORMAT",
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Set specific loggers
    savanty_logger = logging.getLogger("savanty")
    savanty_logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)

    return savanty_logger


logger = setup_logging()
