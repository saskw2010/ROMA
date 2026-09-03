from __future__ import annotations

import asyncio

from src.agents import SecurityAuditorAgent


async def _run_end_to_end() -> tuple[str, dict[str, object]]:
    agent = SecurityAuditorAgent()

    async def fake_scan(repo_url: str, branch: str = "main", timeout: int | None = None) -> dict[str, object]:
        return {
            "status": "success",
            "repo_url": repo_url,
            "clone_path": "/tmp/repo",
            "commit_sha": "deadbeef",
            "branch": branch,
            "files_count": 3,
            "files": [{"name": "app.py", "path": "app.py", "size": 10}],
        }

    async def fake_analysis(repo_path: str, timeout: int | None = None) -> dict[str, object]:
        return {
            "status": "success",
            "findings": [
                {
                    "type": "bandit",
                    "severity": "MEDIUM",
                    "issue_type": "B101",
                    "message": "Use of assert detected.",
                    "file": "app.py",
                    "line": 4,
                }
            ],
        }

    async def fake_dependency(repo_path: str, timeout: int | None = None) -> dict[str, object]:
        return {
            "status": "success",
            "vulnerabilities": [
                {
                    "package": "flask",
                    "version": "1.0.0",
                    "vulnerability_id": "PYSEC-0001",
                    "description": "Example vulnerability",
                    "fixed_version": "1.0.1",
                }
            ],
        }

    agent.scanner.execute = fake_scan
    agent.analyzer.execute = fake_analysis
    agent.dependency_checker.execute = fake_dependency

    report = await agent.audit("https://github.com/example/project", parallel_execution=False)
    return report.audit_id, agent.last_run


def test_end_to_end_audit_flow() -> None:
    audit_id, last_run = asyncio.run(_run_end_to_end())

    assert audit_id.startswith("audit_")
    assert last_run["scan"]["status"] == "success"
    assert last_run["analysis"]["status"] == "success"
    assert last_run["dependency"]["status"] == "success"
    assert last_run["report"]["status"] == "success"
