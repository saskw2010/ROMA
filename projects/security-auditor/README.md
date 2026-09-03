# Security Auditor

Phase 1 security audit workflow for ROMA-based multi-agent repository analysis.

## What it includes

- `SecurityAuditorAgent` orchestrator
- Repository scanning
- Static analysis via Bandit and Semgrep
- Dependency checks via `pip-audit`
- JSON report generation
- Runnable CLI entry point

## Getting started

```bash
cd /home/runner/work/ROMA/ROMA
python -m pip install -r projects/security-auditor/requirements.txt
python projects/security-auditor/src/audit.py https://github.com/example/repo --branch main
```

Reports are written to `projects/security-auditor/reports/` by default.

## Configuration

Copy `.env.example` values into your environment as needed:

- `SECURITY_AUDITOR_TEMP_DIR`
- `SECURITY_AUDITOR_REPORTS_DIR`
- `SECURITY_AUDITOR_ENABLE_BANDIT`
- `SECURITY_AUDITOR_ENABLE_SEMGREP`
- `SECURITY_AUDITOR_ENABLE_PIP_AUDIT`

## Example

```bash
python projects/security-auditor/src/audit.py \
  https://github.com/pallets/flask \
  --branch main \
  --output /tmp/flask-audit.json
```
