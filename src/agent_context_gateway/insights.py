from __future__ import annotations

from .models import ContextCapsule, ContextInsight


def generate_context_insights(capsule: ContextCapsule) -> list[ContextInsight]:
    facts = " ".join(" ".join(item.facts) for item in capsule.facts).lower()
    refs = sorted({ref for item in capsule.facts for ref in item.refs})
    insights: list[ContextInsight] = []

    if capsule.cache_hit:
        insights.append(
            ContextInsight(
                severity="info",
                title="Cached context selection reused",
                message="The gateway reused a prior slice-selection pattern for this task scope.",
                source_refs=refs,
                recommendation="Track cache hit rate by task family to measure token savings.",
            )
        )
    if "iam" in facts or "role" in facts or "policy" in facts:
        insights.append(
            ContextInsight(
                severity="high",
                title="High-sensitivity identity context released",
                message=(
                    "The capsule contains identity or policy-related context. This can be valid "
                    "for platform tasks, but should remain task-scoped and auditable."
                ),
                source_refs=refs,
                recommendation="Preserve the audit record and avoid forwarding the capsule outside the task boundary.",
            )
        )
    if "prod" in facts or "production" in facts:
        insights.append(
            ContextInsight(
                severity="medium",
                title="Production-scoped context released",
                message="The capsule contains production-scoped context.",
                source_refs=refs,
                recommendation="Use shorter TTLs and stricter release policy for production task capsules.",
            )
        )
    if not insights:
        insights.append(
            ContextInsight(
                severity="info",
                title="Minimal context capsule",
                message="No high-sensitivity identity or production signals were released in this capsule.",
                source_refs=refs,
                recommendation="Continue monitoring token savings and context denial rates.",
            )
        )
    return insights
