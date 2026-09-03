from __future__ import annotations

from pathlib import Path


class ModelDeploymentManager:
    """Simple deployment state helper."""

    def deploy(self, model_path: str | Path) -> dict:
        path = Path(model_path)
        return {"path": str(path), "exists": path.exists()}
