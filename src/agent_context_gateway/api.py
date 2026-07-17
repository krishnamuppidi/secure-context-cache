from __future__ import annotations

from pathlib import Path

try:
    from fastapi import FastAPI, Header
    from pydantic import BaseModel
except Exception:  # pragma: no cover
    FastAPI = None
    BaseModel = object

from .gateway import AgentContextGateway
from .models import TaskRequest

if FastAPI is None:  # pragma: no cover
    raise RuntimeError("Install API dependencies with: pip install -e '.[api]'")

app = FastAPI(title="Agent Context Gateway", version="0.1.0")
gateway = AgentContextGateway()


class CapsuleRequest(BaseModel):
    repo: str = "examples/sample_repo"
    task_type: str
    path: str
    prompt: str
    agent_id: str = "secreviewagent"
    environment: str = "unknown"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/capsules")
def create_capsule(payload: CapsuleRequest, x_agent_api_key: str = Header()) -> dict:
    _graph, slices = gateway.load_context(Path(payload.repo))
    capsule, metrics = gateway.request_capsule(
        TaskRequest(
            task_type=payload.task_type,
            path=payload.path,
            prompt=payload.prompt,
            agent_id=payload.agent_id,
            environment=payload.environment,
        ),
        slices,
        api_key=x_agent_api_key,
    )
    return {"capsule": capsule.to_dict(), "metrics": metrics.to_dict()}


@app.post("/v1/insights")
def context_insights(payload: CapsuleRequest, x_agent_api_key: str = Header()) -> dict:
    _graph, slices = gateway.load_context(Path(payload.repo))
    capsule, metrics = gateway.request_capsule(
        TaskRequest(
            task_type=payload.task_type,
            path=payload.path,
            prompt=payload.prompt,
            agent_id=payload.agent_id,
            environment=payload.environment,
        ),
        slices,
        api_key=x_agent_api_key,
    )
    insights = gateway.generate_insights(capsule)
    return {
        "capsule": capsule.to_dict(),
        "insights": [item.to_dict() for item in insights],
        "metrics": metrics.to_dict(),
    }
