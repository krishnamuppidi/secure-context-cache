from __future__ import annotations

from agent_context_gateway.identity import AgentRegistry


def test_local_registry_can_be_configured_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("ACG_LOCAL_AGENT_ID", "architecture-agent")
    monkeypatch.setenv("ACG_LOCAL_API_KEY", "test-key")
    monkeypatch.setenv("ACG_LOCAL_ALLOWED_TASK_TYPES", "architecture_qa,onboarding")
    monkeypatch.setenv("ACG_LOCAL_MAX_SENSITIVITY", "medium")

    identity = AgentRegistry.from_env_or_demo().authenticate("architecture-agent", "test-key")

    assert identity.allowed_task_types == ["architecture_qa", "onboarding"]
    assert identity.max_sensitivity == "medium"
    assert identity.owner == "local-runtime"
