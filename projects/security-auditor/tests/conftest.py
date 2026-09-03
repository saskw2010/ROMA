from datetime import datetime
from pathlib import Path

import pytest

from src.models import (
    AuditReport,
    AuditSummary,
    Finding,
    FindingType,
    RepositoryInfo,
    SeverityLevel,
)


@pytest.fixture
def temp_paths(tmp_path, monkeypatch):
    monkeypatch.setenv("SECURITY_AUDITOR_BASE_DIR", str(tmp_path))
    monkeypatch.setenv("SECURITY_AUDITOR_TEMP_DIR", str(tmp_path / "tmp"))
    monkeypatch.setenv("SECURITY_AUDITOR_REPORTS_DIR", str(tmp_path / "reports"))
    monkeypatch.setenv(
        "SECURITY_AUDITOR_LOG_FILE", str(tmp_path / "reports" / "audit.log")
    )
    return tmp_path


@pytest.fixture
def sample_finding() -> Finding:
    return Finding(
        finding_id="finding_0001",
        type=FindingType.OTHER,
        severity=SeverityLevel.HIGH,
        title="Potential SQL injection",
        description="Input is used directly in query execution.",
        file_path="app/db.py",
        line_number=12,
        recommendation="Use parameterized queries",
        tool_source="bandit",
    )


@pytest.fixture
def sample_report(sample_finding: Finding) -> AuditReport:
    return AuditReport(
        audit_id="audit_test",
        repository=RepositoryInfo(
            url="https://github.com/example/repo",
            name="repo",
            owner="example",
            branch="main",
            commit_sha="abc123",
            clone_timestamp=datetime.utcnow(),
        ),
        summary=AuditSummary(total_findings=1, high=1, files_scanned=5, risk_score=2.0),
        findings=[sample_finding],
        recommendations=["Use prepared statements"],
    )


@pytest.fixture
def mock_repo_dir(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    (repo / "app.py").write_text("print('ok')\n", encoding="utf-8")
    return repo
