"""
Configuration utilities for the security auditor.
"""

import os
from dataclasses import dataclass
from pathlib import Path


def _as_bool(value: str, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class AuditorConfig:
    project_root: Path
    temp_dir: Path
    reports_dir: Path
    enable_bandit: bool
    enable_semgrep: bool
    log_level: str


def load_config() -> AuditorConfig:
    project_root = Path(__file__).resolve().parent.parent
    temp_dir = Path(os.getenv("SECURITY_AUDITOR_TEMP_DIR", project_root / "tmp"))
    reports_dir = Path(os.getenv("SECURITY_AUDITOR_REPORTS_DIR", project_root / "reports"))

    temp_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    return AuditorConfig(
        project_root=project_root,
        temp_dir=temp_dir,
        reports_dir=reports_dir,
        enable_bandit=_as_bool(os.getenv("SECURITY_AUDITOR_ENABLE_BANDIT"), True),
        enable_semgrep=_as_bool(os.getenv("SECURITY_AUDITOR_ENABLE_SEMGREP"), True),
        log_level=os.getenv("SECURITY_AUDITOR_LOG_LEVEL", "INFO").upper(),
    )


config = load_config()
