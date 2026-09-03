# ML Training & Recommendation Engine

ML utilities for training recommendation and risk models that integrate with ROMA's Security Auditor workflows.

## Layout

- `src/models/` recommendation and prediction models
- `src/training/` training, metrics, and tuning helpers
- `src/datasets/` synthetic data generation and preprocessing
- `src/evaluation/` validation, benchmarking, and analysis helpers
- `src/integration/` bridge utilities for Security Auditor integration
- `tests/` focused unit and integration tests

## Quick start

```bash
cd projects/ml-training
pip install -r requirements-dev.txt
pytest tests -q
```

See [GETTING_STARTED.md](./GETTING_STARTED.md) and [ROADMAP.md](./ROADMAP.md) for more details.
