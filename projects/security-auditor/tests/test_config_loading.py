from pathlib import Path

from src.config import load_config


def test_config_loading_from_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("SECURITY_AUDITOR_TEMP_DIR", str(tmp_path / "temp-artifacts"))
    monkeypatch.setenv("SECURITY_AUDITOR_REPORTS_DIR", str(tmp_path / "reports"))
    monkeypatch.setenv("SECURITY_AUDITOR_ENABLE_BANDIT", "false")
    monkeypatch.setenv("SECURITY_AUDITOR_ENABLE_SEMGREP", "true")
    monkeypatch.setenv("SECURITY_AUDITOR_LOG_LEVEL", "debug")

    cfg = load_config()

    assert cfg.temp_dir == Path(tmp_path / "temp-artifacts")
    assert cfg.reports_dir == Path(tmp_path / "reports")
    assert cfg.temp_dir.exists()
    assert cfg.reports_dir.exists()
    assert cfg.enable_bandit is False
    assert cfg.enable_semgrep is True
    assert cfg.log_level == "DEBUG"
