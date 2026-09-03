"""Configuration and logging tests."""

from __future__ import annotations

from pathlib import Path

from src.config import AuditorConfig
from src.logging_config import setup_logging


def test_config_defaults(monkeypatch):
    monkeypatch.delenv("SECURITY_AUDITOR_REPORTS_DIR", raising=False)
    monkeypatch.delenv("SECURITY_AUDITOR_TEMP_DIR", raising=False)
    monkeypatch.delenv("SECURITY_AUDITOR_ENABLE_BANDIT", raising=False)
    monkeypatch.delenv("SECURITY_AUDITOR_ENABLE_SEMGREP", raising=False)

    cfg = AuditorConfig.from_env()

    assert cfg.reports_dir.exists()
    assert cfg.temp_dir.exists()
    assert cfg.enable_bandit is True
    assert cfg.enable_semgrep is True


def test_config_custom_env(monkeypatch, tmp_path: Path):
    reports_dir = tmp_path / "reports"
    temp_dir = tmp_path / "temp"
    monkeypatch.setenv("SECURITY_AUDITOR_REPORTS_DIR", str(reports_dir))
    monkeypatch.setenv("SECURITY_AUDITOR_TEMP_DIR", str(temp_dir))
    monkeypatch.setenv("SECURITY_AUDITOR_ENABLE_BANDIT", "false")
    monkeypatch.setenv("SECURITY_AUDITOR_ENABLE_SEMGREP", "no")

    cfg = AuditorConfig.from_env()

    assert cfg.reports_dir == reports_dir
    assert cfg.temp_dir == temp_dir
    assert cfg.enable_bandit is False
    assert cfg.enable_semgrep is False


def test_setup_logging_writes_plain_file_levels(tmp_path: Path):
    log_file = tmp_path / "security-auditor.log"
    logger = setup_logging("INFO", log_file)

    logger.info("hello")

    contents = log_file.read_text(encoding="utf-8")
    assert "INFO" in contents
    assert "\033[" not in contents
