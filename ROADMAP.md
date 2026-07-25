# Secure Context Cache Roadmap

The roadmap is evidence-driven. Dates are targets, not commitments.

## 0.7 - Token optimization framework

- [x] Provider-neutral token accounting and model-tokenizer extra.
- [x] Stable provider-cacheable context prefixes.
- [x] Security-scoped selection-plan reuse.
- [x] AWS compiled-context reuse by source-manifest hash.
- [x] OpenAI, Anthropic, and Bedrock prompt-caching examples.
- [x] Optional LLMLingua-2 compression adapter.
- [x] Provider usage normalization and token budgets.
- [ ] Publish a long-context labeled benchmark with quality and cost-per-accepted-result results.
- [ ] Add optional LiteLLM, Portkey, vLLM, and RouteLLM reference deployments.
- [ ] Add policy-scoped exact response caching for deterministic read-only workloads.

## 0.6 - Discoverability and integration

- Publish crawlable documentation, comparisons, benchmark guidance, and machine-readable mirrors.
- Add OpenAI, Anthropic, Amazon Bedrock, MCP, LangChain, and generic REST client patterns.
- Publish the first GitHub release and container image.
- Establish contribution, support, citation, and issue-triage workflows.

## 0.8 - Benchmark harness

- Add a provider-neutral paired-task runner.
- Preserve raw token, latency, price, quality, and authorization records.
- Export privacy-preserving JSON/CSV benchmark manifests.
- Add confidence intervals and failure-case reporting.

## 0.9 - Context ingestion and policy

- Add pluggable parsers and source adapters.
- Improve dependency-aware slicing without treating retrieval relevance as authorization.
- Add policy simulation and explainable deny decisions.
- Expand freshness, version, and approval-state controls.

## 0.10 - Production hardening

- Support per-workload identity and policy profiles by default.
- Add remote encrypted state, deletion protection, alarms, budgets, and retention examples.
- Add adversarial test suites for prompt injection, cross-context access, stale replay, and empty
  capsule fallback.
- Publish an operator upgrade and compatibility policy.

## 1.0 release criteria

- Stable capsule and audit contracts.
- Reproducible provider-measured benchmark with a published quality threshold.
- Zero unauthorized-context release in the release test suite.
- Documented migration policy and production operations evidence.
