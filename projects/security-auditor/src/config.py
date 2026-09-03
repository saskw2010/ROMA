"""Configuration for the security auditor."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class Config:
    base_dir: Path
    temp_dir: Path
    reports_dir: Path
    log_file: Path
    enable_bandit: bool = True
    enable_semgrep: bool = True


def _to_bool(value: Optional[str], default: bool = True) -> bool:
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "no", "off"}


def load_config() -> Config:
    base_dir = Path(
        os.getenv("SECURITY_AUDITOR_BASE_DIR", Path(__file__).resolve().parent.parent)
    ).resolve()
    temp_dir = Path(os.getenv("SECURITY_AUDITOR_TEMP_DIR", base_dir / "tmp")).resolve()
    reports_dir = Path(
        os.getenv("SECURITY_AUDITOR_REPORTS_DIR", base_dir / "reports")
    ).resolve()
    log_file = Path(
        os.getenv("SECURITY_AUDITOR_LOG_FILE", reports_dir / "audit.log")
    ).resolve()

    temp_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    return Config(
        base_dir=base_dir,
        temp_dir=temp_dir,
        reports_dir=reports_dir,
        log_file=log_file,
        enable_bandit=_to_bool(os.getenv("SECURITY_AUDITOR_ENABLE_BANDIT"), True),
        enable_semgrep=_to_bool(os.getenv("SECURITY_AUDITOR_ENABLE_SEMGREP"), True),
    )


config = load_config()
