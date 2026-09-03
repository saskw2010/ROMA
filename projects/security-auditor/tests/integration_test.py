from src.agents import SecurityAuditorAgent


async def _fake_scan(self, repo_url, branch="main"):
    return {
        "status": "success",
        "repo_url": repo_url,
        "clone_path": "/tmp/repo",
        "commit_sha": "abc123",
        "branch": branch,
        "files_count": 3,
    }


async def _fake_analysis(self, repo_path):
    return {
        "status": "success",
        "findings": [
            {
                "type": "bandit",
                "severity": "LOW",
                "issue_type": "B101",
                "message": "assert used",
                "file": "app.py",
                "line": 1,
            }
        ],
    }


async def _fake_deps(self, repo_path):
    return {"status": "success", "vulnerabilities": []}


def test_end_to_end_workflow(monkeypatch):
    agent = SecurityAuditorAgent()
    monkeypatch.setattr(
        agent.scanner, "execute", _fake_scan.__get__(agent.scanner, type(agent.scanner))
    )
    monkeypatch.setattr(
        agent.analyzer,
        "execute",
        _fake_analysis.__get__(agent.analyzer, type(agent.analyzer)),
    )
    monkeypatch.setattr(
        agent.dependency_checker,
        "execute",
        _fake_deps.__get__(agent.dependency_checker, type(agent.dependency_checker)),
    )

    import asyncio

    report = asyncio.run(agent.audit("https://github.com/example/repo.git"))
    assert report.summary.total_findings == 1
    assert report.repository.name == "repo"
