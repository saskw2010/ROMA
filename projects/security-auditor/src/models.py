"""Pydantic models for the security auditor."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class SeverityLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class FindingType(str, Enum):
    SECRET = "secret"
    INJECTION = "injection"
    DEPENDENCY = "dependency"
    MISCONFIGURATION = "misconfiguration"
    OTHER = "other"


class DependencyVulnerability(BaseModel):
    package: str
    version: str | None = None
    vulnerability_id: str
    description: str | None = None
    fixed_version: str | None = None


class Finding(BaseModel):
    finding_id: str
    type: FindingType = FindingType.OTHER
    severity: SeverityLevel
    title: str
    description: str
    file_path: str | None = None
    line_number: int | None = None
    code_snippet: str | None = None
    recommendation: str | None = None
    tool_source: str | None = None

    @field_validator("line_number")
    @classmethod
    def validate_line_number(cls, value: int | None) -> int | None:
        if value is not None and value < 1:
            raise ValueError("line_number must be positive")
        return value


class AuditSummary(BaseModel):
    total_findings: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0
    vulnerable_dependencies: int = 0
    files_scanned: int = 0
    risk_score: float = 0.0

    @field_validator("risk_score")
    @classmethod
    def validate_risk_score(cls, value: float) -> float:
        if not 0 <= value <= 10:
            raise ValueError("risk_score must be between 0 and 10")
        return value


class RepositoryInfo(BaseModel):
    url: str
    name: str
    owner: str
    language: str | None = None
    is_private: bool = False
    branch: str = "main"
    commit_sha: str | None = None
    clone_timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AuditReport(BaseModel):
    audit_id: str
    repository: RepositoryInfo
    summary: AuditSummary
    findings: list[Finding] = Field(default_factory=list)
    dependency_vulnerabilities: list[DependencyVulnerability] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    agent_statuses: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
