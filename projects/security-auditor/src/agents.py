"""Multi-agent security auditor implementation."""

import asyncio
import json
import logging
import os
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    from .config import config
    from .models import (
        AuditReport,
        AuditSummary,
        Finding,
        FindingType,
        RepositoryInfo,
        SeverityLevel,
    )
except ImportError:  # pragma: no cover - script execution fallback
    from config import config  # type: ignore
    from models import (  # type: ignore
        AuditReport,
        AuditSummary,
        Finding,
        FindingType,
        RepositoryInfo,
        SeverityLevel,
    )

logger = logging.getLogger("security_auditor")


class RepositoryScannerAgent:
    """🔍 SEARCH Agent - Scans and analyzes repositories"""

    def __init__(self):
        self.name = "RepositoryScannerAgent"
        self.temp_dir = config.temp_dir

    async def execute(self, repo_url: str, branch: str = "main") -> dict[str, Any]:
        """Scan repository and return file manifest"""
        logger.info(f"📍 [SEARCH] Scanning repository: {repo_url}")

        try:
            repo_name = repo_url.split("/")[-1].replace(".git", "")
            clone_path = self.temp_dir / repo_name

            if clone_path.exists():
                shutil.rmtree(clone_path)

            # Clone with depth to save time
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "-b",
                    branch,
                    repo_url,
                    str(clone_path),
                ],
                check=True,
                capture_output=True,
                timeout=60,
            )

            # Get commit info
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=clone_path,
                capture_output=True,
                text=True,
                check=True,
            )
            commit_sha = result.stdout.strip()

            # Scan files
            files = []
            for root, dirs, filenames in os.walk(clone_path):
                dirs[:] = [
                    d
                    for d in dirs
                    if d not in {".git", "__pycache__", "node_modules", ".venv"}
                ]
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

            logger.info(f"✅ Found {len(files)} files")
            return {
                "status": "success",
                "repo_url": repo_url,
                "clone_path": str(clone_path),
                "commit_sha": commit_sha,
                "branch": branch,
                "files_count": len(files),
                "files": files[:100],
                "timestamp": datetime.now(UTC).isoformat(),
            }
        except Exception as e:
            logger.error(f"❌ Repository scan failed: {e}")
            return {"status": "error", "error": str(e)}


