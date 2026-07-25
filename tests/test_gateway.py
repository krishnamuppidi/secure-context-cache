from pathlib import Path

import pytest

from agent_context_gateway.gateway import AgentContextGateway
from agent_context_gateway.models import ContextSlice, TaskRequest
from agent_context_gateway.policy import load_policy

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_REPO = ROOT / "examples" / "sample_repo"


def test_demo_releases_context_and_writes_audit(tmp_path: Path) -> None:
    result = AgentContextGateway().run_demo(SAMPLE_REPO, tmp_path)
    assert result.capsule.facts
    assert result.capsule.denied
    assert result.capsule.source_manifest
    assert result.capsule.redaction_notes
    assert result.audit_record["policy_version"] == result.capsule.policy_version
    assert result.audit_record["source_manifest"]
    assert result.metrics.token_reduction_percent >= 0
    assert (tmp_path / "audit-record.json").exists()
    assert (tmp_path / "context-insights.json").exists()


def test_bad_credentials_are_rejected() -> None:
    gateway = AgentContextGateway()
    _graph, slices = gateway.load_context(SAMPLE_REPO)
    with pytest.raises(PermissionError):
        gateway.request_capsule(
            TaskRequest(
                task_type="iac_security",
                path="terraform/prod/payments/lambda.tf",
                prompt="review prod change",
                agent_id="secreviewagent",
                environment="prod",
            ),
            slices,
            api_key="wrong",
        )


def test_onboarding_agent_cannot_request_iac_security() -> None:
    gateway = AgentContextGateway()
    _graph, slices = gateway.load_context(SAMPLE_REPO)
    capsule, _metrics = gateway.request_capsule(
        TaskRequest(
            task_type="iac_security",
            path="terraform/prod/payments/lambda.tf",
            prompt="review prod change",
            agent_id="onboarding",
            environment="prod",
        ),
        slices,
        api_key="demo-onboarding-key",
    )
    assert not capsule.facts
    assert capsule.denied


def test_repeated_task_uses_cache() -> None:
    gateway = AgentContextGateway()
    _graph, slices = gateway.load_context(SAMPLE_REPO)
    task = TaskRequest(
        task_type="iac_security",
        path="terraform/prod/payments/lambda.tf",
        prompt="review prod change",
        agent_id="secreviewagent",
        environment="prod",
    )
    first, _ = gateway.request_capsule(task, slices, api_key="demo-secreviewagent-key")
    second, _ = gateway.request_capsule(task, slices, api_key="demo-secreviewagent-key")
    assert first.cache_hit is False
    assert second.cache_hit is True
    assert first.audit_id != second.audit_id
    changed_prompt = TaskRequest(
        task_type="iac_security",
        path="terraform/prod/payments/lambda.tf",
        prompt="review a different change",
        agent_id="secreviewagent",
        environment="prod",
    )
    third, _ = gateway.request_capsule(
        changed_prompt,
        slices,
        api_key="demo-secreviewagent-key",
    )
    # Equivalent wording reuses the same policy-scoped selection plan. Request IDs
    # are audit correlation values, not cache-busting inputs.
    assert third.cache_hit is True


def test_cache_is_invalidated_when_source_manifest_changes() -> None:
    gateway = AgentContextGateway()
    _graph, slices = gateway.load_context(SAMPLE_REPO)
    task = TaskRequest(
        task_type="iac_security",
        path="terraform/prod/payments/lambda.tf",
        prompt="review prod change",
        agent_id="secreviewagent",
        environment="prod",
        context_id="payments",
    )
    first, _ = gateway.request_capsule(task, slices, api_key="demo-secreviewagent-key")
    slices[0].source_hash = "changed-source"
    second, _ = gateway.request_capsule(task, slices, api_key="demo-secreviewagent-key")
    assert first.cache_hit is False
    assert second.cache_hit is False


def test_cache_is_invalidated_when_policy_changes_without_version_bump() -> None:
    gateway = AgentContextGateway()
    _graph, slices = gateway.load_context(SAMPLE_REPO)
    task = TaskRequest(
        task_type="iac_security",
        path="terraform/prod/payments/lambda.tf",
        prompt="review prod change",
        agent_id="secreviewagent",
        environment="prod",
    )
    first, _ = gateway.request_capsule(task, slices, api_key="demo-secreviewagent-key")
    gateway.policy["max_slice_age_days"] = 7
    second, _ = gateway.request_capsule(task, slices, api_key="demo-secreviewagent-key")
    assert first.cache_hit is False
    assert second.cache_hit is False


def test_restricted_context_requires_explicit_approval() -> None:
    gateway = AgentContextGateway()
    _graph, slices = gateway.load_context(SAMPLE_REPO)
    slices.append(
        ContextSlice(
            id="restricted-prod-identity-path",
            scope="terraform/prod/payments/restricted-identity.tf",
            slice_type="iam",
            facts=["restricted production identity path exists"],
            sensitivity="restricted",
            refs=["terraform/prod/payments/restricted-identity.tf"],
            version="test",
            token_estimate=5,
            environment="prod",
            source_hash="testhash",
            freshness_timestamp="2026-07-06T00:00:00+00:00",
        )
    )
    capsule, _metrics = gateway.request_capsule(
        TaskRequest(
            task_type="iac_security",
            path="terraform/prod/payments/restricted-identity.tf",
            prompt="review prod change",
            agent_id="secreviewagent",
            environment="prod",
        ),
        slices,
        api_key="demo-secreviewagent-key",
    )
    assert "restricted-prod-identity-path" in capsule.approval_required_slice_ids
    assert any("approval required" in item.reason for item in capsule.denied)


def test_policy_file_overrides_defaults(tmp_path: Path) -> None:
    policy_path = tmp_path / "policy.json"
    policy_path.write_text('{"version": "test", "ttl_minutes": 5}')
    policy = load_policy(policy_path)
    assert policy["version"] == "test"
    assert policy["ttl_minutes"] == 5
    assert policy["max_sensitivity_by_task"]
