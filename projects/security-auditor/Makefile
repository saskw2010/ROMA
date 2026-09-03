PYTHON ?= python

.PHONY: install test lint audit clean docs

install:
	$(PYTHON) -m pip install -e .
	$(PYTHON) -m pip install -r requirements-dev.txt

test:
	pytest -q

lint:
	ruff check src tests security_auditor --select E,F,I
	black --check src tests security_auditor examples
	mypy src security_auditor

audit:
	$(PYTHON) -m security_auditor --repo https://github.com/example/repo.git --format json

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache build dist *.egg-info reports tmp

docs:
	@echo "See GETTING_STARTED.md and ARCHITECTURE.md"
