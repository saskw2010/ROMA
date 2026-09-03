"""Example showing custom runtime configuration."""

from __future__ import annotations

import asyncio
import os


async def main() -> None:
    os.environ["SECURITY_AUDITOR_ENABLE_SEMGREP"] = "false"
    from src.audit import run_audit

    await run_audit("https://github.com/pallets/itsdangerous", "main", "json")


if __name__ == "__main__":
    asyncio.run(main())
