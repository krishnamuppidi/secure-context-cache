# Agent Context Gateway AI

**Agent Context Gateway AI (ACG AI)** is a production-oriented framework that turns Secure Context Cache
into a deployable enterprise AI context and cost-control product pattern:

> Cache approved enterprise context once, release only task-scoped context capsules to AI agents,
> and reduce token spend while preserving access control, auditability, and agent usefulness.

The framework is designed for companies that want AI developer agents, internal assistants,
incident copilots, architecture question-answering tools, and platform APIs without giving every
agent unrestricted enterprise memory.

## Why This Exists

AI agents need context to be useful. Enterprise context is sensitive:

- repositories and ownership
- Infrastructure-as-Code relationships
- service dependencies
- IAM and network paths
- runbooks and escalation workflows
- deployment history
- policy and exception records

Naively pasting all of that into every agent prompt wastes tokens and can expose attack paths.
Agent Context Gateway gives agents enough context to do the task, but not the full memory store.

This is aligned with the industry direction Brian Armstrong described for Coinbase: keep AI usage
high while reducing cost through caching, lean context, routing, and spend visibility. ACG adds the
enterprise security layer: least-privilege context, access policy, audit records, and controlled
context release.

## Core Capabilities

- Canonical context graph from repositories, IaC, docs, and service metadata.
- Context slices tagged by path, environment, task, sensitivity, and owner.
- Cache hit tracking for repeated agent tasks.
- Policy-based release of only the slices required for a task.
- Temporary task capsules for prompts.
- Context insight generation for released task capsules.
- Audit records for selected, denied, cached, and released context.
- Token/cost visibility for full-context vs gateway-assisted prompts.
- CLI for local use and CI.
- Optional FastAPI service for internal platform integration.
- Reference deployment templates for local, Kubernetes, and AWS-oriented review.

## Architecture

```text
Repo/IaC/Docs/Metadata
        |
        v
Context Ingestor -> Context Graph -> Slice Builder -> Slice Cache
                                                |
Agent Request -> Policy Engine -> Capsule Builder -> Agent/API
                                                |
                                        Audit + Cost Metrics
```

SecReviewAgent is one background use case, not the product scope. The product is the gateway:
secure cached context, task-scoped release, audit, and token/cost visibility for many agents.

## Quick Start

```bash
cd agent-context-gateway
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"

acg demo --repo examples/sample_repo --out build/demo
```

Expected output:

```text
capsule_facts=... denied=... cache_hit=... audit_id=...
```

Generated files:

- `build/demo/context-graph.json`
- `build/demo/context-slices.json`
- `build/demo/context-capsule.json`
- `build/demo/context-insights.json`
- `build/demo/audit-record.json`
- `build/demo/metrics.json`

## CLI Examples

Build a context graph:

```bash
acg ingest examples/sample_repo --out build/context-graph.json
```

Build slices:

```bash
acg slice build/context-graph.json --out build/context-slices.json
```

Request a task-scoped capsule:

```bash
acg capsule build/context-slices.json \
  --task-type iac_security \
  --path terraform/prod/payments/lambda.tf \
  --prompt "Review this Terraform change for security and blast-radius risk" \
  --out build/context-capsule.json \
  --audit-out build/audit-record.json
```

Generate context insights:

```bash
acg insights build/context-capsule.json --out build/context-insights.json
```

## API Mode

```bash
pip install -e ".[api]"
uvicorn agent_context_gateway.api:app --reload
```

Endpoints:

- `GET /health`
- `POST /v1/capsules`
- `POST /v1/insights`

## Using Amazon Cognito for Authentication

Amazon Cognito can be used as the identity provider in front of Agent Context Gateway when the
gateway is deployed as an internal API. In this pattern, Cognito authenticates users or service
clients, issues JWT access tokens, and the gateway uses token claims to decide which context slices
can be released for a task.

Typical flow:

```text
User or Agent Client
        |
        v
Amazon Cognito User Pool
        |
        v
JWT Access Token
        |
        v
API Gateway / ALB / Service Middleware
        |
        v
Agent Context Gateway Policy Engine
        |
        v
Task-Scoped Context Capsule
```

Recommended claim mapping:

- `sub`: stable caller identity for audit records.
- `client_id` or `aud`: application or agent identity.
- `cognito:groups`: team, role, or environment access groups.
- custom claims such as `tenant`, `environment`, or `repo_scope`: policy inputs for context release.

Example policy request shape after JWT validation:

```json
{
  "agent": "iac-review-agent",
  "identity": {
    "provider": "cognito",
    "subject": "user-or-client-sub",
    "client_id": "agent-client-id",
    "groups": ["platform-engineering"],
    "environment": "prod"
  },
  "task_type": "iac_security_review",
  "path": "terraform/prod/payments/lambda.tf"
}
```

Deployment options:

- API Gateway with a Cognito authorizer validates the token before traffic reaches the gateway.
- Application Load Balancer with Cognito authentication handles browser-based sign-in.
- Service middleware validates Cognito JWTs directly using the user pool JWKS endpoint.

Policy guidance:

- Treat Cognito authentication as identity proof, not automatic authorization.
- Map groups and custom claims to allowed repositories, environments, task types, and sensitivity
  levels.
- Deny context release by default when claims are missing, expired, or outside the requested scope.
- Store caller identity, client identity, task type, selected slices, denied slices, and token
  metadata in audit records.
- Use short token lifetimes for interactive agents and separate app clients for automated agents.

## Production Integration Pattern

For production, replace local demo pieces with enterprise services:

- identity: SSO/OIDC service identity, workload identity, or GitHub App identity
- secrets: KMS, Vault, or cloud secret manager
- storage: encrypted object store or database with row-level access policy
- audit: immutable log sink, SIEM, or record store
- policy: OPA, Cedar, Rego, or internal policy service
- model routing: internal LLM gateway with cost and cache telemetry
- deployment: private Kubernetes service behind internal gateway

## Product Positioning

Agent Context Gateway is for platform teams that want:

- lower token usage without lowering agent usefulness
- secure shared memory for multiple agents
- secure context release for internal AI agents
- audit-ready AI governance
- reusable internal platform integration
- visibility into AI context cost and cache hit rate

This clean code copy intentionally includes only source, tests, examples, config, and deploy
templates. Generated artifacts, site files, and private deployment outputs are excluded.

## License

See `LICENSE`.

## Disclaimer

The views and opinions expressed in this repository are solely those of the author and do not
represent or reflect the views, positions, policies, or opinions of the author's employer or any
affiliated organization. The content is provided for informational purposes only.
