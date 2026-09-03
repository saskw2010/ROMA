import pytest

from agents import ReportGeneratorAgent


@pytest.mark.asyncio
async def test_report_generation_from_scan_and_analysis_results():
    generator = ReportGeneratorAgent()

    scan_result = {"branch": "main", "commit_sha": "abc123", "files_count": 10}
    analysis_result = {
        "findings": [
            {
                "type": "bandit",
                "severity": "HIGH",
                "issue_type": "B602",
                "message": "subprocess call with shell=True",
                "file": "app.py",
                "line": 10,
            },
            {
                "type": "semgrep",
                "severity": "LOW",
                "issue_type": "RULE_1",
                "message": "weak hash function",
                "file": "utils.py",
                "line": 25,
            },
        ]
    }
    dependency_result = {"vulnerabilities": [{"package": "example", "version": "1.0.0"}]}

    result = await generator.execute(
        "https://github.com/example/repo", scan_result, analysis_result, dependency_result
    )

    assert result["status"] == "success"
    assert result["report"]["summary"]["total_findings"] == 2
    assert result["report"]["summary"]["high"] == 1
    assert result["report"]["summary"]["low"] == 1
    assert result["report"]["summary"]["vulnerable_dependencies"] == 1
