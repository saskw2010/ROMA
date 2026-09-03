# Security Auditor

Phase 1 security auditor for ROMA.

## Quick Commands

```bash
cd /home/runner/work/ROMA/ROMA/projects/security-auditor
python -m pip install -e '.[dev]'
python -m src.audit --repo https://github.com/pallets/flask
```

Reports are written to `projects/security-auditor/reports/` by default.
