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
