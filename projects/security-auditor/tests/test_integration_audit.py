import os

import pytest

from agents import SecurityAuditorAgent


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skipif(
    os.getenv("RUN_SECURITY_AUDITOR_INTEGRATION") != "1",
    reason="Set RUN_SECURITY_AUDITOR_INTEGRATION=1 to run integration test.",
)
async def test_real_public_repository_audit():
    agent = SecurityAuditorAgent()
    report = await agent.audit("https://github.com/github/gitignore", branch="main")

    assert report.repository.name == "gitignore"
    assert report.summary.files_scanned > 0
