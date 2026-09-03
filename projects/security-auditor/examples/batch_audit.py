"""Example for auditing multiple repositories sequentially."""

from __future__ import annotations

import asyncio

from src.audit import run_audit

REPOS = [
    "https://github.com/pallets/itsdangerous",
    "https://github.com/pallets/werkzeug",
]


async def main() -> None:
    for repo in REPOS:
        await run_audit(repo, "main", "json")


if __name__ == "__main__":
    asyncio.run(main())
