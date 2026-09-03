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
DEBUG = 10
INFO = 20
WARNING = 30
ERROR = 40
CRITICAL = 50
NOTSET = 0


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

    def exception(self, message: str, **extra: Any) -> None:
        self._emit("ERROR", message, extra=extra or None)

    def setLevel(self, level: Any) -> None:
        if isinstance(level, int):
            reverse_map = {10: "DEBUG", 20: "INFO", 30: "WARNING", 40: "ERROR", 50: "ERROR"}
            self.level = reverse_map.get(level, "INFO")
        else:
            self.level = str(level).upper()

    def isEnabledFor(self, level: int) -> bool:
        current_level = _LEVEL_ORDER.get((self.level or _GLOBAL_LEVEL).upper(), 20)
        return level >= current_level


def get_logger(name: str) -> StructuredLogger:
    return StructuredLogger(name=name)


def getLogger(name: str | None = None) -> StructuredLogger:
    return StructuredLogger(name=name or "root")


def basicConfig(level: Any = "INFO", **_: Any) -> None:
    configure_logging(str(level))
