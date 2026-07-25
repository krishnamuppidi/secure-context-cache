from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CompressionResult:
    text: str
    applied: bool
    compressor: str
    original_tokens: int
    compressed_tokens: int
    reason: str


class LLMLingua2Compressor:
    """Optional post-authorization compressor with fail-safe term preservation."""

    name = "llmlingua-2"

    def __init__(self, model_name: str | None = None) -> None:
        try:
            from llmlingua import PromptCompressor
        except ImportError as exc:  # pragma: no cover - optional heavyweight dependency
            raise RuntimeError(
                "Install compression support with: "
                "pip install 'secure-context-cache[compression]'"
            ) from exc
        kwargs = {}
        if model_name:
            kwargs["model_name"] = model_name
        self._compressor = PromptCompressor(**kwargs)

    def compress(
        self,
        text: str,
        *,
        original_tokens: int,
        target_token: int,
        required_terms: tuple[str, ...] = (),
    ) -> CompressionResult:
        if target_token >= original_tokens:
            return CompressionResult(
                text,
                False,
                self.name,
                original_tokens,
                original_tokens,
                "target is not smaller than the authorized capsule",
            )
        raw = self._compressor.compress_prompt(
            text,
            target_token=target_token,
            force_tokens=list(required_terms),
        )
        compressed = str(raw.get("compressed_prompt", text))
        missing = [term for term in required_terms if term.lower() not in compressed.lower()]
        if missing:
            return CompressionResult(
                text,
                False,
                self.name,
                original_tokens,
                original_tokens,
                "required terms were not preserved; original authorized capsule returned",
            )
        compressed_tokens = int(raw.get("compressed_tokens", target_token))
        return CompressionResult(
            compressed,
            True,
            self.name,
            original_tokens,
            compressed_tokens,
            "compressed after authorization; caller must still apply its quality gate",
        )
