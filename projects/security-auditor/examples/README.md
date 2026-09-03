# Security Auditor Examples

## Files

- `basic_audit.py` - runs a simple JSON audit.
- `advanced_audit.py` - enables verbose logging, markdown output, and custom paths.
- `batch_audit.py` - audits multiple repositories concurrently.

## Usage

From `/home/runner/work/ROMA/ROMA/projects/security-auditor`:

```bash
python examples/basic_audit.py
python examples/advanced_audit.py
python examples/batch_audit.py
```

Each example saves reports to the local `reports/` directory unless a custom output path is provided.