class StaticAnalysisAgent:
    """🤔 THINK Agent - Performs static code analysis"""

    def __init__(self):
        self.name = "StaticAnalysisAgent"

    async def execute(self, repo_path: str) -> dict[str, Any]:
        """Run static analysis tools"""
        logger.info(f"🔎 [THINK] Running static analysis on: {repo_path}")

        findings = []

        try:
            if config.enable_bandit:
                findings.extend(await self._run_bandit(repo_path))

            if config.enable_semgrep:
                findings.extend(await self._run_semgrep(repo_path))

            logger.info(f"✅ Found {len(findings)} static issues")
            return {
                "status": "success",
                "findings": findings,
                "total_findings": len(findings),
                "timestamp": datetime.now(UTC).isoformat(),
            }
        except Exception as e:
            logger.error(f"❌ Static analysis failed: {e}")
            return {"status": "error", "error": str(e), "findings": []}

    async def _run_bandit(self, repo_path: str) -> list[dict[str, Any]]:
        """Run Bandit security scanner"""
        findings = []
        try:
            result = subprocess.run(
                ["bandit", "-r", repo_path, "-f", "json", "-ll"],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.stdout:
                bandit_results = json.loads(result.stdout)
                for issue in bandit_results.get("results", []):
                    findings.append(
                        {
                            "type": "bandit",
                            "severity": issue.get("severity", "LOW").upper(),
                            "issue_type": issue.get("test_id"),
                            "message": issue.get("issue_text"),
                            "file": issue.get("filename"),
                            "line": issue.get("line_number"),
                            "code": issue.get("code"),
                        }
                    )
                logger.info(f"🔍 Bandit found {len(findings)} issues")
        except FileNotFoundError:
            logger.warning("⚠️  Bandit not installed")
        except Exception as e:
            logger.warning(f"⚠️  Bandit analysis failed: {e}")

        return findings

    async def _run_semgrep(self, repo_path: str) -> list[dict[str, Any]]:
        """Run Semgrep pattern matcher"""
        findings = []
        try:
            result = subprocess.run(
                ["semgrep", "--json", "-c", "p/security-audit", repo_path],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.stdout:
                semgrep_results = json.loads(result.stdout)
                for issue in semgrep_results.get("results", []):
                    findings.append(
                        {
                            "type": "semgrep",
                            "severity": issue.get("severity", "LOW").upper(),
                            "rule_id": issue.get("rule_id"),
                            "message": issue.get("message"),
                            "file": issue.get("path"),
                            "line": issue.get("start", {}).get("line"),
                        }
                    )
                logger.info(f"🔍 Semgrep found {len(findings)} issues")
        except FileNotFoundError:
            logger.warning("⚠️  Semgrep not installed")
        except Exception as e:
            logger.warning(f"⚠️  Semgrep analysis failed: {e}")

        return findings


class DependencyCheckerAgent:
    """📦 SEARCH Agent - Checks dependency vulnerabilities"""

    def __init__(self):
        self.name = "DependencyCheckerAgent"

    async def execute(self, repo_path: str) -> dict[str, Any]:
        """Check for vulnerable dependencies"""
        logger.info(f"📦 [SEARCH] Checking dependencies in: {repo_path}")

        vulnerabilities = []

        try:
            vulnerabilities.extend(await self._check_python_deps(repo_path))

            logger.info(f"✅ Found {len(vulnerabilities)} vulnerabilities")
            return {
                "status": "success",
                "vulnerabilities": vulnerabilities,
                "total_vulnerabilities": len(vulnerabilities),
                "timestamp": datetime.now(UTC).isoformat(),
            }
        except Exception as e:
            logger.error(f"❌ Dependency check failed: {e}")
            return {"status": "error", "error": str(e), "vulnerabilities": []}

    async def _check_python_deps(self, repo_path: str) -> list[dict[str, Any]]:
        """Check Python dependencies using pip-audit"""
        vulns = []
        try:
            req_file = Path(repo_path) / "requirements.txt"
            if req_file.exists():
                result = subprocess.run(
                    ["pip-audit", "-r", str(req_file), "-f", "json"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

                if result.stdout:
                    audit_results = json.loads(result.stdout)
                    for vuln in audit_results.get("vulnerabilities", []):
                        vulns.append(
                            {
                                "package": vuln.get("name"),
                                "version": vuln.get("version"),
                                "vulnerability_id": vuln.get("id"),
                                "description": vuln.get("description"),
                                "fixed_version": vuln.get("fix_versions", [None])[0],
                            }
                        )
                    logger.info(f"📦 Found {len(vulns)} dependency issues")
        except FileNotFoundError:
            logger.warning("⚠️  pip-audit not installed")
        except Exception as e:
            logger.warning(f"⚠️  Python dependency check failed: {e}")

        return vulns


class ReportGeneratorAgent:
    """✍️ WRITE Agent - Generates comprehensive audit reports"""

    def __init__(self):
        self.name = "ReportGeneratorAgent"

    async def execute(
        self,
        repo_url: str,
        scan_result: dict[str, Any],
        analysis_result: dict[str, Any],
        dependency_result: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate comprehensive security report"""
        logger.info(f"📝 [WRITE] Generating report for: {repo_url}")

        try:
            parts = repo_url.rstrip("/").split("/")
            owner = parts[-2]
            name = parts[-1].replace(".git", "")

            repo_info = RepositoryInfo(
                url=repo_url,
                name=name,
                owner=owner,
                language="Python",
                is_private=False,
                branch=scan_result.get("branch", "main"),
                commit_sha=scan_result.get("commit_sha"),
                clone_timestamp=datetime.now(UTC),
            )

            findings = self._process_findings(analysis_result.get("findings", []))
            summary = self._calculate_summary(
                findings,
                dependency_result.get("vulnerabilities", []),
                scan_result.get("files_count", 0),
            )

            report = AuditReport(
                audit_id=f"audit_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}",
                repository=repo_info,
                summary=summary,
                findings=findings,
                recommendations=self._generate_recommendations(findings, summary),
            )

            logger.info(f"✅ Report generated: {report.audit_id}")
            return {
                "status": "success",
                "report": report.model_dump(mode="json"),
                "report_id": report.audit_id,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        except Exception as e:
            logger.error(f"❌ Report generation failed: {e}")
            return {"status": "error", "error": str(e)}

    def _process_findings(self, raw_findings: list[dict[str, Any]]) -> list[Finding]:
        """Convert raw findings to Finding objects"""
        findings = []
        for i, raw in enumerate(raw_findings):
            try:
                severity = self._map_severity(raw.get("severity", "LOW"))
                finding = Finding(
                    finding_id=f"finding_{i:04d}",
                    type=FindingType.OTHER,
                    severity=severity,
                    title=raw.get("issue_type", "Security Issue"),
                    description=raw.get("message", ""),
                    file_path=raw.get("file"),
                    line_number=raw.get("line"),
                    code_snippet=raw.get("code"),
                    recommendation="Review and fix this security issue",
                    tool_source=raw.get("type", "unknown"),
                )
                findings.append(finding)
            except Exception as e:
                logger.warning(f"Failed to process finding: {e}")

        return findings

    def _map_severity(self, severity: str) -> SeverityLevel:
        """Map string severity to SeverityLevel"""
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
        vulnerabilities: list[dict[str, Any]],
        files_count: int,
    ) -> AuditSummary:
        """Calculate summary statistics"""
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
        summary.risk_score = min(10.0, (summary.critical * 2 + summary.high) / 2)
        return summary

    def _generate_recommendations(
        self,
        findings: list[Finding],
        summary: AuditSummary,
    ) -> list[str]:
        """Generate security recommendations"""
        recommendations = []

        if summary.critical > 0:
            recommendations.append(
                "⚠️  URGENT: Address all critical findings immediately"
            )
        if summary.high > 0:
            recommendations.append(
                "🔴 High priority: Fix high-severity vulnerabilities within 1 week"
            )
        if summary.vulnerable_dependencies > 0:
            recommendations.append(
                f"📦 Update {summary.vulnerable_dependencies} vulnerable dependencies"
            )

        recommendations.extend(
            [
                "✅ Implement security code review process",
                "✅ Enable automated security scanning in CI/CD",
                "✅ Add security testing to development workflow",
                "✅ Regular dependency updates and vulnerability monitoring",
            ]
        )

        return recommendations


class SecurityAuditorAgent:
    """🔒 ROMA Orchestrator - Main security audit agent"""

    def __init__(self):
        self.name = "SecurityAuditorAgent"
        self.scanner = RepositoryScannerAgent()
        self.analyzer = StaticAnalysisAgent()
        self.dependency_checker = DependencyCheckerAgent()
        self.report_generator = ReportGeneratorAgent()

    async def audit(self, repo_url: str, branch: str = "main") -> AuditReport:
        """Execute recursive security audit using ROMA pattern"""
        logger.info(f"\n🔒 {'='*60}")
        logger.info(f"🔒 STARTING SECURITY AUDIT: {repo_url}")
        logger.info(f"🔒 {'='*60}\n")

        try:
            # Phase 1: Repository Scanning (SEARCH Operation)
            logger.info("📋 Phase 1: Repository Scanning (SEARCH)")
            scan_result = await self.scanner.execute(repo_url, branch)
            if scan_result["status"] != "success":
                raise Exception(f"Repository scan failed: {scan_result.get('error')}")
            repo_path = scan_result["clone_path"]

            # Phase 2: Static Analysis (THINK Operation)
            logger.info("📋 Phase 2: Static Analysis (THINK)")
            analysis_result = await self.analyzer.execute(repo_path)
            if analysis_result["status"] != "success":
                logger.warning(
                    "Static analysis had issues: %s",
                    analysis_result.get("error"),
                )

            # Phase 3: Dependency Checking (SEARCH Operation)
            logger.info("📋 Phase 3: Dependency Checking (SEARCH)")
            dependency_result = await self.dependency_checker.execute(repo_path)
            if dependency_result["status"] != "success":
                logger.warning(
                    "Dependency check had issues: %s",
                    dependency_result.get("error"),
                )

            # Phase 4: Report Generation (WRITE Operation)
            logger.info("📋 Phase 4: Report Generation (WRITE)")
            report_result = await self.report_generator.execute(
                repo_url, scan_result, analysis_result, dependency_result
            )
            if report_result["status"] != "success":
                raise Exception(
                    f"Report generation failed: {report_result.get('error')}"
                )

            # Save report
            report_data = report_result["report"]
            report_path = config.reports_dir / f"{report_result['report_id']}.json"
            with open(report_path, "w") as f:
                json.dump(report_data, f, indent=2, default=str)

            logger.info(f"\n✅ {'='*60}")
            logger.info("✅ AUDIT COMPLETE!")
            logger.info(f"✅ Report saved to: {report_path}")
            logger.info(f"✅ {'='*60}\n")

            return AuditReport(**report_data)

        except Exception as e:
            logger.error(f"\n❌ {'='*60}")
            logger.error(f"❌ AUDIT FAILED: {e}")
            logger.error(f"❌ {'='*60}\n")
            raise


async def main():
    """Main entry point for testing"""
    agent = SecurityAuditorAgent()
    
    # Example: Audit a repository
    repo_url = "https://github.com/example/repo"
    try:
        report = await agent.audit(repo_url)
        print(
            "\n📊 Audit Report:\n"
            f"{json.dumps(report.model_dump(mode='json'), indent=2, default=str)}"
        )
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
