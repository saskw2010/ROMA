from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from typing import Optional

try:
    from .agents import SecurityAuditorAgent
except ImportError:
    from agents import SecurityAuditorAgent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the ROMA security auditor.")
    parser.add_argument("repo", help="Repository URL to audit")
    parser.add_argument("--branch", default="main", help="Repository branch to scan")
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path for a copy of the generated JSON report",
    )
    return parser


async def _run_audit(repo: str, branch: str, output: Optional[Path]) -> int:
    report = await SecurityAuditorAgent().audit(repo, branch=branch)
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report.model_dump(mode="json"), indent=2), encoding="utf-8")
    print(json.dumps(report.model_dump(mode="json"), indent=2))
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return asyncio.run(_run_audit(args.repo, args.branch, args.output))
    except Exception as exc:
        print(f"Security audit failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
