from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1] / "projects" / "security-auditor"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agents import SecurityAuditorAgent
from src.config import config


@pytest.mark.integration
def test_real_public_repository_audit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "temp_dir", tmp_path / "temp")
    monkeypatch.setattr(config, "reports_dir", tmp_path / "reports")
    monkeypatch.setattr(config, "log_dir", tmp_path / "logs")
    config.ensure_directories()

    agent = SecurityAuditorAgent()
    report = asyncio.run(
        agent.audit(
            "https://github.com/pallets/flask",
            branch="main",
            timeout=240,
            parallel_execution=True,
        )
    )

    assert report.audit_id.startswith("audit_")
    assert report.repository.name == "flask"
    assert isinstance(report.findings, list)
    assert report.agent_statuses["repository_scanner"] == "success"
    assert report.agent_statuses["static_analysis"] == "success"
    assert report.agent_statuses["dependency_checker"] == "success"
    assert report.agent_statuses["report_generator"] == "success"
    assert report.summary.files_scanned > 0
