from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ProviderUsage:
    provider: str
    input_tokens: int
    cached_input_tokens: int
    cache_write_tokens: int
    output_tokens: int
    measurement_source: str = "provider_reported"

    def to_dict(self) -> dict:
        return asdict(self)


def normalize_provider_usage(provider: str, usage: dict[str, Any]) -> ProviderUsage:
    """Normalize common provider usage payloads without treating estimates as invoices."""
    normalized = provider.lower()
    if normalized == "openai":
        details = usage.get("input_tokens_details", {}) or {}
        return ProviderUsage(
            provider="openai",
            input_tokens=int(usage.get("input_tokens", usage.get("prompt_tokens", 0))),
            cached_input_tokens=int(details.get("cached_tokens", 0)),
            cache_write_tokens=0,
            output_tokens=int(usage.get("output_tokens", usage.get("completion_tokens", 0))),
        )
    if normalized == "anthropic":
        return ProviderUsage(
            provider="anthropic",
            input_tokens=int(usage.get("input_tokens", 0)),
            cached_input_tokens=int(usage.get("cache_read_input_tokens", 0)),
            cache_write_tokens=int(usage.get("cache_creation_input_tokens", 0)),
            output_tokens=int(usage.get("output_tokens", 0)),
        )
    if normalized in {"bedrock", "amazon-bedrock", "aws-bedrock"}:
        return ProviderUsage(
            provider="bedrock",
            input_tokens=int(usage.get("inputTokens", 0)),
            cached_input_tokens=int(usage.get("cacheReadInputTokens", 0)),
            cache_write_tokens=int(usage.get("cacheWriteInputTokens", 0)),
            output_tokens=int(usage.get("outputTokens", 0)),
        )
    raise ValueError("provider must be openai, anthropic, or bedrock")
