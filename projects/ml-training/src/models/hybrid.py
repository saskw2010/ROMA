from __future__ import annotations

import numpy as np

from .base_model import BaseRecommendationModel
from .collaborative_filtering import CollaborativeFilteringModel
from .content_based import ContentBasedModel


class HybridRecommendationModel(BaseRecommendationModel):
    """Combine collaborative and content-based scores."""

    def __init__(self, collaborative_weight: float = 0.5):
        super().__init__("Hybrid Recommendation")
        self.collaborative_weight = collaborative_weight
        self.collaborative_model = CollaborativeFilteringModel()
        self.content_model = ContentBasedModel()

    def train(self, X, y):
        collaborative_X = np.asarray(X["collaborative"], dtype=float)
        content_X = np.asarray(X["content"], dtype=float)
        collaborative_y = y.get("collaborative", collaborative_X)
        content_y = y["content"]
        self.collaborative_model.train(collaborative_X, collaborative_y)
        self.content_model.train(content_X, content_y)
        self.is_trained = True
        return self

    def predict(self, X):
        self._ensure_trained()
        collaborative_scores = self.collaborative_model.predict(X["collaborative"]).mean(axis=0)
        content_scores = self.content_model.predict(X["content"])
        weight = self.collaborative_weight
        return (weight * collaborative_scores) + ((1 - weight) * content_scores)

    def evaluate(self, X, y) -> dict:
        predictions = self.predict(X)
        truth = np.asarray(y["content"], dtype=float)
        errors = np.abs(truth - predictions)
        return {
            "mae": float(np.mean(errors)),
            "max_error": float(np.max(errors)),
        }
