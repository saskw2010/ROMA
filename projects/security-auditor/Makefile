.PHONY: install test lint audit clean

install:
	pip install -e .[dev]

test:
	pytest -q tests

lint:
	ruff check --select E,F,I src tests examples security_auditor.py

audit:
	python src/audit.py --repo https://github.com/pallets/itsdangerous --output json

clean:
	rm -rf .pytest_cache .ruff_cache .tmp_audits reports/*.json reports/*.md reports/*.log
