.PHONY: install test train evaluate clean

install:
	pip install -e .
	pip install -r requirements-dev.txt

train:
	python -m src.training.trainer

evaluate:
	python -m src.evaluation.validator

test:
	pytest tests -v

clean:
	rm -rf .pytest_cache models_saved/* results/*
