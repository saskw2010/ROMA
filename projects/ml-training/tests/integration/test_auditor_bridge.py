from __future__ import annotations

from src.integration.api_wrapper import SecurityAuditorAPIWrapper
from src.integration.security_auditor_bridge import SecurityAuditorBridge


def test_security_auditor_bridge_enhances_reports_and_tracks_deployment(tmp_path):
    bridge = SecurityAuditorBridge(audit_reports=[{"id": "audit-1"}])
    wrapper = SecurityAuditorAPIWrapper(bridge)
    assert wrapper.list_reports() == {"reports": [{"id": "audit-1"}]}

    enriched = wrapper.recommend({"id": "audit-1"}, [0.2, 0.8, 0.5])
    assert enriched["top_recommendation"] == 0.8

    model_path = tmp_path / "model.pkl"
    model_path.write_bytes(b"model")
    deployment = bridge.deploy_model(model_path)
    assert deployment == {"deployed": True, "path": str(model_path)}
