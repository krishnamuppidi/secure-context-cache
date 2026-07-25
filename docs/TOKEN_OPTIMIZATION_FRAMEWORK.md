# Secure Context Cache Token Optimization Framework

Secure Context Cache (SCC) is an open-source framework for reducing the tokens, latency, cost, and
unnecessary data exposure of AI workloads. The name remains Secure Context Cache because secure,
reusable context is its original architecture and its differentiator. Token optimization is the
primary product surface.

SCC combines complementary techniques behind one measurable pipeline:

```text
Measure -> Select -> Reuse -> Compress (optional) -> Route (optional) -> Verify
              \______________________________________________/
                    identity, policy, provenance, audit
```

## Optimization levers

### 1. Measure

- Dependency-free deterministic word proxy for fixtures and offline reproducibility.
- Optional `tiktoken` counters for OpenAI-compatible estimates.
- Normalizers for provider-reported OpenAI, Anthropic, and Amazon Bedrock usage.
- Explicit measurement-source labels so estimates are not presented as provider invoices.
- Token-budget status on every optimization response.

Install tokenizer support:

```bash
pip install "secure-context-cache[tokenizers]"
```

### 2. Select

SCC compiles approved sources into source-backed slices and applies identity, task, path,
environment, sensitivity, freshness, and approval policy before model invocation. Only released
facts enter the stable model context. Denied data never becomes compressor input.

### 3. Reuse

SCC uses two independent reuse layers:

- **Compiled-context reuse:** AWS fingerprints the S3 object manifest and loads unchanged compiled
  slices from DynamoDB instead of downloading and parsing every object again.
- **Selection-plan reuse:** a key binds context ID, agent authorization scope, task type, path,
  environment, approval state, policy version, and source manifest. `request_id` is intentionally
  excluded because it is audit correlation, not task semantics.

Cached slices are re-authorized on every request. A cache hit cannot bypass the current policy.

The model-visible context excludes volatile request IDs, expiry timestamps, and audit IDs. Stable
facts therefore form an exact provider-cacheable prefix; request-specific task text follows it.

### 4. Compress, optionally

Install the optional LLMLingua-2 adapter only for workloads with long authorized capsules:

```bash
pip install "secure-context-cache[compression]"
```

Compression is deliberately not a core dependency. It is skipped below the configured threshold,
runs only after authorization, can force preservation of security-critical terms, and returns the
original authorized capsule if a required term disappears. A workload quality gate is still
required because lexical preservation does not prove task correctness.

### 5. Route, optionally

SCC remains model- and gateway-neutral. Use LiteLLM, Portkey, RouteLLM, or an internal gateway after
SCC. Model routing can reduce cost, but it must not broaden the context authorization boundary.

Semantic response caching is disabled by default. If enabled downstream, namespace it at minimum
by tenant, agent, task, policy version, source-manifest or capsule-content hash, model, parameters,
and TTL. Exact response caching should be limited to deterministic read-only tasks.

### 6. Verify

Token reduction is not success by itself. Compare the optimized path with an approved baseline and
record:

- provider-reported input, cached-input, cache-write, and output tokens;
- latency and timestamped pricing assumptions;
- task-specific recall, precision, reviewer acceptance, and overrides;
- stale-context use and prohibited-context release; and
- cost per accepted, correct, policy-compliant result.

## Local optimization command

```bash
acg optimize \
  --repo examples/sample_repo \
  --task-type iac_security \
  --path terraform/prod/payments/lambda.tf \
  --prompt "Review security and blast-radius risk" \
  --provider openai \
  --model gpt-5 \
  --tokenizer tiktoken:o200k_base \
  --token-budget 100 \
  --out build/optimization.json
```

Use `--tokenizer word` without optional dependencies. With tokenizer support installed, use
`--tokenizer tiktoken` or `--tokenizer tiktoken:o200k_base`.

## API

`POST /v1/optimize` is the primary optimization endpoint. `POST /v1/capsules` remains backward
compatible and returns the same optimization plan.

```json
{
  "context_id": "payments-platform",
  "task_type": "iac_security",
  "path": "terraform/prod/payments/lambda.tf",
  "prompt": "Review security and blast-radius risk",
  "environment": "prod",
  "provider": "openai",
  "model": "gpt-5",
  "tokenizer": "word",
  "token_budget": 800
}
```

The response includes the governed capsule, measured metrics, stable context, a prefix hash, a
security-scoped provider cache namespace, and the status of each optimization lever.

## What SCC integrates and what remains original

SCC interoperates with prompt compression, provider prefix caching, model gateways, model routers,
and inference KV caches. It does not copy their implementations or claim that one technique solves
the entire problem.

SCC's distinct contribution is the combination of source-backed reusable context, deterministic
authorization before model invocation, token-budgeted short-lived capsules, explicit denial
reasons, provenance hashes, audit evidence, and cross-agent reuse without unrestricted shared
memory.

See [Architecture](ARCHITECTURE.md), [Agent Integration](AGENT_INTEGRATION.md), and
[Production Readiness](PRODUCTION_READINESS.md).
