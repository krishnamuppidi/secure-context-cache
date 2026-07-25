from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .models import ContextSlice, stable_hash, stable_id, utc_now
from .policy import SENSITIVITY_RANK
from .slices import estimate_tokens


@dataclass(frozen=True)
class RetrievedCandidate:
    """A retrieval result that remains a candidate until SCC authorizes its release."""

    candidate_id: str
    content: str
    refs: list[str]
    sensitivity: str = "low"
    environment: str = "unknown"
    owner: str = "unknown"
    source_hash: str = ""
    freshness_timestamp: str = ""
    score: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_context_slice(self) -> ContextSlice:
        candidate_id = self.candidate_id.strip()
        if not candidate_id:
            raise ValueError("retrieval candidate_id cannot be empty")
        if not self.content.strip():
            raise ValueError(f"retrieval candidate {candidate_id!r} has empty content")
        if not self.refs:
            raise ValueError(f"retrieval candidate {candidate_id!r} requires a source ref")
        refs = [ref.strip() for ref in self.refs]
        if any(not ref for ref in refs):
            raise ValueError(f"retrieval candidate {candidate_id!r} has an empty source ref")
        if self.sensitivity not in SENSITIVITY_RANK:
            raise ValueError(f"retrieval candidate {candidate_id!r} has unsupported sensitivity")
        content_hash = stable_hash(self.content)
        if self.source_hash and self.source_hash != content_hash:
            raise ValueError(
                f"retrieval candidate {candidate_id!r} source_hash does not match content"
            )
        scope = refs[0]
        return ContextSlice(
            id=stable_id(
                "retrieval-candidate",
                candidate_id,
                scope,
                content_hash,
            ),
            scope=scope,
            slice_type="retrieval_candidate",
            facts=[self.content],
            sensitivity=self.sensitivity,
            refs=refs,
            version=content_hash[:16],
            token_estimate=estimate_tokens([self.content]),
            owner=self.owner,
            environment=self.environment,
            source_hash=content_hash,
            freshness_timestamp=self.freshness_timestamp or utc_now(),
            metadata={
                **self.metadata,
                "candidate_id": candidate_id,
                "retrieval_score": self.score,
                "source_system": self.metadata.get("source_system", "retrieval"),
                "parser_version": "secure-rag-candidate-v1",
            },
        )


def candidates_to_slices(candidates: list[RetrievedCandidate]) -> list[ContextSlice]:
    seen: set[str] = set()
    slices: list[ContextSlice] = []
    for candidate in candidates:
        candidate_id = candidate.candidate_id.strip()
        if candidate_id in seen:
            raise ValueError(f"duplicate retrieval candidate_id: {candidate_id}")
        seen.add(candidate_id)
        slices.append(candidate.to_context_slice())
    return slices
