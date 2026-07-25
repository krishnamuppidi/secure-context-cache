from __future__ import annotations

from pathlib import Path

from agent_context_gateway.gateway import AgentContextGateway
from agent_context_gateway.models import TaskRequest
from agent_context_gateway.optimization import build_optimization_plan, render_stable_context
from agent_context_gateway.provider_usage import normalize_provider_usage
from agent_context_gateway.tokenization import WordTokenCounter, resolve_token_counter

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_REPO = ROOT / "examples" / "sample_repo"


def test_optimization_plan_has_stable_prefix_and_security_scoped_namespace() -> None:
    gateway = AgentContextGateway()
    _graph, slices = gateway.load_context(SAMPLE_REPO)
    task = TaskRequest(
        task_type="iac_security",
        path="terraform/prod/payments/lambda.tf",
        prompt="review",
        agent_id="secreviewagent",
        environment="prod",
        context_id="payments",
        provider="openai",
        token_budget=100,
    )
    capsule, metrics = gateway.request_capsule(
        task,
        slices,
        api_key="demo-secreviewagent-key",
    )
    plan = build_optimization_plan(capsule, metrics, task)
    assert plan.strategy == "measure-select-reuse-compress-route-verify"
    assert plan.cache_namespace
    assert plan.stable_prefix_hash
    assert capsule.request_id not in plan.stable_context
    assert capsule.expires_at not in plan.stable_context
    assert metrics.token_budget_status == "within_budget"


def test_stable_context_does_not_include_denied_content(tmp_path: Path) -> None:
    gateway = AgentContextGateway()
    result = gateway.run_demo(SAMPLE_REPO, tmp_path)
    rendered = render_stable_context(result.capsule)
    released_ids = {item.slice_id for item in result.capsule.facts}
    assert all(item.slice_id not in rendered for item in result.capsule.denied)
    assert released_ids


def test_word_counter_is_dependency_free_and_deterministic() -> None:
    counter = resolve_token_counter("word")
    assert isinstance(counter, WordTokenCounter)
    assert counter.count("one two three") == 3
    assert counter.measurement_source == "deterministic_word_proxy"


def test_provider_usage_normalization() -> None:
    openai = normalize_provider_usage(
        "openai",
        {
            "input_tokens": 100,
            "input_tokens_details": {"cached_tokens": 80},
            "output_tokens": 20,
        },
    )
    anthropic = normalize_provider_usage(
        "anthropic",
        {
            "input_tokens": 100,
            "cache_read_input_tokens": 70,
            "cache_creation_input_tokens": 10,
            "output_tokens": 25,
        },
    )
    bedrock = normalize_provider_usage(
        "bedrock",
        {
            "inputTokens": 100,
            "cacheReadInputTokens": 60,
            "cacheWriteInputTokens": 20,
            "outputTokens": 30,
        },
    )
    assert openai.cached_input_tokens == 80
    assert anthropic.cache_write_tokens == 10
    assert bedrock.output_tokens == 30
