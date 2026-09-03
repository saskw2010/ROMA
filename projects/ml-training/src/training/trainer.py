from __future__ import annotations

import asyncio
import json
import pickle
from pathlib import Path

from .metrics import regression_metrics
from ..datasets.synthetic_generator import SyntheticDataGenerator
from ..models.risk_predictor import RiskPredictorModel


class ModelTrainer:
    """Training pipeline for models."""

    def __init__(self, model, config):
        self.model = model
        self.config = config
        self.last_metrics: dict | None = None

    async def train(self, X_train, y_train, X_val, y_val):
        """Train the model and evaluate validation data."""
        await asyncio.sleep(0)
        self.model.train(X_train, y_train)
        predictions = self.model.predict(X_val)
        self.last_metrics = regression_metrics(y_val, predictions)
        return self.last_metrics

    def evaluate(self, X_test, y_test):
        """Evaluate the trained model."""
        self.last_metrics = self.model.evaluate(X_test, y_test)
        return self.last_metrics

    def save_model(self, path):
        """Save trained model."""
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("wb") as handle:
            pickle.dump(self.model, handle)
        return destination


def main() -> None:
    generator = SyntheticDataGenerator(random_state=21)
    features, scores = generator.generate_risk_dataset(30)
    split = 20
    trainer = ModelTrainer(RiskPredictorModel(), {"name": "default"})
    metrics = asyncio.run(trainer.train(features[:split], scores[:split], features[split:], scores[split:]))
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
