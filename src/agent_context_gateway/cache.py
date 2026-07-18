from __future__ import annotations

from dataclasses import dataclass, field

from .models import ContextSlice, TaskRequest, stable_id


@dataclass
class CacheEntry:
    key: str
    slice_ids: list[str]
    hits: int = 0


@dataclass
class ContextSliceCache:
    entries: dict[str, CacheEntry] = field(default_factory=dict)

    def key_for(self, task: TaskRequest) -> str:
        return stable_id(
            "cache",
            task.normalized_request_id(),
            task.environment,
            task.approval_state,
        )

    def get(self, task: TaskRequest) -> CacheEntry | None:
        key = self.key_for(task)
        entry = self.entries.get(key)
        if entry:
            entry.hits += 1
        return entry

    def put(self, task: TaskRequest, slices: list[ContextSlice]) -> CacheEntry:
        key = self.key_for(task)
        entry = CacheEntry(key=key, slice_ids=[item.id for item in slices])
        self.entries[key] = entry
        return entry
