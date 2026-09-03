# ML Training Getting Started

## Installation

```bash
cd projects/ml-training
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

```bash
python -m src.datasets.synthetic_generator
python -m src.training.trainer
python -m src.evaluation.validator
```
