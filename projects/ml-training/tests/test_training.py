from __future__ import annotations

import asyncio

import numpy as np
import pytest

from src.models.risk_predictor import RiskPredictorModel
from src.training.hyperparameter_tuning import HyperparameterTuner
from src.training.metrics import mean_squared_error
from src.training.trainer import ModelTrainer


def test_model_trainer_trains_evaluates_and_saves(tmp_path):
    X = np.array([[0.0], [1.0], [2.0], [3.0]])
    y = np.array([0.0, 1.0, 2.0, 3.0])
    trainer = ModelTrainer(RiskPredictorModel(), {"name": "unit"})
    metrics = asyncio.run(trainer.train(X[:2], y[:2], X[2:], y[2:]))
    assert metrics["rmse"] >= 0
    saved_path = trainer.save_model(tmp_path / "model.pkl")
    assert saved_path.exists()
    evaluation = trainer.evaluate(X, y)
    assert evaluation["mae"] >= 0


def test_hyperparameter_tuner_returns_best_candidate():
    X = np.array([[0.0], [1.0], [2.0], [3.0]])
    y = np.array([0.0, 1.0, 2.0, 3.0])
    tuner = HyperparameterTuner(lambda: RiskPredictorModel(), mean_squared_error)
    result = tuner.search([{}], X[:2], y[:2], X[2:], y[2:])
    assert result["params"] == {}
    assert result["score"] == pytest.approx(0.0)
