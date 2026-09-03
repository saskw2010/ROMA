"""Integration tests for end-to-end audit flow."""

from __future__ import annotations

import os

import pytest

from src.agents import SecurityAuditorAgent
from src.models import AuditReport


@pytest.mark.asyncio
@pytest.mark.integration
async def test_real_public_repo_audit():
    if os.getenv("RUN_INTEGRATION_TESTS") != "1":
        pytest.skip("Set RUN_INTEGRATION_TESTS=1 to run integration tests")

    auditor = SecurityAuditorAgent()
    report = await auditor.audit("https://github.com/pallets/itsdangerous", "main")

    assert isinstance(report, AuditReport)
    assert report.audit_id
    assert report.repository.name
    assert report.summary.files_scanned >= 1
