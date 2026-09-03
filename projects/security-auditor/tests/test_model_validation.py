import pytest
from pydantic import ValidationError

from models import (
    AuditReport,
    AuditSummary,
    Finding,
    FindingType,
    RepositoryInfo,
    SeverityLevel,
)


def test_finding_model_accepts_valid_values():
    finding = Finding(
        finding_id="f-001",
        type=FindingType.OTHER,
        severity=SeverityLevel.HIGH,
        title="Unsafe call",
        description="Potential unsafe subprocess usage.",
        recommendation="Sanitize input before execution.",
    )

    assert finding.finding_id == "f-001"
    assert finding.severity == SeverityLevel.HIGH


def test_finding_model_rejects_invalid_severity():
    with pytest.raises(ValidationError):
        Finding(
            finding_id="f-002",
            type=FindingType.OTHER,
            severity="SEVERE",
            title="Invalid severity",
            description="Bad value",
            recommendation="Fix severity enum.",
        )


def test_audit_report_model_validation():
    report = AuditReport(
        audit_id="audit_001",
        repository=RepositoryInfo(
            url="https://github.com/example/repo",
            name="repo",
            owner="example",
            language="Python",
        ),
        summary=AuditSummary(total_findings=1),
        findings=[],
        recommendations=[],
    )

    assert report.audit_id == "audit_001"
    assert report.repository.name == "repo"
