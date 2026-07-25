from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from .models import (
    AgentIdentity,
    ContextCapsule,
    ContextSlice,
    DeniedSlice,
    ReleasedFact,
    TaskRequest,
    stable_hash,
    stable_id,
    utc_in,
    utc_now,
)
from .policy import DEFAULT_POLICY, decide_slice


def capsule_hash_for(
    request_id: str,
    released: list[ReleasedFact],
    denied: list,
    policy_version: str,
) -> str:
    raw = json.dumps(
        {
            "request_id": request_id,
            "facts": [item.__dict__ for item in released],
            "denied": [item.__dict__ for item in denied],
            "policy": policy_version,
        },
        sort_keys=True,
    )
    return stable_hash(raw)


def _freshness_warning(slice_: ContextSlice, *, max_age_days: int = 30) -> str:
    if not slice_.freshness_timestamp:
        return f"slice {slice_.id} has no freshness timestamp"
    try:
        timestamp = datetime.fromisoformat(slice_.freshness_timestamp)
    except ValueError:
        return f"slice {slice_.id} has an unreadable freshness timestamp"
    if timestamp.tzinfo is None:
        return f"slice {slice_.id} freshness timestamp has no timezone"
    now = datetime.now(UTC)
    if timestamp > now + timedelta(minutes=5):
        return f"slice {slice_.id} freshness timestamp is in the future"
    age_days = (now - timestamp).days
    if age_days > max_age_days:
        return f"slice {slice_.id} is {age_days} days old"
    return ""


def build_capsule(
    task: TaskRequest,
    identity: AgentIdentity,
    slices: list[ContextSlice],
    *,
    cache_hit: bool = False,
    policy: dict | None = None,
    enforce_freshness: bool = False,
) -> ContextCapsule:
    active_policy = policy or DEFAULT_POLICY
    released: list[ReleasedFact] = []
    denied = []
    source_manifest = []
    freshness_warnings = []
    redaction_notes = []
    for slice_ in slices:
        decision = decide_slice(slice_, identity, task, active_policy)
        if decision is not None:
            denied.append(decision)
            continue
        warning = _freshness_warning(slice_, max_age_days=active_policy.get("max_slice_age_days", 30))
        if warning:
            freshness_warnings.append(warning)
            if enforce_freshness:
                denied.append(DeniedSlice(slice_.id, slice_.sensitivity, warning))
                continue
        redaction_notes.extend(f"{slice_.id}: {rule}" for rule in slice_.redaction_rules)
        source_manifest.append(
            {
                "slice_id": slice_.id,
                "refs": slice_.refs,
                "source_hash": slice_.source_hash,
                "freshness_timestamp": slice_.freshness_timestamp,
                "owner": slice_.owner,
                "environment": slice_.environment,
                "sensitivity": slice_.sensitivity,
                "parser_version": slice_.metadata.get("parser_version", "unknown"),
            }
        )
        released.append(
            ReleasedFact(
                slice_id=slice_.id,
                sensitivity=slice_.sensitivity,
                facts=slice_.facts,
                refs=slice_.refs,
                token_estimate=slice_.token_estimate,
                source_hash=slice_.source_hash,
                freshness_timestamp=slice_.freshness_timestamp,
                redaction_notes=slice_.redaction_rules,
            )
        )
    request_id = task.normalized_request_id()
    audit_id = stable_id("audit", request_id, identity.agent_id, uuid4().hex)
    return ContextCapsule(
        request_id=request_id,
        task=task.__dict__,
        facts=released,
        denied=denied,
        policy_version=active_policy["version"],
        expires_at=utc_in(active_policy.get("ttl_minutes", 30)),
        cache_hit=cache_hit,
        audit_id=audit_id,
        capsule_hash=capsule_hash_for(
            request_id,
            released,
            denied,
            active_policy["version"],
        ),
        generated_at=utc_now(),
        source_manifest=source_manifest,
        freshness_warnings=freshness_warnings,
        redaction_notes=sorted(set(redaction_notes)),
        approval_required_slice_ids=[
            item.slice_id for item in denied if "approval required" in item.reason
        ],
    )
