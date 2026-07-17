from __future__ import annotations

from .models import AgentIdentity, ContextSlice, DeniedSlice, TaskRequest

SENSITIVITY_RANK = {"low": 0, "medium": 1, "high": 2, "restricted": 3}

DEFAULT_POLICY = {
    "version": "2026-06-30",
    "ttl_minutes": 30,
    "max_sensitivity_by_task": {
        "code_review": "medium",
        "iac_security": "high",
        "incident_triage": "high",
        "onboarding": "low",
        "architecture_qa": "medium",
    },
    "required_path_match_tasks": ["code_review", "iac_security"],
    "approval_required_sensitivities": ["restricted"],
}


def rank(value: str) -> int:
    return SENSITIVITY_RANK.get(value, 0)


def allowed_by_sensitivity(slice_: ContextSlice, identity: AgentIdentity, task: TaskRequest, policy: dict) -> bool:
    task_max = policy["max_sensitivity_by_task"].get(task.task_type, "low")
    max_allowed = min(rank(identity.max_sensitivity), rank(task_max))
    return rank(slice_.sensitivity) <= max_allowed


def relevant_to_task(slice_: ContextSlice, task: TaskRequest, policy: dict) -> bool:
    prompt = task.prompt.lower()
    path = task.path.lower()
    scope = slice_.scope.lower()
    refs = " ".join(slice_.refs).lower()
    facts = " ".join(slice_.facts).lower()
    if task.task_type in policy.get("required_path_match_tasks", []):
        return path in scope or path in refs or any(part and part in refs for part in path.split("/"))
    terms = [term for term in [task.task_type, "service", "policy", "runbook"] if term in prompt]
    return bool(set(terms) & set(facts.split())) or task.environment == slice_.environment


def decide_slice(slice_: ContextSlice, identity: AgentIdentity, task: TaskRequest, policy: dict) -> DeniedSlice | None:
    if task.task_type not in identity.allowed_task_types:
        return DeniedSlice(slice_.id, slice_.sensitivity, f"agent is not allowed for {task.task_type}")
    if task.task_type in slice_.denied_task_profiles:
        return DeniedSlice(slice_.id, slice_.sensitivity, f"slice denies task profile {task.task_type}")
    if slice_.allowed_task_profiles and task.task_type not in slice_.allowed_task_profiles:
        return DeniedSlice(slice_.id, slice_.sensitivity, f"slice is not approved for task profile {task.task_type}")
    if slice_.sensitivity in policy.get("approval_required_sensitivities", []) and task.approval_state != "approved":
        return DeniedSlice(slice_.id, slice_.sensitivity, "approval required for restricted context")
    if not allowed_by_sensitivity(slice_, identity, task, policy):
        return DeniedSlice(slice_.id, slice_.sensitivity, "sensitivity exceeds policy")
    if not relevant_to_task(slice_, task, policy):
        return DeniedSlice(slice_.id, slice_.sensitivity, "not relevant to task scope")
    return None
