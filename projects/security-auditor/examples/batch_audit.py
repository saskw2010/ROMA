"""Batch audit example with parallel execution."""

import asyncio

from src.agents import SecurityAuditorAgent


async def audit_repo(repo_url: str):
    agent = SecurityAuditorAgent()
    report = await agent.audit(repo_url)
    return {
        "repo": repo_url,
        "findings": report.summary.total_findings,
        "risk_score": report.summary.risk_score,
    }


async def main() -> None:
    repos = [
        "https://github.com/example/repo1.git",
        "https://github.com/example/repo2.git",
        "https://github.com/example/repo3.git",
    ]

    results = await asyncio.gather(
        *(audit_repo(repo) for repo in repos), return_exceptions=True
    )

    successful = [result for result in results if isinstance(result, dict)]
    total_findings = sum(item["findings"] for item in successful)

    print(f"Audited repositories: {len(successful)}/{len(repos)}")
    print(f"Total findings: {total_findings}")


if __name__ == "__main__":
    asyncio.run(main())
