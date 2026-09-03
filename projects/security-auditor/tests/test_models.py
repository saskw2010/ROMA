from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from src.models import AuditReport, AuditSummary, Finding, FindingType, RepositoryInfo, SeverityLevel


def test_audit_report_model_validation() -> None:
    report = AuditReport(
        audit_id="audit_001",
        repository=RepositoryInfo(
            url="https://github.com/example/project",
            name="project",
            owner="example",
            branch="main",
            commit_sha="abc123",
            clone_timestamp=datetime.now(timezone.utc),
        ),
        summary=AuditSummary(files_scanned=10, total_findings=1, high=1, risk_score=1.5),
        findings=[
            Finding(
                finding_id="finding_0001",
                type=FindingType.OTHER,
                severity=SeverityLevel.HIGH,
                title="Example issue",
                description="Example description",
                file_path="app.py",
                line_number=10,
            )
        ],
    )

    assert report.summary.high == 1
    assert report.findings[0].severity == SeverityLevel.HIGH


def test_finding_rejects_invalid_line_number() -> None:
    with pytest.raises(ValidationError):
        Finding(
            finding_id="finding_0002",
            type=FindingType.OTHER,
            severity=SeverityLevel.LOW,
            title="Invalid line",
            description="line number must be positive",
            line_number=0,
        )
