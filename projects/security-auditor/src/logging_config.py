"""Logging utilities for security auditor."""

import logging
from typing import Optional


class RequestIdFilter(logging.Filter):
    """Attach request id to log records."""

    def __init__(self, request_id: str = "-"):
        super().__init__()
        self.request_id = request_id

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = getattr(record, "request_id", self.request_id)
        return True


class _ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: "\033[36m",
        logging.INFO: "\033[32m",
        logging.WARNING: "\033[33m",
        logging.ERROR: "\033[31m",
        logging.CRITICAL: "\033[35m",
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        color = self.COLORS.get(record.levelno, "")
        return f"{color}{message}{self.RESET}" if color else message


def configure_logging(
    level: int = logging.INFO, log_file: Optional[str] = None, request_id: str = "-"
) -> logging.Logger:
    """Configure structured logging with console and file handlers."""
    logger = logging.getLogger("security_auditor")
    logger.setLevel(level)
    logger.propagate = False

    for handler in list(logger.handlers):
        logger.removeHandler(handler)

    request_filter = RequestIdFilter(request_id=request_id)
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(
        _ColorFormatter(
            "%(asctime)s | %(levelname)s | request=%(request_id)s | "
            "%(name)s | %(message)s"
        )
    )
    console.addFilter(request_filter)
    logger.addHandler(console)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | request=%(request_id)s | "
                "%(name)s | %(message)s"
            )
        )
        file_handler.addFilter(request_filter)
        logger.addHandler(file_handler)

    return logger
