# Getting Started - Security Auditor

## Installation

```bash
cd projects/security-auditor
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

```bash
python -m security_auditor --repo https://github.com/example/repo.git
security-audit --repo https://github.com/example/repo.git --format markdown
```

## Configuration

Environment variables:

- `SECURITY_AUDITOR_BASE_DIR`
- `SECURITY_AUDITOR_TEMP_DIR`
- `SECURITY_AUDITOR_REPORTS_DIR`
- `SECURITY_AUDITOR_LOG_FILE`
- `SECURITY_AUDITOR_ENABLE_BANDIT`
- `SECURITY_AUDITOR_ENABLE_SEMGREP`

## Troubleshooting

- Ensure `git` is installed and repository URL is reachable.
- Optional scanners (`bandit`, `semgrep`, `pip-audit`) can be installed for deeper checks.
- Check `reports/audit.log` for detailed logs.

## Examples

See `examples/README.md` and run scripts under `examples/`.
