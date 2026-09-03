# Security Auditor (Phase 1)

Security auditing package for ROMA with CLI execution, typed reports, and agent-based analysis.

## Run

```bash
pip install -e .
python -m security_auditor --repo https://github.com/example/repo.git
security-audit --repo https://github.com/example/repo.git --format markdown
```

## Development

```bash
make install
make test
make lint
make audit
```
