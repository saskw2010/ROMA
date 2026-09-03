from __future__ import annotations

import numpy as np

from src.datasets.synthetic_generator import SyntheticDataGenerator
from src.models.collaborative_filtering import CollaborativeFilteringModel
from src.models.content_based import ContentBasedModel
from src.models.hybrid import HybridRecommendationModel
from src.models.risk_predictor import RiskPredictorModel


def test_collaborative_filtering_reconstructs_matrix_shape():
    matrix = SyntheticDataGenerator(random_state=1).generate_user_audit_matrix(8, 5)
    model = CollaborativeFilteringModel(n_components=2)
    model.train(matrix, matrix)
    predictions = model.predict(matrix)
    assert predictions.shape == matrix.shape
    assert model.evaluate(matrix, matrix)["rmse"] >= 0


def test_content_based_returns_bounded_scores():
    features = np.array([[1.0, 0.0], [0.5, 0.5], [0.0, 1.0]])
    targets = np.array([1.0, 0.5, 0.0])
    model = ContentBasedModel().train(features, targets)
    scores = model.predict(features)
    assert scores.shape == (3,)
    assert np.all(scores >= 0)
    assert np.all(scores <= 1)


def test_hybrid_combines_collaborative_and_content_scores():
    generator = SyntheticDataGenerator(random_state=2)
    matrix = generator.generate_user_audit_matrix(6, 4)
    features = generator.generate_item_features(4, 3)
    targets = matrix.mean(axis=0)
    model = HybridRecommendationModel(collaborative_weight=0.6)
    model.train({"collaborative": matrix, "content": features}, {"collaborative": matrix, "content": targets})
    predictions = model.predict({"collaborative": matrix, "content": features})
    assert predictions.shape == (4,)
    assert model.evaluate(
        {"collaborative": matrix, "content": features},
        {"content": targets},
    )["mae"] >= 0


def test_risk_predictor_fits_simple_linear_relationship():
    X = np.array([[0.0], [1.0], [2.0], [3.0]])
    y = np.array([0.0, 1.0, 2.0, 3.0])
    model = RiskPredictorModel().train(X, y)
    predictions = model.predict(X)
    assert np.allclose(predictions, y)
