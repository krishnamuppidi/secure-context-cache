from __future__ import annotations

from .models import ContextCapsule, ContextSlice, GatewayMetrics
from .optimization import render_stable_context
from .tokenization import count_facts, resolve_token_counter


def compute_metrics(
    capsule: ContextCapsule,
    all_slices: list[ContextSlice],
    *,
    tokenizer: str = "word",
    model: str = "",
    token_budget: int | None = None,
) -> GatewayMetrics:
    counter = resolve_token_counter(tokenizer, model=model)
    full_context_tokens = sum(count_facts(counter, item.facts) for item in all_slices)
    capsule_tokens = sum(count_facts(counter, item.facts) for item in capsule.facts)
    reusable_prefix_tokens = counter.count(render_stable_context(capsule))
    if full_context_tokens:
        reduction = round((1 - capsule_tokens / full_context_tokens) * 100, 2)
    else:
        reduction = 0.0
    if token_budget is None:
        budget_status = "not_set"
    elif reusable_prefix_tokens <= token_budget:
        budget_status = "within_budget"
    else:
        budget_status = "over_budget"
    return GatewayMetrics(
        request_id=capsule.request_id,
        cache_hit=capsule.cache_hit,
        full_context_tokens=full_context_tokens,
        capsule_tokens=capsule_tokens,
        token_reduction_percent=reduction,
        released_slice_count=len(capsule.facts),
        denied_slice_count=len(capsule.denied),
        tokenizer=counter.name,
        measurement_source=counter.measurement_source,
        reusable_prefix_tokens=reusable_prefix_tokens,
        token_budget=token_budget,
        token_budget_status=budget_status,
    )
