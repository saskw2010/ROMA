import pytest

from src.agents import (
    DependencyCheckerAgent,
    ReportGeneratorAgent,
    SecurityAuditorAgent,
    StaticAnalysisAgent,
)


def test_agent_initialization():
    agent = SecurityAuditorAgent()
    assert agent.scanner is not None
    assert isinstance(agent.analyzer, StaticAnalysisAgent)
    assert isinstance(agent.dependency_checker, DependencyCheckerAgent)
    assert isinstance(agent.report_generator, ReportGeneratorAgent)


@pytest.mark.asyncio
async def test_report_generator_builds_report(sample_finding):
    generator = ReportGeneratorAgent()

    result = await generator.execute(
        repo_url="https://github.com/example/repo.git",
        scan_result={"branch": "main", "commit_sha": "abc123", "files_count": 1},
        analysis_result={
            "findings": [
                {
                    "type": "bandit",
                    "severity": "HIGH",
                    "issue_type": sample_finding.title,
                    "message": sample_finding.description,
                    "file": sample_finding.file_path,
                    "line": sample_finding.line_number,
                }
            ]
        },
        dependency_result={"vulnerabilities": []},
    )

    assert result["status"] == "success"
    assert result["report"]["summary"]["high"] == 1


@pytest.mark.asyncio
async def test_static_analysis_handles_invalid_json(monkeypatch, mock_repo_dir):
    analyzer = StaticAnalysisAgent()

    class FakeResult:
        stdout = "{invalid"

    def fake_run(*args, **kwargs):
        return FakeResult()

    monkeypatch.setattr("src.agents.subprocess.run", fake_run)
    findings = await analyzer._run_bandit(str(mock_repo_dir))
    assert findings == []
