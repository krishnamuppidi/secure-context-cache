# Policy Guide

Gateway decisions combine two layers:

1. **Identity grants**: allowed task types and maximum sensitivity for the authenticated workload.
2. **Task policy**: sensitivity limit by task, path relevance, approval requirements, TTL, and
   freshness warnings.

The more restrictive layer wins.

## Default Policy

`config/policy.example.json` defines:

```json
{
  "version": "2026-06-30",
  "ttl_minutes": 30,
  "max_sensitivity_by_task": {
    "code_review": "medium",
    "iac_security": "high",
    "incident_triage": "high",
    "onboarding": "low",
    "architecture_qa": "medium"
  },
  "required_path_match_tasks": ["code_review", "iac_security"],
  "approval_required_sensitivities": ["restricted"],
  "max_slice_age_days": 30
}
```

| Key | Meaning |
| --- | --- |
| `version` | Identifier recorded in capsules and audits |
| `ttl_minutes` | Capsule expiration window |
| `max_sensitivity_by_task` | Highest slice sensitivity each task may receive |
| `required_path_match_tasks` | Tasks that require path/reference relevance |
| `approval_required_sensitivities` | Sensitivities denied unless a trusted approval exists |
| `max_slice_age_days` | Age threshold that produces a freshness warning |

Policy loading is a top-level merge with safe defaults. If an override supplies
`max_sensitivity_by_task`, it replaces the entire default map; include every task the deployment
needs.

## Sensitivity Inference

The current scanner uses deterministic heuristics:

- **high**: path or first 4,000 text characters contain `iam`, `role`, `policy`, `secret`, `kms`,
  `token`, or `prod`;
- **medium**: they contain `vpc`, `security_group`, `database`, `rds`, or `lambda`;
- **low**: none of those terms match.

The scanner does not automatically assign `restricted`. Production deployments should integrate an
authoritative classification source or preprocessing stage. Heuristics are not DLP and can produce
false positives or false negatives.

## Relevance

For `code_review` and `iac_security`, a slice is relevant when the requested path matches the slice
scope/reference or a non-empty path component appears in its references. Other tasks use a simple
task/environment relevance rule. This is intentionally conservative and deterministic; it is not
semantic search.

## Local Policy Configuration

Mount or create a JSON policy and set it before the API process starts:

```bash
export ACG_POLICY_FILE=/absolute/path/to/policy.json
uvicorn agent_context_gateway.api:app
```

The policy is loaded at process startup. Restart the process after a policy change.

Local identity grants are configured separately:

```bash
export ACG_LOCAL_AGENT_ID=architecture-agent
export ACG_LOCAL_API_KEY='<random secret>'
export ACG_LOCAL_ALLOWED_TASK_TYPES=architecture_qa,onboarding
export ACG_LOCAL_MAX_SENSITIVITY=medium
```

## AWS Policy Configuration

Set deployment inputs before running `deploy.sh`:

```bash
export ACG_POLICY_FILE=/absolute/path/to/policy.json
export ACG_ALLOWED_TASK_TYPES=code_review,iac_security,architecture_qa
export ACG_MAX_SENSITIVITY=high
./deploy/aws/deploy.sh
```

The deployment packages the selected policy as `config/policy.json`, passes identity limits to
Terraform, updates Lambda, and runs an authenticated smoke test. Each deployment currently creates
one evaluation Cognito client with the configured grants. Production should use distinct clients or
workload identities with per-client grants.

## Decision Order

A slice is denied when any of these is true:

1. the identity is not allowed to request the task type;
2. the slice explicitly denies the task profile;
3. the slice allows a task-profile list that does not include this task;
4. restricted context requires approval and no trusted approval is present;
5. identity or task sensitivity is lower than the slice sensitivity; or
6. the slice is not relevant to the requested scope.

Denied decisions include a reason and appear in the capsule and AWS audit table.

## Approval Boundary

Library consumers can set `TaskRequest.approval_state="approved"`. The HTTP evaluation API does not
accept caller-asserted approval because that would let the requester approve itself. The bundled
AWS identity configuration also caps sensitivity at `high`; it cannot release `restricted` context.
A production approval integration needs a separately authorized restricted identity, should verify
a signed approval or query a trusted workflow service, confirm request ID, context, task, path,
approver, and expiry, and then set approval state inside the trusted gateway boundary.

## Policy Change Procedure

1. Copy the example policy and assign a new immutable `version`.
2. Validate JSON: `python -m json.tool policy.json`.
3. Run `pytest -q` and a local demo with representative allowed and denied tasks.
4. Review source sensitivity classifications and denial reasons.
5. Deploy without `--auto-approve` and inspect the Terraform plan.
6. Run authenticated positive and negative API tests.
7. Record the policy version and rollout time.
8. Retain the prior policy for rollback.

## Recommended Production Extensions

- Replace heuristic sensitivity with repository labels, data catalog classification, or DLP.
- Use OPA, Cedar, or an internal policy decision service.
- Bind workload identity to context IDs, task profiles, and environments.
- Sign approval assertions and capsules.
- Export policy decisions to immutable audit storage.
- Add automated regression cases for every policy change.
