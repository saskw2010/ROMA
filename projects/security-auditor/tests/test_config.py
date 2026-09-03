"""Configuration loading tests."""

from __future__ import annotations

from pathlib import Path

from src.config import AuditorConfig


def test_config_defaults(monkeypatch):
    monkeypatch.delenv("SECURITY_AUDITOR_REPORTS_DIR", raising=False)
    monkeypatch.delenv("SECURITY_AUDITOR_TEMP_DIR", raising=False)
    cfg = AuditorConfig.from_env()
    assert cfg.reports_dir.exists()
    assert cfg.temp_dir.exists()
    assert cfg.enable_bandit is True
    assert cfg.enable_semgrep is True


def test_config_custom_env(monkeypatch, tmp_path: Path):
    reports = tmp_path / "reports"
    temp_dir = tmp_path / "temp"
    monkeypatch.setenv("SECURITY_AUDITOR_REPORTS_DIR", str(reports))
    monkeypatch.setenv("SECURITY_AUDITOR_TEMP_DIR", str(temp_dir))
    monkeypatch.setenv("SECURITY_AUDITOR_ENABLE_BANDIT", "false")
    cfg = AuditorConfig.from_env()
    assert cfg.reports_dir == reports
    assert cfg.temp_dir == temp_dir
    assert cfg.enable_bandit is False
