# Security Auditor (Phase 1)

Multi-agent security auditor that scans repositories, runs static checks, and generates JSON/Markdown reports.

## Quick run

```bash
cd projects/security-auditor
pip install -e .[dev]
python src/audit.py --repo https://github.com/pallets/itsdangerous
```

## CLI

```bash
python src/audit.py --repo REPO_URL --branch main --output json
python -m src --repo REPO_URL
```

See [GETTING_STARTED.md](./GETTING_STARTED.md) and [examples/README.md](./examples/README.md).
