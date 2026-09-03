from __future__ import annotations

from .security_auditor_bridge import SecurityAuditorBridge


class SecurityAuditorAPIWrapper:
    """Tiny wrapper that exposes bridge operations as API-friendly methods."""

    def __init__(self, bridge: SecurityAuditorBridge):
        self.bridge = bridge

    def list_reports(self) -> dict:
        return {"reports": self.bridge.get_audit_reports()}

    def recommend(self, audit_report, predictions) -> dict:
        return self.bridge.enhance_recommendations(audit_report, predictions)
