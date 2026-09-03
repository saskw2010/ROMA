from __future__ import annotations

import numpy as np


def mean_squared_error(y_true, y_pred) -> float:
    return float(np.mean((np.asarray(y_true) - np.asarray(y_pred)) ** 2))


def mean_absolute_error(y_true, y_pred) -> float:
    return float(np.mean(np.abs(np.asarray(y_true) - np.asarray(y_pred))))


def root_mean_squared_error(y_true, y_pred) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def precision_at_k(y_true, y_scores, k: int = 3) -> float:
    y_true = np.asarray(y_true)
    y_scores = np.asarray(y_scores)
    top_k = np.argsort(y_scores)[::-1][:k]
    positives = np.count_nonzero(y_true[top_k] > 0)
    return float(positives / max(1, k))


def recall_at_k(y_true, y_scores, k: int = 3) -> float:
    y_true = np.asarray(y_true)
    positive_total = np.count_nonzero(y_true > 0)
    if positive_total == 0:
        return 0.0
    y_scores = np.asarray(y_scores)
    top_k = np.argsort(y_scores)[::-1][:k]
    hits = np.count_nonzero(y_true[top_k] > 0)
    return float(hits / positive_total)


def regression_metrics(y_true, y_pred) -> dict:
    return {
        "mse": mean_squared_error(y_true, y_pred),
        "mae": mean_absolute_error(y_true, y_pred),
        "rmse": root_mean_squared_error(y_true, y_pred),
    }
