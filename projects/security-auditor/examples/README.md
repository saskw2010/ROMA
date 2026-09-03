# Security Auditor Examples

## Available examples

- `basic_audit.py`: Runs one repository audit and prints summary.
- `custom_analysis.py`: Shows custom environment configuration and filtered analysis.
- `batch_audit.py`: Audits multiple repositories in parallel and aggregates results.

## Run examples

```bash
cd projects/security-auditor
python examples/basic_audit.py
python examples/custom_analysis.py
python examples/batch_audit.py
```

## Expected output

Each example prints report progress and a final summary. Reports are written under `reports/` when audits succeed.
