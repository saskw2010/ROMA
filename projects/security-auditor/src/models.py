"""Data models for security auditing."""

from datetime import datetime
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
    CODE = "CODE"
    DEPENDENCY = "DEPENDENCY"
    CONFIG = "CONFIG"
    OTHER = "OTHER"


class DependencyVulnerability(BaseModel):
    package: str
    version: str
    vulnerability_id: str
    description: str = ""
    fixed_version: Optional[str] = None


class Finding(BaseModel):
    finding_id: str
    type: FindingType
    severity: SeverityLevel
    title: str
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    recommendation: str = ""
    tool_source: str = ""


class RepositoryInfo(BaseModel):
    url: str
    name: str
    owner: str
    language: str = "unknown"
    is_private: bool = False
    branch: str = "main"
    commit_sha: Optional[str] = None
    clone_timestamp: datetime = Field(default_factory=datetime.utcnow)


class AuditSummary(BaseModel):
    total_findings: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0
    files_scanned: int = 0
    vulnerable_dependencies: int = 0
    risk_score: float = 0.0


class AuditReport(BaseModel):
    audit_id: str
    repository: RepositoryInfo
    summary: AuditSummary
    findings: List[Finding] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_markdown(self) -> str:
        summary = self.summary
        lines = [
            f"# Security Audit Report - {self.repository.owner}/{self.repository.name}",
            "",
            f"- **Audit ID:** {self.audit_id}",
            f"- **Repository:** {self.repository.url}",
            f"- **Branch:** {self.repository.branch}",
            f"- **Commit:** {self.repository.commit_sha or 'N/A'}",
            f"- **Generated:** {self.generated_at.isoformat()}",
            "",
            "## Summary",
            f"- Total Findings: {summary.total_findings}",
            f"- Critical: {summary.critical}",
            f"- High: {summary.high}",
            f"- Medium: {summary.medium}",
            f"- Low: {summary.low}",
            f"- Info: {summary.info}",
            f"- Vulnerable Dependencies: {summary.vulnerable_dependencies}",
            f"- Risk Score: {summary.risk_score}",
            "",
            "## Findings",
        ]

        if not self.findings:
            lines.append("No findings detected.")
        else:
            for finding in self.findings:
                location = (
                    f" ({finding.file_path}:{finding.line_number})"
                    if finding.file_path
                    else ""
                )
                lines.extend(
                    [
                        f"### [{finding.severity}] {finding.title}{location}",
                        finding.description,
                        f"- Recommendation: {finding.recommendation}",
                        "",
                    ]
                )

        if self.recommendations:
            lines.append("## Recommendations")
            lines.extend([f"- {item}" for item in self.recommendations])

        return "\n".join(lines).strip() + "\n"
