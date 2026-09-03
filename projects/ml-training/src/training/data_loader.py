from __future__ import annotations

from pathlib import Path

import numpy as np


class DataLoader:
    """Load saved numpy datasets for the training pipeline."""

    def load_npz(self, path: str | Path) -> dict:
        dataset = np.load(Path(path), allow_pickle=False)
        return {key: dataset[key] for key in dataset.files}

    def split_matrix(self, matrix, validation_fraction: float = 0.2) -> tuple[np.ndarray, np.ndarray]:
        values = np.asarray(matrix, dtype=float)
        split_index = max(1, int(values.shape[0] * (1 - validation_fraction)))
        return values[:split_index], values[split_index:]
