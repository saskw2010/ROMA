"""Basic usage example for a single repository audit."""

from __future__ import annotations

import asyncio

from src.audit import run_audit


async def main() -> None:
    await run_audit("https://github.com/pallets/itsdangerous", "main", "both")


if __name__ == "__main__":
    asyncio.run(main())
