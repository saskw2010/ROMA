import pytest

from src.models import Finding, FindingType, SeverityLevel


def test_finding_validation_requires_fields():
    with pytest.raises(Exception):
        Finding(
            type=FindingType.OTHER,
            severity=SeverityLevel.LOW,
            title="x",
            description="x",
        )


def test_report_to_markdown_contains_sections(sample_report):
    markdown = sample_report.to_markdown()
    assert "# Security Audit Report" in markdown
    assert "## Summary" in markdown
    assert "## Findings" in markdown
    assert "Use prepared statements" in markdown


def test_report_model_dump_contains_findings(sample_report):
    payload = sample_report.model_dump(mode="json")
    assert payload["audit_id"] == "audit_test"
    assert payload["summary"]["total_findings"] == 1
    assert payload["findings"][0]["severity"] == "HIGH"
