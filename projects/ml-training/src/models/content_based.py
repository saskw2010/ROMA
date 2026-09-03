from __future__ import annotations

import numpy as np

from .base_model import BaseRecommendationModel
from ..training.metrics import regression_metrics


class ContentBasedModel(BaseRecommendationModel):
    """Content-based recommender using a learned preference profile."""

    def __init__(self):
        super().__init__("Content Based")
        self._profile: np.ndarray | None = None

    def train(self, X, y):
        features = np.asarray(X, dtype=float)
        targets = np.asarray(y, dtype=float).reshape(-1)
        if features.shape[0] != targets.shape[0]:
            raise ValueError("Feature and target lengths must match")
        total_weight = float(np.sum(np.abs(targets))) or 1.0
        self._profile = (features * targets[:, None]).sum(axis=0) / total_weight
        self.is_trained = True
        return self

    def predict(self, X):
        self._ensure_trained()
        features = np.asarray(X, dtype=float)
        profile_norm = np.linalg.norm(self._profile) or 1.0
        feature_norms = np.linalg.norm(features, axis=1)
        feature_norms[feature_norms == 0] = 1.0
        scores = (features @ self._profile) / (feature_norms * profile_norm)
        return np.clip(scores, 0.0, 1.0)

    def evaluate(self, X, y) -> dict:
        predictions = self.predict(X)
        return regression_metrics(y, predictions)
