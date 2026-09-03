from __future__ import annotations

from src.agents import (
    DependencyCheckerAgent,
    ReportGeneratorAgent,
    RepositoryScannerAgent,
    SecurityAuditorAgent,
    StaticAnalysisAgent,
)


def test_agent_initialization() -> None:
    orchestrator = SecurityAuditorAgent()

    assert orchestrator.name == "SecurityAuditorAgent"
    assert isinstance(orchestrator.scanner, RepositoryScannerAgent)
    assert isinstance(orchestrator.analyzer, StaticAnalysisAgent)
    assert isinstance(orchestrator.dependency_checker, DependencyCheckerAgent)
    assert isinstance(orchestrator.report_generator, ReportGeneratorAgent)
    assert orchestrator.last_run == {}
