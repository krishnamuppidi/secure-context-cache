from __future__ import annotations

from .models import ContextGraph, ContextSlice, stable_id


def estimate_tokens(facts: list[str]) -> int:
    return max(1, sum(len(fact.split()) for fact in facts))


def build_slices(graph: ContextGraph) -> list[ContextSlice]:
    slices: list[ContextSlice] = []
    for node in graph.nodes:
        if node.kind == "repository":
            continue
        facts = [
            f"{node.kind} {node.path} belongs to environment {node.environment}",
            f"sensitivity={node.sensitivity}",
        ]
        if node.sensitivity in {"medium", "high", "restricted"}:
            facts.append(f"{node.path} may affect security posture or operational blast radius")
        redaction_rules = []
        if node.sensitivity in {"high", "restricted"}:
            redaction_rules.append("release derived facts only; do not release raw secrets or credential values")
        slice_id = stable_id("slice", node.path, node.environment, node.sensitivity)
        slices.append(
            ContextSlice(
                id=slice_id,
                scope=node.path,
                slice_type=node.kind,
                facts=facts,
                sensitivity=node.sensitivity,
                refs=[node.path],
                version=graph.generated_at,
                token_estimate=estimate_tokens(facts),
                owner=node.owner,
                environment=node.environment,
                allowed_task_profiles=[],
                denied_task_profiles=[],
                redaction_rules=redaction_rules,
                source_hash=str(node.metadata.get("source_hash", "")),
                freshness_timestamp=str(node.metadata.get("freshness_timestamp", graph.generated_at)),
                metadata={
                    "node_id": node.id,
                    "source_system": node.metadata.get("source_system", "unknown"),
                    "parser_version": node.metadata.get("parser_version", "unknown"),
                },
            )
        )
    return slices
