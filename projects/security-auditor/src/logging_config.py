"""Logging helpers for the security auditor CLI."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from .config import config


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in ("event", "audit_id", "repo", "output_paths"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


class ConsoleFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] {record.levelname:<7} {record.getMessage()}"


def configure_logging(
    *,
    verbose: bool = False,
    log_level: str = "INFO",
    log_file: str | Path | None = None,
) -> logging.Logger:
    level_name = ("DEBUG" if verbose and log_level == "INFO" else log_level).upper()
    level = getattr(logging, level_name, logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(ConsoleFormatter())
    root_logger.addHandler(console_handler)

    log_path = Path(log_file) if log_file else config.default_log_file()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(level)
    file_handler.setFormatter(JsonFormatter())
    root_logger.addHandler(file_handler)

    return logging.getLogger("security_auditor")
