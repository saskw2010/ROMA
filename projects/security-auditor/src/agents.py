"""Multi-agent security auditor implementation."""

from __future__ import annotations

import asyncio
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import config
from .models import (
    AuditReport,
    AuditSummary,
    DependencyVulnerability,
    Finding,
    FindingType,
    RepositoryInfo,
    SeverityLevel,
)

import logging

logger = logging.getLogger(__name__)


class RepositoryScannerAgent:
    """Scans and clones repositories for auditing."""

    def __init__(self) -> None:
        self.name = "RepositoryScannerAgent"
        self.temp_dir = config.temp_dir

    async def execute(self, repo_url: str, branch: str = "main", timeout: int | None = None) -> dict[str, Any]:
        logger.info("Scanning repository %s", repo_url)
        repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
        clone_path = self.temp_dir / repo_name

        try:
            if clone_path.exists():
                shutil.rmtree(clone_path)

            result = subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    str(config.clone_depth),
                    "-b",
                    branch,
                    repo_url,
                    str(clone_path),
                ],
                capture_output=True,
                text=True,
                check=True,
                timeout=timeout or config.clone_timeout,
            )
            logger.debug("git clone stdout: %s", result.stdout.strip())

            commit_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=clone_path,
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )
            commit_sha = commit_result.stdout.strip()

            files: list[dict[str, Any]] = []
            for root, dirs, filenames in os.walk(clone_path):
                dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", "node_modules", ".venv"}]
                for filename in filenames:
                    filepath = Path(root) / filename
                    rel_path = filepath.relative_to(clone_path)
                    files.append(
                        {
                            "name": filename,
                            "path": str(rel_path),
                            "size": filepath.stat().st_size,
                        }
                    )

            return {
                "status": "success",
                "repo_url": repo_url,
                "clone_path": str(clone_path),
                "commit_sha": commit_sha,
                "branch": branch,
                "files_count": len(files),
                "files": files[:100],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as exc:
            logger.error("Repository scan failed: %s", exc)
            return {"status": "error", "error": str(exc), "repo_url": repo_url, "branch": branch}


class StaticAnalysisAgent:
    """Runs static analysis tools against a repository."""

    def __init__(self) -> None:
        self.name = "StaticAnalysisAgent"

    async def execute(self, repo_path: str, timeout: int | None = None) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []
        try:
            if config.enable_bandit:
                findings.extend(await self._run_bandit(repo_path, timeout=timeout))
            if config.enable_semgrep:
                findings.extend(await self._run_semgrep(repo_path, timeout=timeout))
            return {
                "status": "success",
                "findings": findings,
                "total_findings": len(findings),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as exc:
            logger.error("Static analysis failed: %s", exc)
            return {"status": "error", "error": str(exc), "findings": []}

    async def _run_bandit(self, repo_path: str, timeout: int | None = None) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        try:
            result = subprocess.run(
                ["bandit", "-r", repo_path, "-f", "json", "-ll"],
                capture_output=True,
                text=True,
                timeout=timeout or config.analysis_timeout,
            )
            if result.stdout:
                bandit_results = json.loads(result.stdout)
                for issue in bandit_results.get("results", []):
                    findings.append(
                        {
                            "type": "bandit",
                            "severity": issue.get("severity", "LOW").upper(),
                            "issue_type": issue.get("test_id", "Bandit finding"),
                            "message": issue.get("issue_text", ""),
                            "file": issue.get("filename"),
                            "line": issue.get("line_number"),
                            "code": issue.get("code"),
                        }
                    )
        except FileNotFoundError:
            logger.warning("Bandit is not installed; skipping bandit scan")
        except Exception as exc:
            logger.warning("Bandit analysis failed: %s", exc)
        return findings

    async def _run_semgrep(self, repo_path: str, timeout: int | None = None) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        try:
            result = subprocess.run(
                ["semgrep", "--json", "-c", "p/security-audit", repo_path],
                capture_output=True,
                text=True,
                timeout=timeout or config.analysis_timeout,
            )
            if result.stdout:
                semgrep_results = json.loads(result.stdout)
                for issue in semgrep_results.get("results", []):
                    findings.append(
                        {
                            "type": "semgrep",
                            "severity": issue.get("severity", "LOW").upper(),
                            "issue_type": issue.get("check_id") or issue.get("rule_id") or "Semgrep finding",
                            "message": issue.get("message", ""),
                            "file": issue.get("path"),
                            "line": issue.get("start", {}).get("line"),
                        }
                    )
        except FileNotFoundError:
            logger.warning("Semgrep is not installed; skipping semgrep scan")
        except Exception as exc:
            logger.warning("Semgrep analysis failed: %s", exc)
        return findings


class DependencyCheckerAgent:
    """Checks dependency manifests for vulnerable packages."""

    def __init__(self) -> None:
        self.name = "DependencyCheckerAgent"

    async def execute(self, repo_path: str, timeout: int | None = None) -> dict[str, Any]:
        vulnerabilities: list[dict[str, Any]] = []
        try:
            vulnerabilities.extend(await self._check_python_deps(repo_path, timeout=timeout))
            return {
                "status": "success",
                "vulnerabilities": vulnerabilities,
                "total_vulnerabilities": len(vulnerabilities),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as exc:
            logger.error("Dependency check failed: %s", exc)
            return {"status": "error", "error": str(exc), "vulnerabilities": []}

    async def _check_python_deps(self, repo_path: str, timeout: int | None = None) -> list[dict[str, Any]]:
        req_file = Path(repo_path) / "requirements.txt"
        vulnerabilities: list[dict[str, Any]] = []
        if not req_file.exists():
            return vulnerabilities

        try:
            result = subprocess.run(
                ["pip-audit", "-r", str(req_file), "-f", "json"],
                capture_output=True,
                text=True,
                timeout=timeout or config.dependency_timeout,
            )
            if not result.stdout:
                return vulnerabilities

            audit_results = json.loads(result.stdout)
            if isinstance(audit_results, list):
                for dependency in audit_results:
                    package_name = dependency.get("name")
                    package_version = dependency.get("version")
                    for vuln in dependency.get("vulns", []):
                        vulnerabilities.append(
                            {
                                "package": package_name,
                                "version": package_version,
                                "vulnerability_id": vuln.get("id"),
                                "description": vuln.get("description"),
                                "fixed_version": (vuln.get("fix_versions") or [None])[0],
                            }
                        )
            elif isinstance(audit_results, dict):
                for vuln in audit_results.get("vulnerabilities", []):
                    vulnerabilities.append(
                        {
                            "package": vuln.get("name"),
                            "version": vuln.get("version"),
                            "vulnerability_id": vuln.get("id"),
                            "description": vuln.get("description"),
                            "fixed_version": (vuln.get("fix_versions") or [None])[0],
                        }
                    )
        except FileNotFoundError:
            logger.warning("pip-audit is not installed; skipping dependency audit")
        except Exception as exc:
            logger.warning("Dependency audit failed: %s", exc)
        return vulnerabilities


class ReportGeneratorAgent:
    """Builds machine-readable and markdown reports."""

    def __init__(self) -> None:
        self.name = "ReportGeneratorAgent"

    async def execute(
        self,
        repo_url: str,
        scan_result: dict[str, Any],
        analysis_result: dict[str, Any],
        dependency_result: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            repo_info = self._build_repository_info(repo_url, scan_result)
            findings = self._process_findings(analysis_result.get("findings", []))
            dependency_vulnerabilities = [
                DependencyVulnerability(**item) for item in dependency_result.get("vulnerabilities", [])
            ]
            summary = self._calculate_summary(findings, dependency_vulnerabilities, scan_result.get("files_count", 0))
            report = AuditReport(
                audit_id=f"audit_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
                repository=repo_info,
                summary=summary,
                findings=findings,
                dependency_vulnerabilities=dependency_vulnerabilities,
                recommendations=self._generate_recommendations(summary),
                agent_statuses={
                    "repository_scanner": scan_result.get("status", "unknown"),
                    "static_analysis": analysis_result.get("status", "unknown"),
                    "dependency_checker": dependency_result.get("status", "unknown"),
                    "report_generator": "success",
                },
                metadata={
                    "branch": scan_result.get("branch", repo_info.branch),
                    "files_sample": scan_result.get("files", []),
                },
            )
            return {
                "status": "success",
                "report": report.model_dump(mode="json"),
                "report_id": report.audit_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as exc:
            logger.error("Report generation failed: %s", exc)
            return {"status": "error", "error": str(exc)}

    def _build_repository_info(self, repo_url: str, scan_result: dict[str, Any]) -> RepositoryInfo:
        parts = repo_url.rstrip("/").split("/")
        owner = parts[-2] if len(parts) >= 2 else "unknown"
        name = parts[-1].replace(".git", "")
        return RepositoryInfo(
            url=repo_url,
            name=name,
            owner=owner,
            language="Unknown",
            is_private=False,
            branch=scan_result.get("branch", "main"),
            commit_sha=scan_result.get("commit_sha"),
        )

    def _process_findings(self, raw_findings: list[dict[str, Any]]) -> list[Finding]:
        findings: list[Finding] = []
        for index, raw in enumerate(raw_findings):
            finding = Finding(
                finding_id=f"finding_{index:04d}",
                type=self._map_finding_type(raw.get("type", "other")),
                severity=self._map_severity(raw.get("severity", "LOW")),
                title=raw.get("issue_type", "Security Issue"),
                description=raw.get("message", ""),
                file_path=raw.get("file"),
                line_number=raw.get("line"),
                code_snippet=raw.get("code"),
                recommendation="Review and remediate this issue.",
                tool_source=raw.get("type", "unknown"),
            )
            findings.append(finding)
        return findings

    def _map_finding_type(self, raw_type: str) -> FindingType:
        mapping = {
            "bandit": FindingType.MISCONFIGURATION,
            "semgrep": FindingType.OTHER,
            "dependency": FindingType.DEPENDENCY,
        }
        return mapping.get(raw_type.lower(), FindingType.OTHER)

    def _map_severity(self, severity: str) -> SeverityLevel:
        mapping = {
            "CRITICAL": SeverityLevel.CRITICAL,
            "HIGH": SeverityLevel.HIGH,
            "MEDIUM": SeverityLevel.MEDIUM,
            "LOW": SeverityLevel.LOW,
            "INFO": SeverityLevel.INFO,
        }
        return mapping.get(severity.upper(), SeverityLevel.LOW)

    def _calculate_summary(
        self,
        findings: list[Finding],
        vulnerabilities: list[DependencyVulnerability],
        files_count: int,
    ) -> AuditSummary:
        summary = AuditSummary(files_scanned=files_count)
        for finding in findings:
            summary.total_findings += 1
            if finding.severity == SeverityLevel.CRITICAL:
                summary.critical += 1
            elif finding.severity == SeverityLevel.HIGH:
                summary.high += 1
            elif finding.severity == SeverityLevel.MEDIUM:
                summary.medium += 1
            elif finding.severity == SeverityLevel.LOW:
                summary.low += 1
            else:
                summary.info += 1
        summary.vulnerable_dependencies = len(vulnerabilities)
        score = summary.critical * 2.5 + summary.high * 1.5 + summary.medium * 1.0 + summary.low * 0.5
        if vulnerabilities:
            score += min(len(vulnerabilities), 3)
        summary.risk_score = min(10.0, round(score, 2))
        return summary

    def _generate_recommendations(self, summary: AuditSummary) -> list[str]:
        recommendations: list[str] = []
        if summary.critical:
            recommendations.append("Address critical findings immediately.")
        if summary.high:
            recommendations.append("Prioritize high-severity issues in the next remediation cycle.")
        if summary.vulnerable_dependencies:
            recommendations.append("Upgrade vulnerable dependencies to patched versions.")
        recommendations.extend(
            [
                "Enable automated security scanning in CI/CD.",
                "Review third-party dependencies on a regular schedule.",
                "Add secure code review checkpoints before release.",
            ]
        )
        return recommendations

    def render_markdown(self, report: AuditReport) -> str:
        lines = [
            f"# Security Audit Report: {report.repository.owner}/{report.repository.name}",
            "",
            f"- Audit ID: `{report.audit_id}`",
            f"- Branch: `{report.repository.branch}`",
            f"- Commit: `{report.repository.commit_sha or 'unknown'}`",
            f"- Generated at: `{report.generated_at.isoformat()}`",
            "",
            "## Summary",
            "",
            f"- Files scanned: {report.summary.files_scanned}",
            f"- Total findings: {report.summary.total_findings}",
            f"- Vulnerable dependencies: {report.summary.vulnerable_dependencies}",
            f"- Risk score: {report.summary.risk_score}/10",
            "",
            "## Agent Status",
            "",
        ]
        for name, status in report.agent_statuses.items():
            lines.append(f"- {name}: {status}")
        lines.extend(["", "## Findings", ""])
        if not report.findings and not report.dependency_vulnerabilities:
            lines.append("No findings were reported by the configured scanners.")
        for finding in report.findings:
            location = finding.file_path or "repository-wide"
            if finding.line_number:
                location = f"{location}:{finding.line_number}"
            lines.extend(
                [
                    f"### {finding.title}",
                    f"- Severity: {finding.severity.value}",
                    f"- Source: {finding.tool_source or 'unknown'}",
                    f"- Location: {location}",
                    f"- Description: {finding.description}",
                    f"- Recommendation: {finding.recommendation or 'Review the issue.'}",
                    "",
                ]
            )
        if report.dependency_vulnerabilities:
            lines.extend(["## Dependency Vulnerabilities", ""])
            for vulnerability in report.dependency_vulnerabilities:
                lines.append(
                    f"- `{vulnerability.package}` ({vulnerability.version or 'unknown'}) - "
                    f"{vulnerability.vulnerability_id}"
                )
        lines.extend(["", "## Recommendations", ""])
        lines.extend(f"- {item}" for item in report.recommendations)
        return "\n".join(lines).strip() + "\n"


class SecurityAuditorAgent:
    """Orchestrates the complete security audit workflow."""

    def __init__(self) -> None:
        self.name = "SecurityAuditorAgent"
        self.scanner = RepositoryScannerAgent()
        self.analyzer = StaticAnalysisAgent()
        self.dependency_checker = DependencyCheckerAgent()
        self.report_generator = ReportGeneratorAgent()
        self.last_run: dict[str, Any] = {}

    async def audit(
        self,
        repo_url: str,
        branch: str = "main",
        timeout: int | None = None,
        parallel_execution: bool | None = None,
    ) -> AuditReport:
        if timeout is not None:
            return await asyncio.wait_for(
                self._audit_impl(repo_url, branch, parallel_execution=parallel_execution),
                timeout=timeout,
            )
        return await self._audit_impl(repo_url, branch, parallel_execution=parallel_execution)

    async def _audit_impl(
        self,
        repo_url: str,
        branch: str,
        *,
        parallel_execution: bool | None,
    ) -> AuditReport:
        logger.info("Starting security audit for %s", repo_url)
        scan_result = await self.scanner.execute(repo_url, branch=branch, timeout=config.clone_timeout)
        if scan_result.get("status") != "success":
            raise RuntimeError(f"Repository scan failed: {scan_result.get('error', 'unknown error')}")

        repo_path = scan_result["clone_path"]
        use_parallel = config.parallel_execution if parallel_execution is None else parallel_execution
        if use_parallel:
            analysis_result, dependency_result = await asyncio.gather(
                self.analyzer.execute(repo_path, timeout=config.analysis_timeout),
                self.dependency_checker.execute(repo_path, timeout=config.dependency_timeout),
            )
        else:
            analysis_result = await self.analyzer.execute(repo_path, timeout=config.analysis_timeout)
            dependency_result = await self.dependency_checker.execute(repo_path, timeout=config.dependency_timeout)

        report_result = await self.report_generator.execute(repo_url, scan_result, analysis_result, dependency_result)
        if report_result.get("status") != "success":
            raise RuntimeError(f"Report generation failed: {report_result.get('error', 'unknown error')}")

        self.last_run = {
            "scan": scan_result,
            "analysis": analysis_result,
            "dependency": dependency_result,
            "report": report_result,
            "parallel_execution": use_parallel,
        }
        return AuditReport(**report_result["report"])
