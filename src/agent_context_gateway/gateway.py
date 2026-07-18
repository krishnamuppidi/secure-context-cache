from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from .cache import ContextSliceCache
from .capsule import build_capsule
from .identity import AgentRegistry
from .insights import generate_context_insights
from .ingest import scan_repo
from .io import write_json
from .metrics import compute_metrics
from .models import (
    AgentIdentity,
    ContextCapsule,
    ContextGraph,
    ContextInsight,
    ContextSlice,
    GatewayMetrics,
    TaskRequest,
)
from .policy import load_policy
from .slices import build_slices


@dataclass
class GatewayResult:
    graph: ContextGraph
    slices: list[ContextSlice]
    capsule: ContextCapsule
    insights: list[ContextInsight]
    metrics: GatewayMetrics
    audit_record: dict


class AgentContextGateway:
    def __init__(
        self,
        registry: AgentRegistry | None = None,
        cache: ContextSliceCache | None = None,
        *,
        policy: dict | None = None,
        audit_store: object | None = None,
        slice_store: object | None = None,
    ) -> None:
        self.registry = registry or AgentRegistry.demo()
        self.cache = cache or ContextSliceCache()
        self.policy = policy or load_policy()
        self.audit_store = audit_store
        self.slice_store = slice_store

    def load_context(self, repo: Path) -> tuple[ContextGraph, list[ContextSlice]]:
        graph = scan_repo(repo)
        slices = build_slices(graph)
        if self.slice_store is not None:
            self.slice_store.put_many(slices)
        return graph, slices

    def request_capsule(
        self,
        task: TaskRequest,
        slices: list[ContextSlice],
        *,
        api_key: str,
    ) -> tuple[ContextCapsule, GatewayMetrics]:
        identity = self.registry.authenticate(task.agent_id, api_key)
        return self.request_capsule_for_identity(task, slices, identity)

    def request_capsule_for_identity(
        self,
        task: TaskRequest,
        slices: list[ContextSlice],
        identity: AgentIdentity,
    ) -> tuple[ContextCapsule, GatewayMetrics]:
        cache_entry = self.cache.get(task)
        cache_hit = cache_entry is not None
        # Policy is authoritative on every request. Cached selection IDs provide
        # repeat-task telemetry but never bypass newer or stricter deny rules.
        capsule = build_capsule(
            task,
            identity,
            slices,
            cache_hit=cache_hit,
            policy=self.policy,
        )
        if not cache_hit:
            released_ids = {item.slice_id for item in capsule.facts}
            self.cache.put(task, [item for item in slices if item.id in released_ids])
        metrics = compute_metrics(capsule, slices)
        if self.audit_store is not None:
            self.audit_store.put(self.build_audit_record(capsule, metrics))
        return capsule, metrics

    @staticmethod
    def build_audit_record(capsule: ContextCapsule, metrics: GatewayMetrics) -> dict:
        task = capsule.task
        return {
            "audit_id": capsule.audit_id,
            "request_id": capsule.request_id,
            "generated_at": capsule.generated_at,
            "agent_id": task.get("agent_id", "unknown"),
            "user": task.get("user", "unknown"),
            "task_type": task.get("task_type", "unknown"),
            "task_path": task.get("path", ""),
            "environment": task.get("environment", "unknown"),
            "approval_state": task.get("approval_state", "none"),
            "policy_version": capsule.policy_version,
            "released_slice_ids": [item.slice_id for item in capsule.facts],
            "denied": [asdict(item) for item in capsule.denied],
            "approval_required_slice_ids": capsule.approval_required_slice_ids,
            "source_manifest": capsule.source_manifest,
            "freshness_warnings": capsule.freshness_warnings,
            "redaction_notes": capsule.redaction_notes,
            "capsule_hash": capsule.capsule_hash,
            "cache_hit": capsule.cache_hit,
            "metrics": metrics.to_dict(),
        }

    def generate_insights(self, capsule: ContextCapsule) -> list[ContextInsight]:
        return generate_context_insights(capsule)

    def run_demo(self, repo: Path, out_dir: Path) -> GatewayResult:
        task = TaskRequest(
            task_type="iac_security",
            path="terraform/prod/payments/lambda.tf",
            prompt="Review this Terraform change for security and blast-radius risk",
            agent_id="secreviewagent",
            user="platform-reviewer",
            environment="prod",
        )
        graph, slices = self.load_context(repo)
        capsule, metrics = self.request_capsule(task, slices, api_key="demo-secreviewagent-key")
        insights = self.generate_insights(capsule)
        audit = self.build_audit_record(capsule, metrics)
        write_json(out_dir / "context-graph.json", graph.to_dict())
        write_json(out_dir / "context-slices.json", [item.to_dict() for item in slices])
        write_json(out_dir / "context-capsule.json", capsule.to_dict())
        write_json(out_dir / "context-insights.json", [item.to_dict() for item in insights])
        write_json(out_dir / "audit-record.json", audit)
        write_json(out_dir / "metrics.json", metrics.to_dict())
        return GatewayResult(graph, slices, capsule, insights, metrics, audit)
