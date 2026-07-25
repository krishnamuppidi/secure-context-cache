from __future__ import annotations

import os
from pathlib import Path

try:
    from fastapi import FastAPI, Header, HTTPException, Request
    from pydantic import BaseModel, Field
except ImportError:  # pragma: no cover
    FastAPI = None
    BaseModel = object

from .aws_runtime import (
    DynamoAuditStore,
    DynamoContextSliceCache,
    DynamoSliceStore,
    S3ContextStore,
)
from .gateway import AgentContextGateway
from .identity import AgentRegistry
from .models import AgentIdentity, TaskRequest
from .optimization import build_optimization_plan
from .policy import DEFAULT_POLICY

if FastAPI is None:  # pragma: no cover
    raise RuntimeError("Install API dependencies with: pip install -e '.[api]'")


def _runtime_mode() -> str:
    return os.getenv("ACG_RUNTIME_MODE", "local").lower()


def _build_gateway() -> AgentContextGateway:
    if _runtime_mode() != "aws":
        return AgentContextGateway(registry=AgentRegistry.from_env_or_demo())
    return AgentContextGateway(
        cache=DynamoContextSliceCache.from_env(),
        audit_store=DynamoAuditStore.from_env(),
        slice_store=DynamoSliceStore.from_env(),
    )


app = FastAPI(title="Secure Context Cache - Token Optimization API", version="0.7.0")
gateway = _build_gateway()
context_store = S3ContextStore.from_env() if _runtime_mode() == "aws" else None


class CapsuleRequest(BaseModel):
    context_id: str = "default"
    repo: str | None = None
    task_type: str
    path: str
    prompt: str
    agent_id: str = "secreviewagent"
    user: str = "developer"
    environment: str = "unknown"
    request_id: str = ""
    provider: str = "generic"
    model: str = ""
    tokenizer: str = "word"
    token_budget: int | None = Field(default=None, gt=0, le=10_000_000)


def _claims_from_request(request: Request) -> dict[str, str]:
    event = request.scope.get("aws.event", {})
    return (
        event.get("requestContext", {})
        .get("authorizer", {})
        .get("jwt", {})
        .get("claims", {})
    )


def _aws_identity(request: Request) -> AgentIdentity:
    claims = _claims_from_request(request)
    client_id = claims.get("client_id") or claims.get("sub")
    if not client_id:
        raise HTTPException(status_code=401, detail="verified Cognito identity is missing")
    allowed = os.getenv(
        "ACG_ALLOWED_TASK_TYPES", ",".join(DEFAULT_POLICY["max_sensitivity_by_task"].keys())
    )
    return AgentIdentity(
        agent_id=client_id,
        allowed_task_types=[item.strip() for item in allowed.split(",") if item.strip()],
        max_sensitivity=os.getenv("ACG_MAX_SENSITIVITY", "high"),
        owner="cognito",
    )


def _local_repo(payload: CapsuleRequest) -> Path:
    requested = Path(payload.repo or "examples/sample_repo").resolve()
    allowed_root = Path(os.getenv("ACG_ALLOWED_REPO_ROOT", Path.cwd())).resolve()
    if requested != allowed_root and allowed_root not in requested.parents:
        raise HTTPException(status_code=400, detail="repo must be inside ACG_ALLOWED_REPO_ROOT")
    if not requested.is_dir():
        raise HTTPException(status_code=404, detail=f"repo not found: {requested}")
    return requested


def _task(payload: CapsuleRequest, identity: AgentIdentity, user: str) -> TaskRequest:
    return TaskRequest(
        task_type=payload.task_type,
        path=payload.path,
        prompt=payload.prompt,
        agent_id=identity.agent_id,
        user=user,
        environment=payload.environment,
        request_id=payload.request_id,
        context_id=payload.context_id,
        provider=payload.provider,
        model=payload.model,
        tokenizer=payload.tokenizer,
        token_budget=payload.token_budget,
    )


def _response(payload: CapsuleRequest, request: Request, api_key: str | None) -> dict:
    try:
        if _runtime_mode() == "aws":
            identity = _aws_identity(request)
            assert context_store is not None
            manifest_hash = context_store.manifest_hash(payload.context_id)
            slices = None
            if gateway.slice_store is not None:
                slices = gateway.slice_store.get_many(payload.context_id, manifest_hash)
            if slices is None:
                with context_store.materialize(payload.context_id) as repo:
                    _graph, slices = gateway.load_context(
                        repo,
                        context_id=payload.context_id,
                        manifest_hash=manifest_hash,
                    )
            claims = _claims_from_request(request)
            task = _task(payload, identity, claims.get("sub", identity.agent_id))
            capsule, metrics = gateway.request_capsule_for_identity(task, slices, identity)
        else:
            if not api_key:
                raise HTTPException(status_code=401, detail="x-agent-api-key is required")
            _graph, slices = gateway.load_context(_local_repo(payload))
            task = TaskRequest(
                task_type=payload.task_type,
                path=payload.path,
                prompt=payload.prompt,
                agent_id=payload.agent_id,
                user=payload.user,
                environment=payload.environment,
                request_id=payload.request_id,
                context_id=payload.context_id,
                provider=payload.provider,
                model=payload.model,
                tokenizer=payload.tokenizer,
                token_budget=payload.token_budget,
            )
            capsule, metrics = gateway.request_capsule(task, slices, api_key=api_key)
    except HTTPException:
        raise
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    optimization = build_optimization_plan(capsule, metrics, task)
    return {
        "capsule": capsule.to_dict(),
        "metrics": metrics.to_dict(),
        "optimization": optimization.to_dict(),
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "runtime": _runtime_mode()}


@app.post("/v1/capsules")
def create_capsule(
    payload: CapsuleRequest,
    request: Request,
    x_agent_api_key: str | None = Header(default=None),
) -> dict:
    return _response(payload, request, x_agent_api_key)


@app.post("/v1/optimize")
def optimize_context(
    payload: CapsuleRequest,
    request: Request,
    x_agent_api_key: str | None = Header(default=None),
) -> dict:
    """Primary token-optimization endpoint; capsules remains backward compatible."""
    return _response(payload, request, x_agent_api_key)


@app.post("/v1/insights")
def context_insights(
    payload: CapsuleRequest,
    request: Request,
    x_agent_api_key: str | None = Header(default=None),
) -> dict:
    response = _response(payload, request, x_agent_api_key)
    raw_capsule = response["capsule"]
    from .models import ContextCapsule, DeniedSlice, ReleasedFact

    capsule = ContextCapsule(
        **{
            **raw_capsule,
            "facts": [ReleasedFact(**item) for item in raw_capsule["facts"]],
            "denied": [DeniedSlice(**item) for item in raw_capsule["denied"]],
        }
    )
    response["insights"] = [item.to_dict() for item in gateway.generate_insights(capsule)]
    return response
