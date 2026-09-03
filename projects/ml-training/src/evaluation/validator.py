from __future__ import annotations

import json

import numpy as np

from ..datasets.synthetic_generator import SyntheticDataGenerator
from ..models.risk_predictor import RiskPredictorModel


class CrossValidator:
    """Run simple k-fold validation."""

    def __init__(self, model_factory, folds: int = 3):
        self.model_factory = model_factory
        self.folds = folds

    def validate(self, X, y):
        features = np.asarray(X, dtype=float)
        targets = np.asarray(y, dtype=float)
        fold_size = max(1, len(features) // self.folds)
        scores = []
        for fold in range(self.folds):
            start = fold * fold_size
            end = min(len(features), start + fold_size)
            X_val = features[start:end]
            y_val = targets[start:end]
            X_train = np.concatenate([features[:start], features[end:]], axis=0)
            y_train = np.concatenate([targets[:start], targets[end:]], axis=0)
            model = self.model_factory()
            model.train(X_train, y_train)
            scores.append(model.evaluate(X_val, y_val))
        return scores


def main() -> None:
    generator = SyntheticDataGenerator(random_state=9)
    features, scores = generator.generate_risk_dataset(18)
    validator = CrossValidator(RiskPredictorModel, folds=3)
    print(json.dumps(validator.validate(features, scores), indent=2))


if __name__ == "__main__":
    main()
