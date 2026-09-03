from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class SeverityLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class FindingType(str, Enum):
    COMMAND_INJECTION = "COMMAND_INJECTION"
    SQL_INJECTION = "SQL_INJECTION"
    PATH_TRAVERSAL = "PATH_TRAVERSAL"
    XSS = "XSS"
    SSRF = "SSRF"
    INSECURE_DESERIALIZATION = "INSECURE_DESERIALIZATION"
    WEAK_CRYPTO = "WEAK_CRYPTO"
    HARD_CODED_SECRET = "HARD_CODED_SECRET"
    AUTHENTICATION = "AUTHENTICATION"
    AUTHORIZATION = "AUTHORIZATION"
    DEPENDENCY = "DEPENDENCY"
    MISCONFIGURATION = "MISCONFIGURATION"
    DATA_EXPOSURE = "DATA_EXPOSURE"
    OTHER = "OTHER"


class RepositoryInfo(BaseModel):
    url: str
    name: str
    owner: str
    language: str = "Unknown"
    is_private: bool = False
    branch: str = "main"
    commit_sha: Optional[str] = None
    clone_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Finding(BaseModel):
    finding_id: str
    type: FindingType = FindingType.OTHER
    severity: SeverityLevel = SeverityLevel.LOW
    title: str
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    recommendation: Optional[str] = None
    tool_source: Optional[str] = None


class DependencyVulnerability(BaseModel):
    package: str
    version: Optional[str] = None
    vulnerability_id: str
    description: Optional[str] = None
    fixed_version: Optional[str] = None


class AuditSummary(BaseModel):
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
    audit_id: str
    repository: RepositoryInfo
    summary: AuditSummary
    findings: List[Finding] = Field(default_factory=list)
    dependency_vulnerabilities: List[DependencyVulnerability] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
