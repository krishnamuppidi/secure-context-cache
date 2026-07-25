from __future__ import annotations

from dataclasses import dataclass, field

from .models import AgentIdentity, ContextSlice, TaskRequest, stable_hash, stable_id


@dataclass
class CacheEntry:
    key: str
    slice_ids: list[str]
    hits: int = 0
    policy_version: str = ""
    source_manifest_hash: str = ""


@dataclass
class ContextSliceCache:
    entries: dict[str, CacheEntry] = field(default_factory=dict)

    def key_for(
        self,
        task: TaskRequest,
        *,
        identity: AgentIdentity | None = None,
        policy_version: str = "",
        source_manifest_hash: str = "",
    ) -> str:
        identity_scope = ""
        if identity is not None:
            identity_scope = stable_hash(
                "|".join(
                    [
                        identity.agent_id,
                        identity.max_sensitivity,
                        ",".join(sorted(identity.allowed_task_types)),
                    ]
                )
            )
        selection_intent = ",".join(
            term
            for term in ("service", "policy", "runbook")
            if term in task.prompt.lower()
        )
        return stable_id(
            "selection-plan",
            task.context_id,
            task.agent_id,
            identity_scope,
            task.task_type,
            task.path,
            selection_intent,
            task.environment,
            task.approval_state,
            policy_version,
            source_manifest_hash,
        )

    def get(
        self,
        task: TaskRequest,
        *,
        identity: AgentIdentity | None = None,
        policy_version: str = "",
        source_manifest_hash: str = "",
    ) -> CacheEntry | None:
        key = self.key_for(
            task,
            identity=identity,
            policy_version=policy_version,
            source_manifest_hash=source_manifest_hash,
        )
        entry = self.entries.get(key)
        if entry:
            entry.hits += 1
        return entry

    def put(
        self,
        task: TaskRequest,
        slices: list[ContextSlice],
        *,
        identity: AgentIdentity | None = None,
        policy_version: str = "",
        source_manifest_hash: str = "",
    ) -> CacheEntry:
        key = self.key_for(
            task,
            identity=identity,
            policy_version=policy_version,
            source_manifest_hash=source_manifest_hash,
        )
        entry = CacheEntry(
            key=key,
            slice_ids=[item.id for item in slices],
            policy_version=policy_version,
            source_manifest_hash=source_manifest_hash,
        )
        self.entries[key] = entry
        return entry
