# Security Auditor Getting Started

## Installation Instructions

From `/home/runner/work/ROMA/ROMA/projects/security-auditor`:

```bash
python -m pip install -e '.[dev]'
```

Optional scanners for deeper checks:

```bash
python -m pip install bandit pip-audit
# semgrep installation is optional and can be added separately if needed
```

## Quick Start (5 Minutes)

1. Change into `projects/security-auditor`.
2. Install the package with development extras.
3. Run `python -m src.audit --repo https://github.com/pallets/flask`.
4. Open the generated JSON report in `reports/`.

## Configuration Guide

Environment variables:

- `SECURITY_AUDITOR_PROJECT_ROOT`
- `SECURITY_AUDITOR_TEMP_DIR`
- `SECURITY_AUDITOR_REPORTS_DIR`
- `SECURITY_AUDITOR_LOG_DIR`
- `SECURITY_AUDITOR_ENABLE_BANDIT`
- `SECURITY_AUDITOR_ENABLE_SEMGREP`
- `SECURITY_AUDITOR_TIMEOUT`
- `SECURITY_AUDITOR_PARALLEL`

## Running Your First Audit

```bash
python -m src.audit --repo https://github.com/pallets/flask --branch main
```

Common options:

```bash
python -m src.audit --repo https://github.com/pallets/flask --output-format both --parallel
python -m src.audit --repo https://github.com/pallets/flask --log-level DEBUG --timeout 180
```

## Understanding the Report

Each report includes:

- repository metadata
- agent execution status
- findings from static analysis
- dependency vulnerabilities
- remediation recommendations
- summary counts and risk score

## CLI Options Reference

- `--repo` required repository URL
- `--branch` branch to audit
- `-v/--verbose` verbose logging
- `--debug` debug logging
- `--output-format` `json`, `markdown`, or `both`
- `-o/--output` output file or directory
- `--log-level` `DEBUG`, `INFO`, `WARNING`, or `ERROR`
- `--log-file` custom JSON log path
- `--timeout` audit timeout in seconds
- `--parallel` / `--no-parallel` toggle parallel execution

## Examples

See `/home/runner/work/ROMA/ROMA/projects/security-auditor/examples/README.md` for runnable examples.

## Troubleshooting

- If cloning fails, confirm the repository URL and branch exist.
- If no findings appear, install optional tools such as Bandit, pip-audit, and Semgrep.
- If permissions errors occur, override report and log directories with environment variables.
- If the audit times out, increase `--timeout` or disable parallel execution for debugging.
