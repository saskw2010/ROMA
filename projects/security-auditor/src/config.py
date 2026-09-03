from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Config:
    base_dir: Path
    temp_dir: Path
    reports_dir: Path
    enable_bandit: bool
    enable_semgrep: bool
    enable_pip_audit: bool


def _build_config() -> Config:
    base_dir = Path(__file__).resolve().parent.parent
    temp_dir = Path(os.getenv("SECURITY_AUDITOR_TEMP_DIR", base_dir / "tmp"))
    reports_dir = Path(os.getenv("SECURITY_AUDITOR_REPORTS_DIR", base_dir / "reports"))
    temp_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    return Config(
        base_dir=base_dir,
        temp_dir=temp_dir,
        reports_dir=reports_dir,
        enable_bandit=_env_flag("SECURITY_AUDITOR_ENABLE_BANDIT", True),
        enable_semgrep=_env_flag("SECURITY_AUDITOR_ENABLE_SEMGREP", True),
        enable_pip_audit=_env_flag("SECURITY_AUDITOR_ENABLE_PIP_AUDIT", True),
    )


config = _build_config()
