import asyncio
import json
import sys
from pathlib import Path


PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(PROJECT_SRC))

import agents
import audit
import models


def test_dependency_checker_parses_pip_audit_records(monkeypatch):
    class Result:
        stdout = json.dumps(
            [
                {
                    "name": "demo",
                    "version": "1.0.0",
                    "vulns": [
                        {
                            "id": "GHSA-123",
                            "description": "Example vulnerability",
                            "fix_versions": ["1.0.1"],
                        }
                    ],
                }
            ]
        )

    monkeypatch.setattr(agents.subprocess, "run", lambda *args, **kwargs: Result())

    vulnerabilities = asyncio.run(agents.DependencyCheckerAgent()._check_python_deps(str(PROJECT_SRC.parent)))

    assert vulnerabilities == [
        {
            "package": "demo",
            "version": "1.0.0",
            "vulnerability_id": "GHSA-123",
            "description": "Example vulnerability",
            "fixed_version": "1.0.1",
        }
    ]


def test_cli_main_writes_output(monkeypatch, tmp_path):
    report = models.AuditReport(
        audit_id="audit_test",
        repository=models.RepositoryInfo(url="https://github.com/example/repo", name="repo", owner="example"),
        summary=models.AuditSummary(files_scanned=5),
    )

    async def fake_audit(self, repo_url, branch="main"):
        assert repo_url == "https://github.com/example/repo"
        assert branch == "develop"
        return report

    monkeypatch.setattr(audit.SecurityAuditorAgent, "audit", fake_audit)

    output_path = tmp_path / "report.json"
    exit_code = audit.main(
        ["https://github.com/example/repo", "--branch", "develop", "--output", str(output_path)]
    )

    assert exit_code == 0
    assert json.loads(output_path.read_text(encoding="utf-8"))["audit_id"] == "audit_test"
