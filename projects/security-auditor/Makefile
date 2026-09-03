.PHONY: help install test lint audit

help:
	@echo "Security Auditor commands"
	@echo "========================="
	@echo "install    Install package and development dependencies"
	@echo "test       Run project tests"
	@echo "lint       Run Ruff checks"
	@echo "audit      Run a sample audit against a public repository"
	@echo "help       Show this message"

install:
	python -m pip install -e '.[dev]'

test:
	python -m pytest tests ../../tests/test_integration.py

lint:
	python -m ruff check src tests examples ../../tests/test_integration.py

audit:
	python -m src.audit --repo https://github.com/pallets/flask --branch main --output-format json
