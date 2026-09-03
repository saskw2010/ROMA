"""Structured logging configuration for security auditor."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

_COLORS = {
    "DEBUG": "\033[36m",
    "INFO": "\033[32m",
    "WARNING": "\033[33m",
    "ERROR": "\033[31m",
    "CRITICAL": "\033[35m",
}
_RESET = "\033[0m"


class ColorFormatter(logging.Formatter):
    """Formatter that adds colors by severity for console output."""

    def format(self, record: logging.LogRecord) -> str:
        original = record.levelname
        color = _COLORS.get(original, "")
        if color:
            record.levelname = f"{color}{original}{_RESET}"
        try:
            return super().format(record)
        finally:
            record.levelname = original


def setup_logging(
    log_level: str = "INFO",
    log_file: Path | None = None,
) -> logging.Logger:
    """Set up console and file logging with context-rich formatting."""
    logger = logging.getLogger("security_auditor")
    logger.setLevel(log_level.upper())
    logger.handlers.clear()

    fmt = (
        "%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s"
    )

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(ColorFormatter(fmt))
    logger.addHandler(console)

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(file_handler)

    logger.propagate = False
    return logger
