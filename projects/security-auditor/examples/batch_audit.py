from __future__ import annotations

import asyncio

from src.audit import run_audit

REPOSITORIES = [
    ("https://github.com/pallets/flask", "main"),
    ("https://github.com/pallets/click", "main"),
]


async def audit_repository(repo_url: str, branch: str) -> dict[str, str]:
    report, paths = await run_audit(
        repo_url=repo_url,
        branch=branch,
        output_format="json",
        parallel_execution=True,
    )
    return {"repo": repo_url, "audit_id": report.audit_id, "output": str(paths[0])}


async def main() -> None:
    results = await asyncio.gather(*(audit_repository(repo, branch) for repo, branch in REPOSITORIES))
    for result in results:
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
