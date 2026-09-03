from __future__ import annotations


class HyperparameterTuner:
    """Simple grid-search tuner."""

    def __init__(self, model_factory, scorer):
        self.model_factory = model_factory
        self.scorer = scorer

    def search(self, parameter_grid, X_train, y_train, X_val, y_val):
        best_result = None
        for params in parameter_grid:
            model = self.model_factory(**params)
            model.train(X_train, y_train)
            score = self.scorer(y_val, model.predict(X_val))
            candidate = {"params": params, "score": score}
            if best_result is None or score < best_result["score"]:
                best_result = candidate
        return best_result
