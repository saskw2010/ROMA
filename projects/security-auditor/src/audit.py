"""CLI entrypoint for the security auditor."""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

from .agents import SecurityAuditorAgent
from .config import config
from .logging_config import configure_logging


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run security audit for a git repository"
    )
    parser.add_argument("--repo", required=True, help="Repository URL")
    parser.add_argument("--branch", default="main", help="Repository branch")
    parser.add_argument(
        "--format", choices=["json", "markdown"], default="json", help="Output format"
    )
    parser.add_argument("--output", help="Output file path")
    parser.add_argument(
        "--request-id", default="-", help="Request id for log correlation"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    return parser


def _default_output_path(report_id: str, output_format: str) -> Path:
    extension = "md" if output_format == "markdown" else "json"
    return config.reports_dir / f"{report_id}.{extension}"


def _write_report(report, output_format: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_format == "markdown":
        output_path.write_text(report.to_markdown(), encoding="utf-8")
    else:
        output_path.write_text(
            json.dumps(report.model_dump(mode="json"), indent=2, default=str),
            encoding="utf-8",
        )


async def run_audit(args: argparse.Namespace):
    logger = configure_logging(
        level=getattr(logging, args.log_level),
        log_file=str(config.log_file),
        request_id=args.request_id,
    )

    logger.info("Starting audit for %s", args.repo)
    agent = SecurityAuditorAgent()
    report = await agent.audit(repo_url=args.repo, branch=args.branch)

    output_path = (
        Path(args.output)
        if args.output
        else _default_output_path(report.audit_id, args.format)
    )
    _write_report(report, args.format, output_path)
    logger.info("Audit report written to %s", output_path)
    return output_path


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        output_path = asyncio.run(run_audit(args))
        print(output_path)
        return 0
    except KeyboardInterrupt:
        print("Audit interrupted", file=sys.stderr)
        return 130
    except Exception as exc:  # pragma: no cover - defensive CLI wrapper
        print(f"Audit failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
