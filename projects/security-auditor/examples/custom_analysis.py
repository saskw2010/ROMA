"""Custom configuration example."""

import asyncio
import os

from src.agents import SecurityAuditorAgent


async def run_for_repo(repo_url: str) -> None:
    agent = SecurityAuditorAgent()
    report = await agent.audit(repo_url, branch="main")
    print(f"{repo_url} -> risk_score={report.summary.risk_score}")


async def main() -> None:
    os.environ["SECURITY_AUDITOR_ENABLE_BANDIT"] = "true"
    os.environ["SECURITY_AUDITOR_ENABLE_SEMGREP"] = "false"

    repos = [
        "https://github.com/example/repo1.git",
        "https://github.com/example/repo2.git",
    ]

    for repo in repos:
        try:
            await run_for_repo(repo)
        except Exception as exc:
            print(f"{repo}: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
