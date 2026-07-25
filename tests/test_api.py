from __future__ import annotations

from fastapi.testclient import TestClient
from starlette.requests import Request

from agent_context_gateway.api import _aws_identity, app


def test_local_api_requires_key_and_returns_capsule() -> None:
    client = TestClient(app)
    payload = {
        "task_type": "iac_security",
        "path": "terraform/prod/payments/lambda.tf",
        "prompt": "review this change",
        "agent_id": "secreviewagent",
        "user": "api-test-user",
        "environment": "prod",
        "request_id": "api-test-request",
    }
    assert client.post("/v1/capsules", json=payload).status_code == 401
    response = client.post(
        "/v1/capsules",
        json=payload,
        headers={"x-agent-api-key": "demo-secreviewagent-key"},
    )
    assert response.status_code == 200
    assert response.json()["capsule"]["facts"]
    assert response.json()["capsule"]["request_id"] == "api-test-request"
    assert response.json()["capsule"]["task"]["user"] == "api-test-user"
    assert response.json()["optimization"]["framework"] == "Secure Context Cache"
    assert response.json()["optimization"]["stable_context"]


def test_optimize_endpoint_returns_budget_and_cache_plan() -> None:
    client = TestClient(app)
    response = client.post(
        "/v1/optimize",
        json={
            "task_type": "iac_security",
            "path": "terraform/prod/payments/lambda.tf",
            "prompt": "review this change",
            "agent_id": "secreviewagent",
            "environment": "prod",
            "provider": "openai",
            "token_budget": 100,
        },
        headers={"x-agent-api-key": "demo-secreviewagent-key"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["metrics"]["token_budget_status"] == "within_budget"
    assert body["optimization"]["provider"] == "openai"
    assert body["optimization"]["cache_namespace"]


def test_secure_rag_authorizes_candidates_and_never_echoes_denied_content() -> None:
    client = TestClient(app)
    payload = {
        "task_type": "iac_security",
        "path": "terraform/prod/payments/lambda.tf",
        "prompt": "review this infrastructure change",
        "agent_id": "secreviewagent",
        "environment": "prod",
        "candidates": [
            {
                "candidate_id": "approved-policy",
                "content": "The production role must not use wildcard permissions.",
                "refs": ["terraform/prod/payments/lambda.tf"],
                "sensitivity": "high",
                "environment": "prod",
            },
            {
                "candidate_id": "restricted-runbook",
                "content": "DENIED-SECRET-CONTENT-MUST-NOT-LEAK",
                "refs": ["terraform/prod/payments/lambda.tf"],
                "sensitivity": "restricted",
                "environment": "prod",
            },
        ],
    }
    assert client.post("/v1/authorize-retrieval", json=payload).status_code == 401
    response = client.post(
        "/v1/authorize-retrieval",
        json=payload,
        headers={"x-agent-api-key": "demo-secreviewagent-key"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["retrieval"]["authorized_candidate_ids"] == ["approved-policy"]
    assert body["retrieval"]["denied_candidates"][0]["candidate_id"] == "restricted-runbook"
    assert body["retrieval"]["empty_authorized_result"] is False
    assert "production role" in body["optimization"]["stable_context"]
    assert "DENIED-SECRET-CONTENT-MUST-NOT-LEAK" not in response.text


def test_secure_rag_empty_authorized_result_fails_closed() -> None:
    client = TestClient(app)
    response = client.post(
        "/v1/authorize-retrieval",
        json={
            "task_type": "iac_security",
            "path": "terraform/prod/payments/lambda.tf",
            "prompt": "review this infrastructure change",
            "agent_id": "secreviewagent",
            "environment": "prod",
            "candidates": [
                {
                    "candidate_id": "unrelated",
                    "content": "Unrelated development documentation.",
                    "refs": ["docs/dev/onboarding.md"],
                    "sensitivity": "low",
                    "environment": "dev",
                }
            ],
        },
        headers={"x-agent-api-key": "demo-secreviewagent-key"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["retrieval"]["empty_authorized_result"] is True
    assert body["retrieval"]["fail_closed"] is True
    assert body["retrieval"]["unrestricted_fallback_allowed"] is False
    assert body["optimization"]["stable_context"] == ""
    selection = next(
        item
        for item in body["optimization"]["levers"]
        if item["name"] == "policy_selection"
    )
    assert selection["status"] == "blocked"


def test_secure_rag_rejects_duplicate_candidate_ids() -> None:
    client = TestClient(app)
    candidate = {
        "candidate_id": "duplicate",
        "content": "candidate content",
        "refs": ["terraform/prod/payments/lambda.tf"],
    }
    response = client.post(
        "/v1/authorize-retrieval",
        json={
            "task_type": "iac_security",
            "path": "terraform/prod/payments/lambda.tf",
            "prompt": "review",
            "agent_id": "secreviewagent",
            "candidates": [candidate, candidate],
        },
        headers={"x-agent-api-key": "demo-secreviewagent-key"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "duplicate retrieval candidate_id: duplicate"


def test_secure_rag_rejects_false_source_hash() -> None:
    client = TestClient(app)
    response = client.post(
        "/v1/authorize-retrieval",
        json={
            "task_type": "iac_security",
            "path": "terraform/prod/payments/lambda.tf",
            "prompt": "review",
            "agent_id": "secreviewagent",
            "candidates": [
                {
                    "candidate_id": "tampered",
                    "content": "candidate content",
                    "refs": ["terraform/prod/payments/lambda.tf"],
                    "source_hash": "0" * 64,
                }
            ],
        },
        headers={"x-agent-api-key": "demo-secreviewagent-key"},
    )
    assert response.status_code == 400
    assert "source_hash does not match content" in response.json()["detail"]


def test_secure_rag_denies_stale_candidates_without_echoing_content() -> None:
    client = TestClient(app)
    response = client.post(
        "/v1/authorize-retrieval",
        json={
            "task_type": "iac_security",
            "path": "terraform/prod/payments/lambda.tf",
            "prompt": "review",
            "agent_id": "secreviewagent",
            "candidates": [
                {
                    "candidate_id": "stale",
                    "content": "STALE-CONTENT-MUST-NOT-BE-RELEASED",
                    "refs": ["terraform/prod/payments/lambda.tf"],
                    "freshness_timestamp": "2020-01-01T00:00:00+00:00",
                }
            ],
        },
        headers={"x-agent-api-key": "demo-secreviewagent-key"},
    )
    assert response.status_code == 200
    assert response.json()["retrieval"]["fail_closed"] is True
    assert "days old" in response.json()["retrieval"]["denied_candidates"][0]["reason"]
    assert "STALE-CONTENT-MUST-NOT-BE-RELEASED" not in response.text


def test_cognito_claims_map_to_agent_identity(monkeypatch) -> None:
    monkeypatch.setenv("ACG_ALLOWED_TASK_TYPES", "iac_security,architecture_qa")
    request = Request(
        {
            "type": "http",
            "aws.event": {
                "requestContext": {
                    "authorizer": {
                        "jwt": {"claims": {"client_id": "machine-client", "sub": "subject"}}
                    }
                }
            },
        }
    )
    identity = _aws_identity(request)
    assert identity.agent_id == "machine-client"
    assert identity.allowed_task_types == ["iac_security", "architecture_qa"]
