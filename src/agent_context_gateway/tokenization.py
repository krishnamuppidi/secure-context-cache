from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class TokenCounter(Protocol):
    """Count model-input tokens without coupling the core package to one provider."""

    name: str
    measurement_source: str

    def count(self, text: str) -> int: ...


@dataclass(frozen=True)
class WordTokenCounter:
    """Deterministic dependency-free proxy retained for fixtures and offline use."""

    name: str = "word"
    measurement_source: str = "deterministic_word_proxy"

    def count(self, text: str) -> int:
        return max(1, len(text.split())) if text else 0


class TiktokenCounter:
    """OpenAI-compatible tokenizer loaded only when the optional extra is installed."""

    measurement_source = "model_tokenizer"

    def __init__(self, model: str = "", encoding: str = "o200k_base") -> None:
        try:
            import tiktoken
        except ImportError as exc:  # pragma: no cover - depends on optional package
            raise ValueError(
                "Install tokenizer support with: pip install 'secure-context-cache[tokenizers]'"
            ) from exc
        if model:
            try:
                self._encoding = tiktoken.encoding_for_model(model)
                self.name = f"tiktoken:model:{model}"
                return
            except KeyError:
                pass
        self._encoding = tiktoken.get_encoding(encoding)
        self.name = f"tiktoken:{encoding}"

    def count(self, text: str) -> int:
        return len(self._encoding.encode(text))


def resolve_token_counter(
    tokenizer: str = "word",
    *,
    model: str = "",
) -> TokenCounter:
    normalized = (tokenizer or "word").strip().lower()
    if normalized in {"word", "proxy", "deterministic"}:
        return WordTokenCounter()
    if normalized in {"auto", "tiktoken"}:
        return TiktokenCounter(model=model)
    if normalized.startswith("tiktoken:"):
        return TiktokenCounter(model=model, encoding=normalized.split(":", 1)[1])
    raise ValueError(
        "tokenizer must be 'word', 'auto', 'tiktoken', or 'tiktoken:<encoding>'"
    )


def count_facts(counter: TokenCounter, facts: list[str]) -> int:
    return sum(counter.count(fact) for fact in facts)
