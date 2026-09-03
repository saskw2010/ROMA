from __future__ import annotations

import numpy as np


def normalize_rows(matrix):
    values = np.asarray(matrix, dtype=float)
    row_sums = values.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1.0
    return values / row_sums


def train_validation_split(values, validation_fraction: float = 0.2):
    array = np.asarray(values, dtype=float)
    split_index = max(1, int(len(array) * (1 - validation_fraction)))
    return array[:split_index], array[split_index:]
