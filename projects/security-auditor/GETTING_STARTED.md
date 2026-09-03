# Security Auditor - Getting Started

## 1) Prerequisites

- Python 3.12+
- Git

## 2) Install

```bash
cd /home/runner/work/ROMA/ROMA/projects/security-auditor
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .[dev]
```

## 3) Run your first audit

```bash
python src/audit.py --repo https://github.com/example/repo --branch main
```

You can print the full report as JSON:

```bash
python src/audit.py --repo https://github.com/example/repo --branch main --json
```

You can save the report to a file:

```bash
python src/audit.py \
  --repo https://github.com/example/repo \
  --branch main \
  --output reports/audit-report.json
```

## 4) Help command

```bash
python src/audit.py --help
```

## 5) Run tests

```bash
pytest tests -q
```

Integration test (real public repository):

```bash
RUN_SECURITY_AUDITOR_INTEGRATION=1 pytest tests/test_integration_audit.py -q
```

## 6) Architecture

- `src/audit.py`: CLI entry point
- `src/agents.py`: orchestrator and security agents
- `src/logging.py`: structured logging
- `src/config.py`: environment-based configuration
- `src/models.py`: Pydantic data models
- `tests/`: unit and integration tests
- `examples/`: runnable usage examples
