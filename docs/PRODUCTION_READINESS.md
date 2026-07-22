# Production Readiness Checklist

The included AWS automation is a controlled evaluation/pilot stack. Production promotion requires
an explicit architecture, security, reliability, data-governance, and operations review.

## Identity and Access

- [ ] One workload identity per agent/application; no shared evaluation client.
- [ ] Context IDs, task types, environments, and sensitivity bound to workload identity.
- [ ] Client secrets stored and rotated through a managed secret service, or replaced by workload
      identity without long-lived shared secrets.
- [ ] Deployer role, runtime role, permission boundary, SCP, and `iam:PassRole` reviewed.
- [ ] Human approvals verified by a trusted service and bound to request scope and expiry.

## Context and Data Governance

- [ ] Approved source inventory, owner, classification, retention, residency, and legal basis.
- [ ] Secret/DLP scanning before upload; `.tfvars`, JSON, YAML, Markdown, and source code reviewed.
- [ ] Authoritative sensitivity labels replace heuristic-only classification.
- [ ] Context size/object quotas and source commit/export provenance enforced.
- [ ] S3 version lifecycle, recovery, deletion, and legal-hold behavior defined.

## Policy and Agent Safety

- [ ] Versioned policy reviewed as code with positive and negative regression tests.
- [ ] OPA, Cedar, or equivalent policy service considered for centralized decisions.
- [ ] Empty/denied capsule never falls back to unrestricted source context.
- [ ] Capsules treated as untrusted data in prompts; prompt-injection tests pass.
- [ ] Cross-agent, cross-context, path traversal, over-broad release, and stale-context tests pass.
- [ ] Capsule integrity/signing requirement decided.

## Platform Security

- [ ] WAF/rate limits, TLS policy, private networking, egress policy, and DDoS controls reviewed.
- [ ] KMS key policy, rotation, separation of duties, and deletion recovery reviewed.
- [ ] Terraform state uses encrypted remote backend, locking, versioning, least privilege, and logs.
- [ ] Dependencies, image/package provenance, vulnerability scanning, signing, and SBOM implemented.
- [ ] CloudTrail and security monitoring cover management and data events as required.

## Reliability and Scale

- [ ] Representative load/latency tests include real context object counts and sizes.
- [ ] Asynchronous ingestion or persistent slice reads replace per-request full-prefix scanning where
      necessary.
- [ ] Concurrency, Lambda memory, API timeout, DynamoDB, S3, KMS, and Cognito limits tested.
- [ ] Multi-region/DR architecture, RTO, RPO, backup, restore, and failover tested.
- [ ] Rollback and client-credential rotation tested without unacceptable downtime.

## Observability and Cost

- [ ] Metrics, dashboards, alarms, traces, structured logs, and immutable audit export implemented.
- [ ] Sensitive prompts, context, tokens, and credentials excluded from telemetry.
- [ ] Denial rates, freshness, capsule sizes, estimated token reduction, latency, and errors monitored.
- [ ] Budgets, anomaly detection, log retention, table growth, S3 versions, and KMS fixed cost tracked.
- [ ] Estimated token metrics clearly separated from measured model-provider usage/cost.

## Operations and Compliance

- [ ] Service owner, data owner, security owner, on-call, escalation, and change process assigned.
- [ ] Incident response covers credential exposure, context exposure, policy bypass, and model traces.
- [ ] Audit retention, access, export, evidence integrity, and privacy requirements implemented.
- [ ] Runbooks for deploy, verify, update, rollback, rotate, restore, and teardown tested.
- [ ] Disclaimer and internal acceptable-use boundaries reviewed by the organization.

Production readiness is an organizational decision. Passing this checklist requires evidence from
the target environment, not only repository configuration.
