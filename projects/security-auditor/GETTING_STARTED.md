# Security Auditor - Getting Started

## Installation

```bash
cd projects/security-auditor
pip install -e .[dev]
```

## Quick Start

```bash
python src/audit.py --repo https://github.com/pallets/itsdangerous
python src/audit.py --repo https://github.com/pallets/itsdangerous --branch main --output json
python -m src --repo https://github.com/pallets/itsdangerous
```

## Configuration

Copy `.env.example` values into your environment:

- `SECURITY_AUDITOR_REPORTS_DIR`
- `SECURITY_AUDITOR_TEMP_DIR`
- `SECURITY_AUDITOR_LOG_LEVEL`
- `SECURITY_AUDITOR_ENABLE_BANDIT`
- `SECURITY_AUDITOR_ENABLE_SEMGREP`

## Troubleshooting

- If `bandit`, `semgrep`, or `pip-audit` are not installed, scans continue and log warnings.
- Use `make test` for quick validation.
- Set `RUN_INTEGRATION_TESTS=1` to run integration tests.
