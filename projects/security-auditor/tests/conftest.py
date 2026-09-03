"""Pytest fixtures for security-auditor tests."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from src.models import AuditReport, AuditSummary, RepositoryInfo


@pytest.fixture
def sample_report() -> AuditReport:
    """Create a minimal valid audit report instance."""
    return AuditReport(
        audit_id="audit_20260101_000000",
        repository=RepositoryInfo(
            url="https://github.com/example/repo",
            name="repo",
            owner="example",
            branch="main",
            commit_sha="deadbeef",
            clone_timestamp=datetime.now(timezone.utc),
        ),
        summary=AuditSummary(files_scanned=10),
        findings=[],
        recommendations=["Keep dependencies up to date"],
    )
