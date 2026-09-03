from src.agents import (
    DependencyCheckerAgent,
    ReportGeneratorAgent,
    RepositoryScannerAgent,
    SecurityAuditorAgent,
    StaticAnalysisAgent,
)


def test_security_auditor_initializes_all_agents():
    orchestrator = SecurityAuditorAgent()

    assert isinstance(orchestrator.scanner, RepositoryScannerAgent)
    assert isinstance(orchestrator.analyzer, StaticAnalysisAgent)
    assert isinstance(orchestrator.dependency_checker, DependencyCheckerAgent)
    assert isinstance(orchestrator.report_generator, ReportGeneratorAgent)
