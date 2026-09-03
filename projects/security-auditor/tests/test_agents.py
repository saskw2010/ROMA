"""Agent initialization and CLI/report tests."""

from __future__ import annotations

import json
import runpy
import subprocess
from pathlib import Path

import pytest

from src import agents as agents_module
from src import audit as audit_module
from src.agents import (
    DependencyCheckerAgent,
    ReportGeneratorAgent,
    RepositoryScannerAgent,
    SecurityAuditorAgent,
    StaticAnalysisAgent,
)
from src.models import (
    AuditReport,
    AuditSummary,
    Finding,
    FindingType,
    RepositoryInfo,
    SeverityLevel,
)


def test_agent_initialization():
    assert RepositoryScannerAgent().name == "RepositoryScannerAgent"
    assert StaticAnalysisAgent().name == "StaticAnalysisAgent"
    assert DependencyCheckerAgent().name == "DependencyCheckerAgent"
    assert ReportGeneratorAgent().name == "ReportGeneratorAgent"


@pytest.mark.asyncio
async def test_security_auditor_initialization_only():
    auditor = SecurityAuditorAgent()
    assert auditor.scanner.name == "RepositoryScannerAgent"
    assert auditor.analyzer.name == "StaticAnalysisAgent"
    assert auditor.dependency_checker.name == "DependencyCheckerAgent"
    assert auditor.report_generator.name == "ReportGeneratorAgent"


