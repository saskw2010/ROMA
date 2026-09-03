"""Pydantic model validation tests."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.models import (
    AuditReport,
    AuditSummary,
    Finding,
    FindingType,
    RepositoryInfo,
    SeverityLevel,
)


def test_finding_model_validation():
    finding = Finding(
        finding_id="finding_0001",
        type=FindingType.CODE,
        severity=SeverityLevel.HIGH,
        title="Hardcoded secret",
        description="Potential hardcoded secret discovered",
    )
    assert finding.severity == SeverityLevel.HIGH


def test_repository_url_validation():
    with pytest.raises(ValidationError):
        RepositoryInfo(url="invalid-url", name="repo", owner="me")


def test_audit_report_model_roundtrip():
    report = AuditReport(
        audit_id="audit_1",
        repository=RepositoryInfo(
            url="https://github.com/example/repo", name="repo", owner="example"
        ),
        summary=AuditSummary(files_scanned=2),
    )
    serialized = report.model_dump(mode="json")
    restored = AuditReport(**serialized)
    assert restored.audit_id == "audit_1"
