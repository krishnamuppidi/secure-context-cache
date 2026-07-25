# Secure Context Cache - Agent Context Gateway Architecture

Secure Context Cache defines a complete token-optimization framework: measure, select, reuse,
optionally compress, route, and verify. Its original canonical graph, protected reusable slices,
and task-scoped capsules provide the secure-context add-on that differentiates it from generic
compression and model-routing tools. Agent Context Gateway is the deployable API and policy
boundary. SecureReviewAgent is the flagship application.

The gateway is not a vector database, secret manager, or authorization system for cloud actions.
It interoperates with model routers rather than duplicating them.

## Core Flow

```text
approved source files
    |
    v
scanner -> Secure Context Cache graph -> protected slices -> identity + task policy
                                                       |            |
                                                       +-----+------+
                                                             v
                                                task-scoped capsule
                                                             |
                                              +--------------+-------------+
                                              v                            v
                                    SecureReviewAgent or              audit + metrics
                                      another AI agent
```

1. The scanner reads supported files and records path, hash, inferred environment, inferred
   sensitivity, parser version, and freshness time.
2. The slicer produces one policy unit per supported file.
3. Identity limits task types and maximum sensitivity.
4. Task policy checks task type, path relevance, sensitivity, freshness, and approval requirements.
5. The capsule contains derived facts, source references, provenance, TTL, denials, and a hash.
6. The caller decides whether and how to pass released facts to a model.

## Local Runtime

```text
client -> FastAPI -> local directory scan -> in-memory cache -> capsule response
                       |
                       +-> no durable server-side audit store
```

The local API is for development. It uses an API key and a configured allowed repository root. The
cache is process-local; restarting the process clears it. Audit data is returned in the capsule but
is not persisted by the server. The offline CLI writes an audit JSON file.

## AWS Evaluation Runtime

```text
deployer -> supported source files -> private KMS-encrypted S3 prefix

agent -> Cognito client credentials -> API Gateway JWT authorizer -> Lambda
                                                               |
                                      +------------------------+----------------------+
                                      v                        v                      v
                                S3 context source       DynamoDB slices/cache   DynamoDB audit
```

- API Gateway rejects unauthenticated capsule and insight requests.
- Cognito supplies a verified machine-client identity.
- Lambda uses an IAM execution role; deployer access keys are not copied into the runtime.
- S3 stores uploaded source files by validated context ID.
- DynamoDB stores derived slices, selection-cache telemetry, and audit records.
- KMS encrypts S3 and DynamoDB data; S3 public access is blocked and versioning is enabled.

The health endpoint is intentionally unauthenticated and reveals only status and runtime mode.

## Data Objects

### Context graph

A graph contains repository and file nodes plus `contains` edges. File nodes include source hashes,
environment, sensitivity, parser version, and freshness metadata.

### Context slice

A slice is the atomic policy unit. It contains derived facts, references, sensitivity, environment,
token estimate, source hash, freshness, redaction notes, and optional task-profile controls.

### Context capsule

A capsule is a request-scoped release. It contains released facts, denied slices and reasons,
source manifest, policy version, expiry time, cache status, audit ID, and capsule hash.

### Metrics

Metrics compare the estimated tokens in all generated slices with the estimated tokens in released
slices. They are framework estimates, not a cloud-provider bill and not measured model input usage.

## Optimization and Cache Semantics

AWS fingerprints the S3 object manifest. An unchanged fingerprint loads compiled slices from
DynamoDB, avoiding repeat object downloads and parsing. A selection-plan cache binds context,
authorization scope, task, path, environment, approval state, policy version, and source manifest.
Cached released slices are re-authorized on every request.

The stable model context contains only reusable source-backed facts and instructions. Volatile
request, expiry, and audit metadata stay outside that prefix, enabling provider prompt caching.
Optional compression runs only after authorization and is not installed in the core Lambda package.

## Trust Boundaries

- The model is untrusted and never receives credentials or authority from the gateway.
- The caller is responsible for keeping OAuth tokens, client secrets, and API keys outside prompts.
- The deployer is trusted to curate source files before upload.
- Sensitivity classification is heuristic in the current scanner and must not replace data
  classification or DLP.
- A source reference is provenance, not proof that a model conclusion is correct.
- An audit record proves what the gateway released or denied; it does not prove the model followed
  instructions.

## Current Limits

- Supported parsing is file-level and deterministic; there is no semantic chunking or vector search.
- Facts describe file scope, environment, sensitivity, and operational relevance; raw source content
  is not returned.
- The AWS runtime still lists the selected S3 prefix to compute an object-manifest fingerprint.
- API Gateway and Lambda constrain long-running requests; large repositories need preprocessing or
  a future asynchronous ingestion path.
- The current Terraform stack creates one shared evaluation Cognito client.
- Production approval-service integration, immutable audit export, WAF, alarms, budgets, remote
  Terraform state, backup automation, and disaster recovery are operator responsibilities.

See [Production Readiness](PRODUCTION_READINESS.md) for the promotion checklist.