@pytest.mark.asyncio
async def test_repository_scanner_execute_success(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(agents_module.config, "temp_dir", tmp_path)

    def fake_run(cmd, **kwargs):
        if cmd[:2] == ["git", "clone"]:
            clone_path = Path(cmd[-1])
            clone_path.mkdir(parents=True, exist_ok=True)
            (clone_path / "README.md").write_text("hello", encoding="utf-8")
            return subprocess.CompletedProcess(cmd, 0)
        if cmd[:3] == ["git", "rev-parse", "HEAD"]:
            return subprocess.CompletedProcess(cmd, 0, stdout="deadbeef\n")
        raise AssertionError(f"Unexpected command: {cmd}")

    monkeypatch.setattr(agents_module.subprocess, "run", fake_run)

    result = await RepositoryScannerAgent().execute(
        "https://github.com/example/repo.git",
        "main",
    )

    assert result["status"] == "success"
    assert result["commit_sha"] == "deadbeef"
    assert result["files_count"] == 1
    assert result["files"][0]["path"] == "README.md"


@pytest.mark.asyncio
async def test_repository_scanner_execute_error(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(agents_module.config, "temp_dir", tmp_path)

    def fake_run(cmd, **kwargs):
        raise subprocess.CalledProcessError(returncode=1, cmd=cmd)

    monkeypatch.setattr(agents_module.subprocess, "run", fake_run)

    result = await RepositoryScannerAgent().execute(
        "https://github.com/example/repo.git",
        "main",
    )

    assert result["status"] == "error"
    assert "returned non-zero exit status" in result["error"]


@pytest.mark.asyncio
async def test_repository_scanner_removes_existing_clone(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(agents_module.config, "temp_dir", tmp_path)
    existing = tmp_path / "repo"
    existing.mkdir()
    (existing / "stale.txt").write_text("stale", encoding="utf-8")

    def fake_run(cmd, **kwargs):
        if cmd[:2] == ["git", "clone"]:
            clone_path = Path(cmd[-1])
            clone_path.mkdir(parents=True, exist_ok=True)
            (clone_path / "fresh.txt").write_text("fresh", encoding="utf-8")
            return subprocess.CompletedProcess(cmd, 0)
        if cmd[:3] == ["git", "rev-parse", "HEAD"]:
            return subprocess.CompletedProcess(cmd, 0, stdout="cafebabe\n")
        raise AssertionError(f"Unexpected command: {cmd}")

    monkeypatch.setattr(agents_module.subprocess, "run", fake_run)

    result = await RepositoryScannerAgent().execute(
        "https://github.com/example/repo.git",
        "main",
    )

    assert result["status"] == "success"
    assert not (existing / "stale.txt").exists()


@pytest.mark.asyncio
async def test_static_analysis_execute_parses_bandit_and_semgrep(monkeypatch):
    monkeypatch.setattr(agents_module.config, "enable_bandit", True)
    monkeypatch.setattr(agents_module.config, "enable_semgrep", True)

    def fake_run(cmd, **kwargs):
        if cmd[0] == "bandit":
            return subprocess.CompletedProcess(
                cmd,
                0,
                stdout=json.dumps(
                    {
                        "results": [
                            {
                                "severity": "HIGH",
                                "test_id": "B105",
                                "issue_text": "Hardcoded password",
                                "filename": "app.py",
                                "line_number": 7,
                                "code": "password = 'x'",
                            }
                        ]
                    }
                ),
            )
        if cmd[0] == "semgrep":
            return subprocess.CompletedProcess(
                cmd,
                0,
                stdout=json.dumps(
                    {
                        "results": [
                            {
                                "severity": "MEDIUM",
                                "rule_id": "python.lang.security.audit",
                                "message": "Suspicious use",
                                "path": "app.py",
                                "start": {"line": 9},
                            }
                        ]
                    }
                ),
            )
        raise AssertionError(f"Unexpected command: {cmd}")

    monkeypatch.setattr(agents_module.subprocess, "run", fake_run)

    result = await StaticAnalysisAgent().execute("/tmp/repo")

    assert result["status"] == "success"
    assert result["total_findings"] == 2
    assert {item["type"] for item in result["findings"]} == {"bandit", "semgrep"}


@pytest.mark.asyncio
async def test_static_analysis_execute_error(monkeypatch):
    monkeypatch.setattr(agents_module.config, "enable_bandit", True)
    monkeypatch.setattr(agents_module.config, "enable_semgrep", False)

    agent = StaticAnalysisAgent()

    async def failing_bandit(repo_path: str):
        raise RuntimeError("bandit exploded")

    monkeypatch.setattr(agent, "_run_bandit", failing_bandit)

    result = await agent.execute("/tmp/repo")

    assert result["status"] == "error"
    assert result["findings"] == []


@pytest.mark.asyncio
async def test_static_analysis_handles_missing_tools(monkeypatch):
    def missing_tool(*args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(agents_module.subprocess, "run", missing_tool)

    agent = StaticAnalysisAgent()

    assert await agent._run_bandit("/tmp/repo") == []
    assert await agent._run_semgrep("/tmp/repo") == []


@pytest.mark.asyncio
async def test_dependency_checker_parses_pip_audit(monkeypatch, tmp_path: Path):
    (tmp_path / "requirements.txt").write_text("pydantic==2.8.0\n", encoding="utf-8")

    def fake_run(cmd, **kwargs):
        return subprocess.CompletedProcess(
            cmd,
            0,
            stdout=json.dumps(
                {
                    "vulnerabilities": [
                        {
                            "name": "pydantic",
                            "version": "2.8.0",
                            "id": "PYSEC-0001",
                            "description": "Example vulnerability",
                            "fix_versions": ["2.8.1"],
                        }
                    ]
                }
            ),
        )

    monkeypatch.setattr(agents_module.subprocess, "run", fake_run)

    result = await DependencyCheckerAgent().execute(str(tmp_path))

    assert result["status"] == "success"
    assert result["total_vulnerabilities"] == 1
    assert result["vulnerabilities"][0]["package"] == "pydantic"


@pytest.mark.asyncio
async def test_dependency_checker_execute_error(monkeypatch):
    agent = DependencyCheckerAgent()

    async def failing_check(repo_path: str):
        raise RuntimeError("pip-audit exploded")

    monkeypatch.setattr(agent, "_check_python_deps", failing_check)

    result = await agent.execute("/tmp/repo")

    assert result["status"] == "error"
    assert result["vulnerabilities"] == []


def test_report_generator_processes_findings_and_summary():
    report_generator = ReportGeneratorAgent()

    findings = report_generator._process_findings(
        [
            {
                "type": "bandit",
                "severity": "CRITICAL",
                "issue_type": "B999",
                "message": "Critical issue",
                "file": "app.py",
                "line": 12,
                "code": "danger()",
            },
            {
                "type": "bandit",
                "severity": "LOW",
                "issue_type": "B100",
                "message": "Bad line",
                "line": "not-an-int",
            },
        ]
    )
    summary = report_generator._calculate_summary(findings, [{"id": "vuln"}], 8)
    recommendations = report_generator._generate_recommendations(findings, summary)

    assert len(findings) == 1
    assert summary.critical == 1
    assert summary.vulnerable_dependencies == 1
    assert any("URGENT" in item for item in recommendations)


@pytest.mark.asyncio
async def test_report_generator_execute_success():
    result = await ReportGeneratorAgent().execute(
        "https://github.com/example/repo",
        {
            "branch": "main",
            "commit_sha": "abc123",
            "files_count": 4,
        },
        {
            "findings": [
                {
                    "type": "bandit",
                    "severity": "HIGH",
                    "issue_type": "B105",
                    "message": "Hardcoded password",
                    "file": "app.py",
                    "line": 7,
                }
            ]
        },
        {"vulnerabilities": [{"id": "v1"}]},
    )

    assert result["status"] == "success"
    assert result["report"]["summary"]["high"] == 1
    assert result["report"]["summary"]["vulnerable_dependencies"] == 1


@pytest.mark.asyncio
async def test_report_generator_execute_invalid_repo_url():
    result = await ReportGeneratorAgent().execute(
        "invalid",
        {"branch": "main", "files_count": 1},
        {"findings": []},
        {"vulnerabilities": []},
    )

    assert result["status"] == "error"


@pytest.mark.asyncio
async def test_security_auditor_audit_success(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(agents_module.config, "reports_dir", tmp_path)

    async def fake_scan(repo_url: str, branch: str):
        return {
            "status": "success",
            "clone_path": "/tmp/repo",
            "branch": branch,
            "commit_sha": "abc123",
            "files_count": 2,
        }

    async def fake_analysis(repo_path: str):
        return {
            "status": "success",
            "findings": [
                {
                    "type": "bandit",
                    "severity": "HIGH",
                    "issue_type": "B105",
                    "message": "Hardcoded password",
                    "file": "app.py",
                    "line": 7,
                }
            ],
        }

    async def fake_dependencies(repo_path: str):
        return {
            "status": "success",
            "vulnerabilities": [],
        }

    async def fake_report(repo_url, scan_result, analysis_result, dependency_result):
        return {
            "status": "success",
            "report_id": "audit_test",
            "report": {
                "audit_id": "audit_test",
                "repository": {
                    "url": repo_url,
                    "name": "repo",
                    "owner": "example",
                    "language": "Python",
                    "is_private": False,
                    "branch": scan_result["branch"],
                    "commit_sha": scan_result["commit_sha"],
                    "clone_timestamp": "2026-01-01T00:00:00Z",
                },
                "summary": {
                    "files_scanned": 2,
                    "total_findings": 1,
                    "critical": 0,
                    "high": 1,
                    "medium": 0,
                    "low": 0,
                    "info": 0,
                    "vulnerable_dependencies": 0,
                    "risk_score": 0.5,
                },
                "findings": [],
                "recommendations": ["Fix high severity issues"],
            },
        }

    auditor = SecurityAuditorAgent()
    monkeypatch.setattr(auditor.scanner, "execute", fake_scan)
    monkeypatch.setattr(auditor.analyzer, "execute", fake_analysis)
    monkeypatch.setattr(auditor.dependency_checker, "execute", fake_dependencies)
    monkeypatch.setattr(auditor.report_generator, "execute", fake_report)

    report = await auditor.audit("https://github.com/example/repo", "main")

    assert report.audit_id == "audit_test"
    assert (tmp_path / "audit_test.json").exists()


@pytest.mark.asyncio
async def test_security_auditor_audit_scan_failure(monkeypatch):
    auditor = SecurityAuditorAgent()

    async def fake_scan(repo_url: str, branch: str):
        return {"status": "error", "error": "clone failed"}

    monkeypatch.setattr(auditor.scanner, "execute", fake_scan)

    with pytest.raises(Exception, match="Repository scan failed"):
        await auditor.audit("https://github.com/example/repo", "main")


def test_render_markdown_without_findings():
    report = AuditReport(
        audit_id="audit_empty",
        repository=RepositoryInfo(
            url="https://github.com/example/repo",
            name="repo",
            owner="example",
        ),
        summary=AuditSummary(files_scanned=1),
        recommendations=["Stay vigilant"],
    )

    rendered = audit_module._render_markdown(report)

    assert "No findings detected." in rendered


def test_audit_main_success(monkeypatch):
    async def fake_run_audit(repo: str, branch: str, output: str):
        return {}

    monkeypatch.setattr(audit_module, "run_audit", fake_run_audit)

    assert audit_module.main(["--repo", "https://github.com/example/repo"]) == 0


def test_audit_main_keyboard_interrupt(monkeypatch, capsys):
    async def fake_run_audit(repo: str, branch: str, output: str):
        raise KeyboardInterrupt

    monkeypatch.setattr(audit_module, "run_audit", fake_run_audit)

    assert audit_module.main(["--repo", "https://github.com/example/repo"]) == 130
    assert "Audit interrupted by user" in capsys.readouterr().out


@pytest.mark.asyncio
async def test_run_audit_writes_json_and_markdown(monkeypatch, tmp_path: Path):
    report = AuditReport(
        audit_id="audit_test",
        repository=RepositoryInfo(
            url="https://github.com/example/repo",
            name="repo",
            owner="example",
            commit_sha="abc123",
        ),
        summary=AuditSummary(
            files_scanned=3,
            total_findings=1,
            high=1,
            risk_score=0.5,
        ),
        findings=[
            Finding(
                finding_id="finding_1",
                type=FindingType.CODE,
                severity=SeverityLevel.HIGH,
                title="Issue",
                description="Description",
                recommendation="Fix it",
            )
        ],
        recommendations=["Rotate credentials"],
    )

    class StubAuditor:
        async def audit(self, repo: str, branch: str) -> AuditReport:
            return report

    monkeypatch.setattr(audit_module, "SecurityAuditorAgent", StubAuditor)
    monkeypatch.setattr(audit_module.config, "reports_dir", tmp_path)

    files = await audit_module.run_audit(
        "https://github.com/example/repo",
        "main",
        "both",
    )

    assert files["json"].exists()
    assert files["markdown"].exists()
    assert "Security Audit Report" in files["markdown"].read_text(encoding="utf-8")


def test_main_rejects_invalid_repo():
    assert audit_module.main(["--repo", "not-a-git-url"]) == 1


@pytest.mark.asyncio
async def test_agents_module_main_prints_report(monkeypatch, capsys):
    report = AuditReport(
        audit_id="audit_print",
        repository=RepositoryInfo(
            url="https://github.com/example/repo",
            name="repo",
            owner="example",
        ),
        summary=AuditSummary(files_scanned=1),
        recommendations=[],
    )

    async def fake_audit(self, repo_url: str, branch: str = "main"):
        return report

    monkeypatch.setattr(SecurityAuditorAgent, "audit", fake_audit)

    await agents_module.main()

    assert "audit_print" in capsys.readouterr().out


def test_package_main_module_executes(monkeypatch):
    monkeypatch.setattr(audit_module, "main", lambda: 0)

    with pytest.raises(SystemExit) as exc_info:
        runpy.run_module("src", run_name="__main__")

    assert exc_info.value.code == 0
