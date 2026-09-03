from __future__ import annotations

import asyncio

from src.audit import run_audit


async def main() -> None:
    report, paths = await run_audit(
        repo_url="https://github.com/pallets/flask",
        branch="main",
        output_format="json",
    )
    print(report.audit_id)
    for path in paths:
        print(path)


if __name__ == "__main__":
    asyncio.run(main())
