from __future__ import annotations

from pathlib import Path

from src.config import SecurityAuditorConfig


def test_config_loads_from_environment(tmp_path: Path) -> None:
    env = {
        "SECURITY_AUDITOR_PROJECT_ROOT": str(tmp_path),
        "SECURITY_AUDITOR_ENABLE_BANDIT": "false",
        "SECURITY_AUDITOR_ENABLE_SEMGREP": "true",
        "SECURITY_AUDITOR_TIMEOUT": "45",
        "SECURITY_AUDITOR_PARALLEL": "false",
    }

    loaded = SecurityAuditorConfig.load(env)

    assert loaded.project_root == tmp_path
    assert loaded.enable_bandit is False
    assert loaded.enable_semgrep is True
    assert loaded.default_timeout == 45
    assert loaded.parallel_execution is False
    assert loaded.reports_dir.exists()
    assert loaded.log_dir.exists()
