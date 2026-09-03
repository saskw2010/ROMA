from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class MLTrainingConfig:
    random_seed: int = 42
    results_dir: Path = Path("results")
    models_dir: Path = Path("models_saved")
    validation_fraction: float = 0.2
