"""
Structured logging helpers for security auditor.
"""

import json
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


_LEVEL_ORDER = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40}
_GLOBAL_LEVEL = "INFO"


def configure_logging(level: str = "INFO") -> None:
    global _GLOBAL_LEVEL
    _GLOBAL_LEVEL = level.upper()


@dataclass
class StructuredLogger:
    name: str
    level: Optional[str] = None

    def _should_emit(self, level: str) -> bool:
        current_level = (self.level or _GLOBAL_LEVEL).upper()
        return _LEVEL_ORDER[level] >= _LEVEL_ORDER.get(current_level, 20)

    def _emit(self, level: str, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        if not self._should_emit(level):
            return
        payload: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "logger": self.name,
            "message": message,
        }
        if extra:
            payload.update(extra)
        sys.stderr.write(json.dumps(payload, default=str) + "\n")

    def debug(self, message: str, **extra: Any) -> None:
        self._emit("DEBUG", message, extra=extra or None)

    def info(self, message: str, **extra: Any) -> None:
        self._emit("INFO", message, extra=extra or None)

    def warning(self, message: str, **extra: Any) -> None:
        self._emit("WARNING", message, extra=extra or None)

    def error(self, message: str, **extra: Any) -> None:
        self._emit("ERROR", message, extra=extra or None)


def get_logger(name: str) -> StructuredLogger:
    return StructuredLogger(name=name)
