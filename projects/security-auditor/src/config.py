"""Configuration for the security auditor."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _to_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class AuditorConfig:
    """Runtime configuration loaded from environment variables."""

    reports_dir: Path
    temp_dir: Path
    log_level: str = "INFO"
    enable_bandit: bool = True
    enable_semgrep: bool = True

    @classmethod
    def from_env(cls) -> "AuditorConfig":
        """Load configuration from environment variables."""
        base_dir = Path(__file__).resolve().parents[1]
        reports_dir = Path(
            os.getenv("SECURITY_AUDITOR_REPORTS_DIR", base_dir / "reports")
        )
        temp_dir = Path(
            os.getenv("SECURITY_AUDITOR_TEMP_DIR", base_dir / ".tmp_audits")
        )
        config = cls(
            reports_dir=reports_dir,
            temp_dir=temp_dir,
            log_level=os.getenv("SECURITY_AUDITOR_LOG_LEVEL", "INFO").upper(),
            enable_bandit=_to_bool(
                os.getenv("SECURITY_AUDITOR_ENABLE_BANDIT"),
                True,
            ),
            enable_semgrep=_to_bool(
                os.getenv("SECURITY_AUDITOR_ENABLE_SEMGREP"),
                True,
            ),
        )
        config.reports_dir.mkdir(parents=True, exist_ok=True)
        config.temp_dir.mkdir(parents=True, exist_ok=True)
        return config


config = AuditorConfig.from_env()
