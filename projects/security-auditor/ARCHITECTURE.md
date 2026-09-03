# Security Auditor Architecture

## System design

The Phase 1 auditor follows a simple four-stage orchestrator:

1. **RepositoryScannerAgent** clones and inventories repository files.
2. **StaticAnalysisAgent** runs static tools (Bandit/Semgrep when enabled).
3. **DependencyCheckerAgent** checks Python dependencies (pip-audit when available).
4. **ReportGeneratorAgent** normalizes findings into typed report models.

`SecurityAuditorAgent` coordinates these stages and persists JSON reports under `reports/`.

## Agent flow

`audit.py` CLI parses inputs, configures logging, then invokes `SecurityAuditorAgent.audit()`.

## Data flow

Raw tool output -> normalized findings -> `AuditSummary` aggregation -> `AuditReport` serialization (JSON/Markdown).

## Integration points

- CLI: `python -m security_auditor` and `security-audit`
- CI: `.github/workflows/security-auditor-ci.yml`
- Test suite: `tests/` for config, model, agent, and integration checks
