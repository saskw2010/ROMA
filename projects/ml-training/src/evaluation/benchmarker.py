from __future__ import annotations


class Benchmarker:
    """Compare models on the same dataset."""

    def run(self, models, X, y):
        results = {}
        for model in models:
            model.train(X, y)
            results[model.name] = model.evaluate(X, y)
        return results
