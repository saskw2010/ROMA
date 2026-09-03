from __future__ import annotations

import numpy as np

from src.evaluation.analyzer import ResultAnalyzer
from src.evaluation.benchmarker import Benchmarker
from src.evaluation.validator import CrossValidator
from src.models.risk_predictor import RiskPredictorModel


def test_cross_validator_returns_one_result_per_fold():
    X = np.array([[0.0], [1.0], [2.0], [3.0], [4.0], [5.0]])
    y = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
    validator = CrossValidator(RiskPredictorModel, folds=3)
    results = validator.validate(X, y)
    assert len(results) == 3
    assert all("rmse" in result for result in results)


def test_benchmarker_and_analyzer_summarize_results():
    X = np.array([[0.0], [1.0], [2.0], [3.0]])
    y = np.array([0.0, 1.0, 2.0, 3.0])
    results = Benchmarker().run([RiskPredictorModel()], X, y)
    summary = ResultAnalyzer().summarize(results)
    assert summary == {"best_model": "Risk Predictor", "model_count": 1}
