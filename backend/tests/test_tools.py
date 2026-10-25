"""Unit tests for the tool registry: permissions, risk, idempotency."""
from app.tools.registry import RiskLevel, ToolSpec, tool_registry


def test_registered_tools_have_required_fields():
    specs = {t.name: t for t in tool_registry.list()}
    assert "email_send" in specs
    assert "knowledge_answer" in specs
    for spec in specs.values():
        assert spec.name
        assert spec.description
        assert "type" in spec.input_schema
        assert isinstance(spec.required_permissions, list)
        assert isinstance(spec.risk, RiskLevel)
        assert spec.timeout_seconds > 0


def test_email_send_is_high_risk():
    spec = tool_registry.get("email_send")
    assert spec is not None
    assert spec.risk == RiskLevel.HIGH
    assert "email.send" in spec.required_permissions


def test_knowledge_answer_is_low_risk_no_perm():
    spec = tool_registry.get("knowledge_answer")
    assert spec is not None
    assert spec.risk == RiskLevel.LOW
    assert spec.required_permissions == []


def test_permission_check():
    assert tool_registry.has_permission("email_send", ["email.send"])
    assert not tool_registry.has_permission("email_send", ["email.read"])
    assert tool_registry.has_permission("knowledge_answer", [])
