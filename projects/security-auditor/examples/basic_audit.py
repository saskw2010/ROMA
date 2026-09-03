"""Basic security audit example."""

import asyncio

from src.agents import SecurityAuditorAgent


async def main() -> None:
    agent = SecurityAuditorAgent()
    repo_url = "https://github.com/example/repo.git"
    try:
        report = await agent.audit(repo_url)
        print(f"Report ID: {report.audit_id}")
        print(f"Findings: {report.summary.total_findings}")
    except Exception as exc:
        print(f"Audit failed: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
