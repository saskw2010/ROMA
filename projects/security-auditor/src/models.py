"""Pydantic models used by the security auditor."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl


class FindingType(str, Enum):
    """High-level finding categories."""

    CODE = "code"
    DEPENDENCY = "dependency"
    CONFIGURATION = "configuration"
    OTHER = "other"


class SeverityLevel(str, Enum):
    """Severity levels for findings."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class RepositoryInfo(BaseModel):
    """Repository metadata for a report."""

    url: HttpUrl
    name: str
    owner: str
    language: str = "Unknown"
    is_private: bool = False
    branch: str = "main"
    commit_sha: str | None = None
    clone_timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class DependencyVulnerability(BaseModel):
    """Dependency vulnerability details."""

    package: str
    version: str
    vulnerability_id: str
    description: str | None = None
    fixed_version: str | None = None


class Finding(BaseModel):
    """Single security finding."""

    finding_id: str
    type: FindingType
    severity: SeverityLevel
    title: str
    description: str
    file_path: str | None = None
    line_number: int | None = None
    code_snippet: str | None = None
    recommendation: str | None = None
    tool_source: str | None = None


class AuditSummary(BaseModel):
    """Summary metrics for an audit run."""

    files_scanned: int = 0
    total_findings: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0
    vulnerable_dependencies: int = 0
    risk_score: float = 0.0


class AuditReport(BaseModel):
    """Top-level security audit report."""

    audit_id: str
    repository: RepositoryInfo
    summary: AuditSummary
    findings: list[Finding] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
