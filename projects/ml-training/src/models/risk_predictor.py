from __future__ import annotations

import numpy as np

from .base_model import BaseRecommendationModel
from ..training.metrics import regression_metrics


class RiskPredictorModel(BaseRecommendationModel):
    """Linear risk score predictor."""

    def __init__(self):
        super().__init__("Risk Predictor")
        self._weights: np.ndarray | None = None

    def train(self, X, y):
        features = np.asarray(X, dtype=float)
        targets = np.asarray(y, dtype=float).reshape(-1, 1)
        bias = np.ones((features.shape[0], 1))
        design = np.hstack([bias, features])
        self._weights = np.linalg.pinv(design) @ targets
        self.is_trained = True
        return self

    def predict(self, X):
        self._ensure_trained()
        features = np.asarray(X, dtype=float)
        bias = np.ones((features.shape[0], 1))
        design = np.hstack([bias, features])
        return (design @ self._weights).reshape(-1)

    def evaluate(self, X, y) -> dict:
        predictions = self.predict(X)
        return regression_metrics(y, predictions)
