"""Configuration for the security auditor project."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Mapping

from pydantic import BaseModel, Field


def _parse_bool(value: str | bool | None, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return value.strip().lower() in {"1", "true", "yes", "on"}


class SecurityAuditorConfig(BaseModel):
    project_root: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[1])
    temp_dir: Path | None = None
    reports_dir: Path | None = None
    log_dir: Path | None = None
    enable_bandit: bool = True
    enable_semgrep: bool = True
    clone_depth: int = 1
    clone_timeout: int = 60
    analysis_timeout: int = 120
    dependency_timeout: int = 60
    default_timeout: int = 300
    parallel_execution: bool = True

    def model_post_init(self, __context: object) -> None:
        self.temp_dir = self.temp_dir or self.project_root / ".tmp"
        self.reports_dir = self.reports_dir or self.project_root / "reports"
        self.log_dir = self.log_dir or self.project_root / "logs"
        self.ensure_directories()

    def ensure_directories(self) -> None:
        for path in (self.temp_dir, self.reports_dir, self.log_dir):
            path.mkdir(parents=True, exist_ok=True)

    def default_log_file(self) -> Path:
        return self.log_dir / "audit.log"

    @classmethod
    def load(cls, env: Mapping[str, str] | None = None) -> "SecurityAuditorConfig":
        environ = dict(os.environ if env is None else env)
        project_root = Path(environ.get("SECURITY_AUDITOR_PROJECT_ROOT", Path(__file__).resolve().parents[1]))
        return cls(
            project_root=project_root,
            temp_dir=Path(environ["SECURITY_AUDITOR_TEMP_DIR"]) if environ.get("SECURITY_AUDITOR_TEMP_DIR") else None,
            reports_dir=Path(environ["SECURITY_AUDITOR_REPORTS_DIR"]) if environ.get("SECURITY_AUDITOR_REPORTS_DIR") else None,
            log_dir=Path(environ["SECURITY_AUDITOR_LOG_DIR"]) if environ.get("SECURITY_AUDITOR_LOG_DIR") else None,
            enable_bandit=_parse_bool(environ.get("SECURITY_AUDITOR_ENABLE_BANDIT"), True),
            enable_semgrep=_parse_bool(environ.get("SECURITY_AUDITOR_ENABLE_SEMGREP"), True),
            clone_depth=int(environ.get("SECURITY_AUDITOR_CLONE_DEPTH", 1)),
            clone_timeout=int(environ.get("SECURITY_AUDITOR_CLONE_TIMEOUT", 60)),
            analysis_timeout=int(environ.get("SECURITY_AUDITOR_ANALYSIS_TIMEOUT", 120)),
            dependency_timeout=int(environ.get("SECURITY_AUDITOR_DEPENDENCY_TIMEOUT", 60)),
            default_timeout=int(environ.get("SECURITY_AUDITOR_TIMEOUT", 300)),
            parallel_execution=_parse_bool(environ.get("SECURITY_AUDITOR_PARALLEL"), True),
        )


config = SecurityAuditorConfig.load()
