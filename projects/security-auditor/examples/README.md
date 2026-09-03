# Security Auditor Examples

## CLI quick start

```bash
cd projects/security-auditor
python src/audit.py --repo https://github.com/example/repo --branch main
python src/audit.py --help
```

## Save output report

```bash
python src/audit.py \
  --repo https://github.com/example/repo \
  --branch main \
  --json \
  --output reports/example-report.json
```

## Python API example

```bash
python examples/run_audit.py
```
