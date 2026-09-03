from __future__ import annotations

from pathlib import Path


class SecurityAuditorBridge:
    """Bridge between ML training and Security Auditor."""

    def __init__(self, audit_reports=None):
        self.audit_reports = list(audit_reports or [])
        self.deployed_model_path: str | None = None

    def get_audit_reports(self):
        """Fetch audit reports."""
        return list(self.audit_reports)

    def enhance_recommendations(self, audit_report, predictions):
        """Enhance audit with ML predictions."""
        return {
            **audit_report,
            "recommendations": list(predictions),
            "top_recommendation": max(predictions) if predictions else None,
        }

    def deploy_model(self, model_path):
        """Deploy trained model."""
        path = Path(model_path)
        self.deployed_model_path = str(path)
        return {"deployed": path.exists(), "path": self.deployed_model_path}
