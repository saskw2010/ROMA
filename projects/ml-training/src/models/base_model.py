from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import numpy as np


class BaseRecommendationModel(ABC):
    """Base class for recommendation models."""

    def __init__(self, name: str):
        self.name = name
        self.is_trained = False

    @abstractmethod
    def train(self, X: Any, y: Any):
        """Train the model."""

    @abstractmethod
    def predict(self, X: Any) -> np.ndarray:
        """Return predictions for the supplied input."""

    @abstractmethod
    def evaluate(self, X: Any, y: Any) -> dict:
        """Evaluate the model on supplied data."""

    def _ensure_trained(self) -> None:
        if not self.is_trained:
            raise RuntimeError(f"{self.name} must be trained before use")
