"""
CLI entry point for Security Auditor.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence
from urllib.parse import urlparse

if __package__ in {None, ""}:
    script_dir = Path(__file__).resolve().parent
    if str(script_dir) in sys.path:
        sys.path.remove(str(script_dir))
    project_root = script_dir.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

import asyncio

try:
    from src.agents import SecurityAuditorAgent
    from src.logging import configure_logging
except ImportError:
    import importlib.util

    from agents import SecurityAuditorAgent
    logging_path = Path(__file__).with_name("logging.py")
    spec = importlib.util.spec_from_file_location("security_auditor_logging", logging_path)
    if spec is None or spec.loader is None:
        raise ImportError("Unable to load security auditor logging module")
    logging_module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = logging_module
    spec.loader.exec_module(logging_module)
    configure_logging = logging_module.configure_logging


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Security Auditor against a repository.")
    parser.add_argument("--repo", required=True, help="Repository URL (GitHub HTTPS URL).")
    parser.add_argument("--branch", default="main", help="Repository branch to audit.")
    parser.add_argument("--output", help="Optional path to save generated report JSON.")
    parser.add_argument("--json", action="store_true", help="Print full report JSON to stdout.")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Log level.",
    )
    return parser


def _validate_repo_url(repo_url: str) -> bool:
    parsed = urlparse(repo_url)
    if parsed.scheme != "https" or parsed.netloc != "github.com":
        return False
    parts = parsed.path.strip("/").split("/")
    return len(parts) >= 2 and all(parts[:2])


async def _run(repo_url: str, branch: str, output: str | None, emit_json: bool) -> int:
    agent = SecurityAuditorAgent()
    report = await agent.audit(repo_url, branch=branch)
    report_data = report.model_dump(mode="json")

    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report_data, indent=2, default=str))

    if emit_json:
        print(json.dumps(report_data, indent=2, default=str))
    else:
        print(f"Audit ID: {report.audit_id}")
        print(f"Repository: {report.repository.url}")
        print(f"Findings: {report.summary.total_findings}")
        print(f"Vulnerable dependencies: {report.summary.vulnerable_dependencies}")
        print(f"Risk score: {report.summary.risk_score}")

    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    configure_logging(args.log_level)

    if not _validate_repo_url(args.repo):
        parser.error("Invalid --repo value. Provide a full GitHub HTTPS URL.")

    try:
        return asyncio.run(_run(args.repo, args.branch, args.output, args.json))
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        print(f"Audit failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
