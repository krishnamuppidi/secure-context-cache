from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .cache import ContextSliceCache
from .capsule import build_capsule, capsule_hash_for
from .identity import AgentRegistry
from .ingest import scan_repo
from .insights import generate_context_insights
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
    stable_hash,
)
from .optimization import OptimizationPlan, build_optimization_plan
from .policy import load_policy
from .slices import build_slices


@dataclass
class GatewayResult:
    graph: ContextGraph
    slices: list[ContextSlice]
    capsule: ContextCapsule
    insights: list[ContextInsight]
    metrics: GatewayMetrics
    optimization: OptimizationPlan
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

    def load_context(
        self,
        repo: Path,
        *,
        context_id: str = "default",
        manifest_hash: str = "",
    ) -> tuple[ContextGraph, list[ContextSlice]]:
        graph = scan_repo(repo)
        slices = build_slices(graph)
        if self.slice_store is not None:
            self.slice_store.put_many(
                slices,
                context_id=context_id,
                manifest_hash=manifest_hash,
            )
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
        policy_version = str(self.policy.get("version", "unknown"))
        policy_fingerprint = stable_hash(json.dumps(self.policy, sort_keys=True))
        source_manifest_hash = stable_hash(
            json.dumps(
                [
                    {
                        "id": item.id,
                        "source_hash": item.source_hash,
                        "facts": item.facts,
                        "refs": item.refs,
                        "sensitivity": item.sensitivity,
                        "environment": item.environment,
                    }
                    for item in sorted(slices, key=lambda value: value.id)
                ],
                sort_keys=True,
            )
        )
        cache_entry = self.cache.get(
            task,
            identity=identity,
            policy_version=f"{policy_version}:{policy_fingerprint}",
            source_manifest_hash=source_manifest_hash,
        )
        cache_hit = cache_entry is not None
        candidate_slices = slices
        if cache_entry is not None:
            cached_ids = set(cache_entry.slice_ids)
            # A cached plan narrows the expensive capsule-building path. Every cached
            # slice is still re-authorized below, and the key binds identity, policy,
            # task scope, approval state, context ID, and the source manifest.
            candidate_slices = [item for item in slices if item.id in cached_ids]
        capsule = build_capsule(
            task,
            identity,
            candidate_slices,
            cache_hit=cache_hit,
            policy=self.policy,
        )
        if cache_entry is not None:
            # Preserve an explicit audit reason for slices excluded by the cached plan.
            from .models import DeniedSlice

            selected_or_denied = {item.slice_id for item in capsule.facts}
            selected_or_denied.update(item.slice_id for item in capsule.denied)
            capsule.denied.extend(
                DeniedSlice(
                    slice_id=item.id,
                    sensitivity=item.sensitivity,
                    reason="not selected by cached policy-scoped plan",
                )
                for item in slices
                if item.id not in selected_or_denied
            )
            capsule.capsule_hash = capsule_hash_for(
                capsule.request_id,
                capsule.facts,
                capsule.denied,
                capsule.policy_version,
            )
        if not cache_hit:
            released_ids = {item.slice_id for item in capsule.facts}
            self.cache.put(
                task,
                [item for item in slices if item.id in released_ids],
                identity=identity,
                policy_version=f"{policy_version}:{policy_fingerprint}",
                source_manifest_hash=source_manifest_hash,
            )
        metrics = compute_metrics(
            capsule,
            slices,
            tokenizer=task.tokenizer,
            model=task.model,
            token_budget=task.token_budget,
        )
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
        optimization = build_optimization_plan(capsule, metrics, task)
        insights = self.generate_insights(capsule)
        audit = self.build_audit_record(capsule, metrics)
        write_json(out_dir / "context-graph.json", graph.to_dict())
        write_json(out_dir / "context-slices.json", [item.to_dict() for item in slices])
        write_json(out_dir / "context-capsule.json", capsule.to_dict())
        write_json(out_dir / "context-insights.json", [item.to_dict() for item in insights])
        write_json(out_dir / "audit-record.json", audit)
        write_json(out_dir / "metrics.json", metrics.to_dict())
        write_json(out_dir / "optimization-plan.json", optimization.to_dict())
        return GatewayResult(graph, slices, capsule, insights, metrics, optimization, audit)
