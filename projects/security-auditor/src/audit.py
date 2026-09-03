"""Command-line entry point for the security auditor."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from .agents import ReportGeneratorAgent, SecurityAuditorAgent
from .config import config
from .logging_config import configure_logging
from .models import AuditReport


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a security audit against a Git repository.")
    parser.add_argument("--repo", required=True, help="Repository URL to audit.")
    parser.add_argument("--branch", default="main", help="Repository branch to audit (default: main).")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose console logging.")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging.")
    parser.add_argument(
        "--output-format",
        choices=("json", "markdown", "both"),
        default="json",
        help="Output format for the saved report.",
    )
    parser.add_argument("-o", "--output", help="Output file or directory for the generated report.")
    parser.add_argument(
        "--log-level",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        help="Override the console and file log level.",
    )
    parser.add_argument("--log-file", help="Optional path for the JSON log file.")
    parser.add_argument("--timeout", type=int, default=config.default_timeout, help="Audit timeout in seconds.")
    parser.add_argument(
        "--parallel",
        action=argparse.BooleanOptionalAction,
        default=config.parallel_execution,
        help="Enable or disable parallel execution for analyzer stages.",
    )
    return parser


def resolve_log_level(args: argparse.Namespace) -> str:
    if args.debug:
        return "DEBUG"
    if args.log_level:
        return args.log_level
    if args.verbose:
        return "INFO"
    return "INFO"


def _base_output_path(report: AuditReport, output_path: str | None) -> Path:
    if not output_path:
        return config.reports_dir / report.audit_id
    path = Path(output_path)
    if path.exists() and path.is_dir():
        return path / report.audit_id
    if path.suffix:
        return path.with_suffix("")
    return path


def save_report(report: AuditReport, output_path: str | None = None, output_format: str = "json") -> list[Path]:
    base_path = _base_output_path(report, output_path)
    base_path.parent.mkdir(parents=True, exist_ok=True)
    report_payload = report.model_dump(mode="json")
    saved_paths: list[Path] = []

    if output_format in {"json", "both"}:
        json_path = base_path.with_suffix(".json")
        json_path.write_text(json.dumps(report_payload, indent=2), encoding="utf-8")
        saved_paths.append(json_path)

    if output_format in {"markdown", "both"}:
        markdown_path = base_path.with_suffix(".md")
        markdown = ReportGeneratorAgent().render_markdown(report)
        markdown_path.write_text(markdown, encoding="utf-8")
        saved_paths.append(markdown_path)

    return saved_paths


async def run_audit(
    *,
    repo_url: str,
    branch: str = "main",
    verbose: bool = False,
    debug: bool = False,
    output_format: str = "json",
    output_path: str | None = None,
    log_level: str | None = None,
    timeout: int | None = None,
    parallel_execution: bool | None = None,
    log_file: str | None = None,
) -> tuple[AuditReport, list[Path]]:
    resolved_log_level = "DEBUG" if debug else (log_level or "INFO")
    logger = configure_logging(verbose=verbose or debug, log_level=resolved_log_level, log_file=log_file)
    logger.info("Running security audit", extra={"event": "audit_started", "repo": repo_url})

    agent = SecurityAuditorAgent()
    report = await agent.audit(
        repo_url,
        branch=branch,
        timeout=timeout,
        parallel_execution=parallel_execution,
    )
    saved_paths = save_report(report, output_path=output_path, output_format=output_format)
    logger.info(
        "Security audit completed",
        extra={
            "event": "audit_completed",
            "audit_id": report.audit_id,
            "repo": repo_url,
            "output_paths": [str(path) for path in saved_paths],
        },
    )
    return report, saved_paths


def cli(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        report, saved_paths = asyncio.run(
            run_audit(
                repo_url=args.repo,
                branch=args.branch,
                verbose=args.verbose,
                debug=args.debug,
                output_format=args.output_format,
                output_path=args.output,
                log_level=resolve_log_level(args),
                timeout=args.timeout,
                parallel_execution=args.parallel,
                log_file=args.log_file,
            )
        )
    except KeyboardInterrupt:
        print("Audit interrupted by user.", file=sys.stderr)
        return 130
    except (TimeoutError, RuntimeError, ValueError, OSError) as exc:
        print(f"Audit failed: {exc}", file=sys.stderr)
        return 1

    print(f"Audit completed: {report.audit_id}")
    for path in saved_paths:
        print(f"Saved report: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
