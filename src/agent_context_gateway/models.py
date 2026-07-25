from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def utc_in(minutes: int) -> str:
    return (datetime.now(UTC) + timedelta(minutes=minutes)).replace(microsecond=0).isoformat()


def stable_id(*parts: str) -> str:
    return sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]


def stable_hash(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


@dataclass
class ContextNode:
    id: str
    kind: str
    name: str
    path: str
    environment: str = "unknown"
    sensitivity: str = "low"
    owner: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ContextEdge:
    source: str
    target: str
    relation: str
    sensitivity: str = "low"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ContextGraph:
    root: str
    generated_at: str
    nodes: list[ContextNode]
    edges: list[ContextEdge]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ContextSlice:
    id: str
    scope: str
    slice_type: str
    facts: list[str]
    sensitivity: str
    refs: list[str]
    version: str
    token_estimate: int
    owner: str = "unknown"
    environment: str = "unknown"
    allowed_task_profiles: list[str] = field(default_factory=list)
    denied_task_profiles: list[str] = field(default_factory=list)
    redaction_rules: list[str] = field(default_factory=list)
    source_hash: str = ""
    freshness_timestamp: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AgentIdentity:
    agent_id: str
    allowed_task_types: list[str]
    max_sensitivity: str
    owner: str = "platform"


@dataclass
class TaskRequest:
    task_type: str
    path: str
    prompt: str
    agent_id: str = "secreviewagent"
    user: str = "developer"
    environment: str = "unknown"
    approval_state: str = "none"
    request_id: str = ""
    context_id: str = "default"
    provider: str = "generic"
    model: str = ""
    tokenizer: str = "word"
    token_budget: int | None = None

    def normalized_request_id(self) -> str:
        if self.request_id:
            return self.request_id
        return stable_id(self.task_type, self.path, self.prompt, self.agent_id, self.user)


@dataclass
class ReleasedFact:
    slice_id: str
    sensitivity: str
    facts: list[str]
    refs: list[str]
    token_estimate: int
    source_hash: str = ""
    freshness_timestamp: str = ""
    redaction_notes: list[str] = field(default_factory=list)


@dataclass
class DeniedSlice:
    slice_id: str
    sensitivity: str
    reason: str


@dataclass
class ContextCapsule:
    request_id: str
    task: dict[str, Any]
    facts: list[ReleasedFact]
    denied: list[DeniedSlice]
    policy_version: str
    expires_at: str
    cache_hit: bool
    audit_id: str
    capsule_hash: str
    generated_at: str = ""
    source_manifest: list[dict[str, Any]] = field(default_factory=list)
    freshness_warnings: list[str] = field(default_factory=list)
    redaction_notes: list[str] = field(default_factory=list)
    approval_required_slice_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ContextInsight:
    severity: str
    title: str
    message: str
    source_refs: list[str]
    recommendation: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GatewayMetrics:
    request_id: str
    cache_hit: bool
    full_context_tokens: int
    capsule_tokens: int
    token_reduction_percent: float
    released_slice_count: int
    denied_slice_count: int
    tokenizer: str = "word"
    measurement_source: str = "deterministic_word_proxy"
    reusable_prefix_tokens: int = 0
    token_budget: int | None = None
    token_budget_status: str = "not_set"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()
