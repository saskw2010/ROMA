from pathlib import Path


def test_load_config_creates_directories(temp_paths):
    from src.config import load_config

    cfg = load_config()
    assert cfg.base_dir == temp_paths
    assert cfg.temp_dir.exists()
    assert cfg.reports_dir.exists()
    assert cfg.log_file.parent.exists()


def test_load_config_respects_boolean_overrides(monkeypatch, tmp_path):
    monkeypatch.setenv("SECURITY_AUDITOR_BASE_DIR", str(tmp_path))
    monkeypatch.setenv("SECURITY_AUDITOR_ENABLE_BANDIT", "false")
    monkeypatch.setenv("SECURITY_AUDITOR_ENABLE_SEMGREP", "0")

    from src.config import load_config

    cfg = load_config()
    assert cfg.enable_bandit is False
    assert cfg.enable_semgrep is False


def test_load_config_uses_custom_paths(monkeypatch, tmp_path):
    temp_dir = tmp_path / "custom-temp"
    reports_dir = tmp_path / "custom-reports"
    monkeypatch.setenv("SECURITY_AUDITOR_BASE_DIR", str(tmp_path))
    monkeypatch.setenv("SECURITY_AUDITOR_TEMP_DIR", str(temp_dir))
    monkeypatch.setenv("SECURITY_AUDITOR_REPORTS_DIR", str(reports_dir))

    from src.config import load_config

    cfg = load_config()
    assert cfg.temp_dir == Path(temp_dir)
    assert cfg.reports_dir == Path(reports_dir)
