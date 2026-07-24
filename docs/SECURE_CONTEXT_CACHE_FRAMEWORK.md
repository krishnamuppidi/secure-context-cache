# Secure Context Cache Framework

Secure Context Cache is the research and architecture layer for governed context sharing across
enterprise AI agents. Agent Context Gateway AI is its deployable control plane. SecureReviewAgent
is the flagship application used to test the framework on a concrete, reviewable workflow.

## Product Family

```text
Approved enterprise sources
          |
          v
Secure Context Cache framework
  canonical graph -> protected slices -> least-privilege selector
          |
          v
Agent Context Gateway AI
  identity -> policy -> expiring capsule -> audit + token metrics
          |
          v
SecureReviewAgent
  Terraform/Kubernetes change -> security review -> human decision
```

### Secure Context Cache

The framework defines the durable design:

- build one canonical, source-backed context graph;
- divide it into path-, resource-, environment-, sensitivity-, and task-scoped slices;
- keep persistent enterprise context outside the agent;
- release a short-lived capsule containing only approved derived facts;
- preserve source hashes, freshness, policy version, denials, and expiry; and
- audit every context decision.

Its core principle is:

> One canonical context graph, many policy-scoped agent capsules.

### Agent Context Gateway AI

The gateway implements the online control boundary. The public repository provides:

- local CLI and FastAPI evaluation paths;
- Cognito workload identity and API Gateway authentication;
- AWS Lambda execution with IAM roles;
- private KMS-encrypted S3 context storage;
- KMS-encrypted DynamoDB slice, cache, and audit stores;
- deterministic task, path, sensitivity, freshness, and approval policy;
- provider-ready capsule APIs and client examples; and
- token-reduction, cache, release, and denial telemetry.

The gateway remains the API and deployment name so existing `acg` commands, environment variables,
clients, and infrastructure interfaces stay stable.

### SecureReviewAgent

SecureReviewAgent is the flagship application because Infrastructure-as-Code review has:

- repeatable Terraform and Kubernetes inputs;
- security findings that can be checked against must-find cases;
- clear context needs such as IAM, network, environment, policy, and ownership facts;
- measurable token, cost, latency, recall, precision, and reviewer-acceptance outcomes; and
- a human decision point before a change is approved.

The intended benchmark compares changed-files-only, full-context, and Secure Context Cache capsule
paths on the same review set. Token reduction counts as a win only when the capsule path meets the
agreed quality and policy threshold.

## Research Foundation

The paper **“Secure Context Cache: Token-Efficient and Least-Privilege Shared Memory for Enterprise
Developer Agents”** was accepted for presentation and publication at the 2026 5th International
Conference on Engineering and Research Application (ICERA).

The research prototype models 24 developer-agent tasks over 32 reusable context slices and reports:

- 75.3% lower average context tokens than full-context release;
- 95.8% task success;
- 98.6% required-fact coverage;
- 92.3% lower high-sensitivity slice exposure; and
- 93.3% lower attack-path reconstructability.

Those figures are deterministic prototype results, not provider-billed production measurements or
universal performance claims. The public gateway's smaller 32-to-16 fixture exists to make its
measurement behavior reproducible. A company pilot should use provider-reported tokens, real
pricing, and predefined quality gates.

## Commercial Positioning

Secure Context Cache is marketed as a governed context framework, not only as a cache:

- **Efficiency:** reuse approved context and reduce repeated input tokens.
- **Security:** keep unrelated topology and high-sensitivity facts outside the prompt.
- **Quality:** release the relationships a task actually needs.
- **Governance:** bind each capsule to identity, task, source, policy, freshness, and expiry.
- **Evidence:** record what was selected, denied, cached, and released.

The strongest first offer is a 30-day SecureReviewAgent pilot that measures cost per accepted,
correct, policy-compliant review. Successful controls can then be reused for code review, incident
response, architecture Q&A, onboarding, compliance evidence, and FinOps agents.

## Naming Rules

- Use **Secure Context Cache Framework** for the research-backed architecture and overall product
  family.
- Use **Agent Context Gateway AI** for the deployable API, CLI, AWS stack, and integration surface.
- Use **SecureReviewAgent** for the flagship Infrastructure-as-Code security application.
- Do not describe the paper as published until final proceedings evidence is available.
- Do not convert prototype or fixture metrics into production savings claims.
