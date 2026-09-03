from __future__ import annotations

import asyncio

from src.audit import run_audit


async def main() -> None:
    report, paths = await run_audit(
        repo_url="https://github.com/pallets/flask",
        branch="main",
        verbose=True,
        debug=True,
        output_format="both",
        output_path="reports/flask-security-audit",
        timeout=180,
        parallel_execution=True,
    )
    print({"audit_id": report.audit_id, "outputs": [str(path) for path in paths]})


if __name__ == "__main__":
    asyncio.run(main())
