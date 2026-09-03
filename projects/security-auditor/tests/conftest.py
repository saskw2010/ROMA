from __future__ import annotations

from pathlib import Path

import pytest

from src.config import config


@pytest.fixture
def isolated_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    temp_dir = tmp_path / "temp"
    reports_dir = tmp_path / "reports"
    log_dir = tmp_path / "logs"
    monkeypatch.setattr(config, "temp_dir", temp_dir)
    monkeypatch.setattr(config, "reports_dir", reports_dir)
    monkeypatch.setattr(config, "log_dir", log_dir)
    config.ensure_directories()
    return tmp_path


@pytest.fixture
def sample_repo_url() -> str:
    return "https://github.com/example/project"


@pytest.fixture
def sample_finding() -> dict[str, object]:
    return {
        "type": "bandit",
        "severity": "HIGH",
        "issue_type": "B101",
        "message": "Use of assert detected.",
        "file": "app.py",
        "line": 12,
        "code": "assert user.is_admin",
    }
