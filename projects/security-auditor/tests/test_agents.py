"""Agent initialization and orchestration tests."""

from __future__ import annotations

import pytest

from src.agents import (
    DependencyCheckerAgent,
    ReportGeneratorAgent,
    RepositoryScannerAgent,
    SecurityAuditorAgent,
    StaticAnalysisAgent,
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
