from __future__ import annotations

from pathlib import Path

import numpy as np


def load_dataset(path: str | Path) -> dict:
    dataset = np.load(Path(path), allow_pickle=False)
    return {key: dataset[key] for key in dataset.files}
