"""CLI entry point for running security audits."""

from __future__ import annotations

import argparse
import asyncio
import json
from collections.abc import Sequence
from pathlib import Path

try:
    from .agents import SecurityAuditorAgent
    from .config import config
    from .logging_config import setup_logging
    from .models import AuditReport
except ImportError:  # pragma: no cover - script execution fallback
    from agents import SecurityAuditorAgent  # type: ignore
    from config import config  # type: ignore
    from logging_config import setup_logging  # type: ignore
    from models import AuditReport  # type: ignore


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a multi-agent security audit")
    parser.add_argument("--repo", required=True, help="Git repository URL to audit")
    parser.add_argument(
        "--branch",
        default="main",
        help="Branch to clone and audit (default: main)",
    )
    parser.add_argument(
        "--output",
        default="both",
        choices=["json", "markdown", "both"],
        help="Output format for generated report",
    )
    return parser


def _validate_repo(repo: str) -> None:
    if not repo.startswith(("https://", "http://", "git@")):
        raise ValueError("--repo must be a valid Git URL")


def _render_markdown(report: AuditReport) -> str:
    summary = report.summary
    lines = [
        f"# Security Audit Report: {report.repository.owner}/{report.repository.name}",
        "",
        f"- **Audit ID:** `{report.audit_id}`",
        f"- **Repository:** {report.repository.url}",
        f"- **Branch:** `{report.repository.branch}`",
        f"- **Commit:** `{report.repository.commit_sha or 'unknown'}`",
        "",
        "## Summary",
        "",
        f"- Files scanned: **{summary.files_scanned}**",
        f"- Total findings: **{summary.total_findings}**",
        (
            "- Critical/High/Medium/Low/Info: "
            f"**{summary.critical}/{summary.high}/{summary.medium}/{summary.low}/{summary.info}**"
        ),
        f"- Vulnerable dependencies: **{summary.vulnerable_dependencies}**",
        f"- Risk score: **{summary.risk_score:.2f}/10**",
        "",
        "## Findings",
        "",
    ]

    if not report.findings:
        lines.append("No findings detected.")
    else:
        for finding in report.findings:
            lines.extend(
                [
                    f"### {finding.severity} - {finding.title}",
                    f"- ID: `{finding.finding_id}`",
                    f"- Type: `{finding.type}`",
                    f"- File: `{finding.file_path or 'n/a'}`",
                    f"- Line: `{finding.line_number or 'n/a'}`",
                    f"- Description: {finding.description}",
                    f"- Recommendation: {finding.recommendation or 'n/a'}",
                    "",
                ]
            )

    lines.extend(["## Recommendations", ""])
    lines.extend(f"- {item}" for item in report.recommendations)
    lines.append("")
    return "\n".join(lines)


async def run_audit(repo: str, branch: str, output: str) -> dict[str, Path]:
    """Run an audit and write report files."""
    _validate_repo(repo)
    logger = setup_logging(
        config.log_level,
        config.reports_dir / "security-auditor.log",
    )
    logger.info("Starting audit for %s on branch %s", repo, branch)

    auditor = SecurityAuditorAgent()
    report = await auditor.audit(repo, branch)

    output_files: dict[str, Path] = {}
    if output in {"json", "both"}:
        json_path = config.reports_dir / f"{report.audit_id}.json"
        json_path.write_text(
            json.dumps(report.model_dump(mode="json"), indent=2),
            encoding="utf-8",
        )
        output_files["json"] = json_path

    if output in {"markdown", "both"}:
        markdown_path = config.reports_dir / f"{report.audit_id}.md"
        markdown_path.write_text(_render_markdown(report), encoding="utf-8")
        output_files["markdown"] = markdown_path

    logger.info(
        "Audit completed; generated %s",
        ", ".join(str(path) for path in output_files.values()),
    )
    return output_files


def main(argv: Sequence[str] | None = None) -> int:
    """CLI main function."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        asyncio.run(run_audit(args.repo, args.branch, args.output))
        return 0
    except KeyboardInterrupt:
        print("Audit interrupted by user")
        return 130
    except Exception as exc:  # pragma: no cover - top-level safety
        print(f"Audit failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
