# API Reference

The API exposes health, capsule release, and capsule-plus-insight endpoints. JSON uses UTF-8.

## Base URLs and Authentication

- Local API: `http://127.0.0.1:8000`; send `x-agent-api-key` and an `agent_id` in the body.
- Docker: commonly `http://127.0.0.1:8080`; authentication is the same as local API.
- AWS: use `ACG_API_URL` from `deploy/aws/.acg-deployment.env`; send a Cognito access token as
  `Authorization: Bearer <token>`.

Never place an API key, access token, client ID/secret pair, or deployment environment file in a
prompt or model tool result.

## `GET /health`

No authentication is required.

```json
{"status":"ok","runtime":"local"}
```

AWS returns `"runtime":"aws"`.

## `POST /v1/capsules`

Returns a policy-scoped capsule and token metrics.

### Request

| Field | Type | Required | Default | Behavior |
| --- | --- | --- | --- | --- |
| `context_id` | string | AWS only | `default` | AWS S3 source name; 1-64 letters, numbers, dot, underscore, or hyphen |
| `repo` | string/null | No | sample repo | Local-only path inside `ACG_ALLOWED_REPO_ROOT`; ignored in AWS mode |
| `task_type` | string | Yes | — | Must be allowed by identity and policy |
| `path` | string | Yes | — | Context-relative path used for scope matching |
| `prompt` | string | Yes | — | Task description used in request identity and relevance checks |
| `agent_id` | string | Local only | `secreviewagent` | Local credential identity; ignored in AWS mode |
| `user` | string | Local only | `developer` | Local audit subject; AWS uses verified JWT claims |
| `environment` | string | No | `unknown` | Common values are `prod`, `stage`, `dev`, and `test` |
| `request_id` | string | No | derived | Caller trace ID; when empty, the gateway derives a stable ID |

AWS example:

```bash
token=$(./deploy/aws/get-token.sh)
curl -sS "$ACG_API_URL/v1/capsules" \
  -H "authorization: Bearer $token" \
  -H 'content-type: application/json' \
  -d '{
    "context_id": "payments-platform",
    "task_type": "iac_security",
    "path": "terraform/prod/payments/lambda.tf",
    "prompt": "Review this change",
    "environment": "prod",
    "request_id": "change-4821"
  }'
```

### Response

```json
{
  "capsule": {
    "request_id": "change-4821",
    "task": {
      "task_type": "iac_security",
      "path": "terraform/prod/payments/lambda.tf",
      "prompt": "Review this change",
      "agent_id": "verified-client-id",
      "user": "verified-client-subject",
      "environment": "prod",
      "approval_state": "none",
      "request_id": "change-4821"
    },
    "facts": [
      {
        "slice_id": "...",
        "sensitivity": "high",
        "facts": ["..."],
        "refs": ["terraform/prod/payments/lambda.tf"],
        "token_estimate": 16,
        "source_hash": "...",
        "freshness_timestamp": "...",
        "redaction_notes": ["..."]
      }
    ],
    "denied": [{"slice_id": "...", "sensitivity": "low", "reason": "not relevant to task scope"}],
    "policy_version": "2026-06-30",
    "expires_at": "...",
    "cache_hit": false,
    "audit_id": "...",
    "capsule_hash": "...",
    "generated_at": "...",
    "source_manifest": [{"slice_id": "...", "refs": ["..."], "source_hash": "..."}],
    "freshness_warnings": [],
    "redaction_notes": [],
    "approval_required_slice_ids": []
  },
  "metrics": {
    "request_id": "change-4821",
    "cache_hit": false,
    "full_context_tokens": 32,
    "capsule_tokens": 16,
    "token_reduction_percent": 50.0,
    "released_slice_count": 1,
    "denied_slice_count": 1
  }
}
```

Callers should reject expired capsules, keep the `request_id` and `audit_id` with downstream traces,
and pass only `capsule.facts` plus necessary source references to a model.

## `POST /v1/insights`

Accepts the same request and returns the same `capsule` and `metrics` plus:

```json
{
  "insights": [
    {
      "severity": "medium",
      "title": "Production-scoped context released",
      "message": "The capsule contains production-scoped context.",
      "source_refs": ["terraform/prod/payments/lambda.tf"],
      "recommendation": "Use shorter TTLs and stricter release policy for production task capsules."
    }
  ]
}
```

Insights are deterministic framework observations, not model-generated analysis or a security scan.

## Errors

| Status | Typical cause | Action |
| --- | --- | --- |
| `400` | Invalid `context_id`, unsafe local path, invalid policy input | Correct the request or configuration |
| `401` | Missing local key or missing/invalid/expired AWS JWT | Get a fresh token or supply the local key |
| `403` | Invalid local credentials or identity not permitted | Check agent ID, key, task grants, and sensitivity limit |
| `404` | Missing local repo or empty/missing AWS context ID | Upload the context and verify its ID |
| `422` | Missing field or wrong JSON type | Compare the body with the request schema |
| `500` | Runtime/configuration error | Check Lambda or local server logs |
| `502`/`504` | Lambda failure or timeout through API Gateway | Check logs and reduce context size |

Policy denials normally return `200` with entries in `capsule.denied`; they are auditable decisions,
not transport errors.

## OpenAPI

Local FastAPI serves `/docs` and `/openapi.json`. The AWS HTTP API provisions only `/health`,
`/v1/capsules`, and `/v1/insights`, so the interactive documentation is not publicly routed in the
evaluation stack.
