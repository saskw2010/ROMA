from __future__ import annotations

import json

import numpy as np


class SyntheticDataGenerator:
    """Generate synthetic audit data."""

    def __init__(self, random_state: int = 42):
        self.random = np.random.default_rng(random_state)

    def generate_user_audit_matrix(self, n_users=100, n_audits=50):
        """Generate a non-negative user-audit interaction matrix."""
        user_preferences = self.random.uniform(0.1, 1.0, size=(n_users, 3))
        audit_profiles = self.random.uniform(0.1, 1.0, size=(3, n_audits))
        noise = self.random.normal(0, 0.05, size=(n_users, n_audits))
        matrix = user_preferences @ audit_profiles + noise
        return np.clip(matrix, 0.0, None)

    def generate_item_features(self, n_audits=50, n_features=6):
        """Generate content features for audit items."""
        return self.random.uniform(0.0, 1.0, size=(n_audits, n_features))

    def generate_risk_scores(self, n_audits=50):
        """Generate bounded risk score data."""
        return self.random.uniform(0.0, 1.0, size=n_audits)

    def generate_risk_dataset(self, n_audits=50, n_features=4):
        """Generate features and synthetic risk targets."""
        features = self.random.uniform(0.0, 1.0, size=(n_audits, n_features))
        weights = np.linspace(0.2, 0.8, n_features)
        scores = np.clip(features @ weights / weights.sum(), 0.0, 1.0)
        return features, scores


def main() -> None:
    generator = SyntheticDataGenerator()
    matrix = generator.generate_user_audit_matrix(5, 4)
    print(json.dumps({"shape": list(matrix.shape), "mean": float(matrix.mean())}, indent=2))


if __name__ == "__main__":
    main()
