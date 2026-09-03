from __future__ import annotations

import numpy as np

from .base_model import BaseRecommendationModel
from ..training.metrics import regression_metrics


class CollaborativeFilteringModel(BaseRecommendationModel):
    """Collaborative filtering via truncated SVD reconstruction."""

    def __init__(self, n_components: int = 20):
        super().__init__("Collaborative Filtering")
        self.n_components = n_components
        self._item_factors: np.ndarray | None = None

    def train(self, X, y=None):
        matrix = np.asarray(X, dtype=float)
        _, _, vt = np.linalg.svd(matrix, full_matrices=False)
        n_components = max(1, min(self.n_components, vt.shape[0]))
        self._item_factors = vt[:n_components]
        self.is_trained = True
        return self

    def predict(self, X):
        self._ensure_trained()
        matrix = np.asarray(X, dtype=float)
        latent = matrix @ self._item_factors.T
        reconstructed = latent @ self._item_factors
        return np.clip(reconstructed, 0.0, None)

    def evaluate(self, X, y) -> dict:
        predictions = self.predict(X)
        return regression_metrics(y, predictions)
