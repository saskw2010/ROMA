from __future__ import annotations


class ResultAnalyzer:
    """Summarize benchmark output."""

    def summarize(self, benchmark_results: dict) -> dict:
        best_model = min(
            benchmark_results.items(),
            key=lambda item: item[1].get("rmse", item[1].get("mae", 0.0)),
        )[0]
        return {"best_model": best_model, "model_count": len(benchmark_results)}
