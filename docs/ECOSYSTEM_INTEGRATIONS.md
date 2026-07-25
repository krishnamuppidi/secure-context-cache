# Token Optimization Ecosystem Integrations

Secure Context Cache brings complementary optimization techniques into one secure pipeline without
copying their implementations or forcing heavyweight dependencies into the core package.

## Integration matrix

| Project or provider | Technique | SCC integration | Default |
| --- | --- | --- | --- |
| [LLMLingua](https://github.com/microsoft/LLMLingua) | Prompt compression | Optional post-authorization adapter with required-term checks and safe fallback | Off |
| [OpenAI prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching) | Exact prefix reuse | Stable context first, volatile task last, scoped `prompt_cache_key` | Example enabled |
| [Anthropic prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) | Explicit prefix breakpoint | Ephemeral cache breakpoint after stable SCC context | Example enabled |
| [Amazon Bedrock prompt caching](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html) | Cache checkpoints | Cache point between stable SCC context and the task | Example enabled |
| [LiteLLM](https://github.com/BerriAI/litellm) | Gateway, routing, budgets, cache | Downstream completion/routing example; SCC retains context authorization | Optional |
| [Portkey](https://github.com/Portkey-AI/gateway) | Gateway, routing, exact/semantic cache | Downstream adapter boundary with strict SCC namespaces | Optional |
| [RouteLLM](https://github.com/lm-sys/RouteLLM) | Strong/weak model routing | Downstream route decision after SCC releases context | Optional |
| [vLLM](https://github.com/vllm-project/vllm) | Prefix KV-cache reuse | OpenAI-compatible example with SCC trust-scoped cache salt | Optional |
| [LMCache](https://github.com/LMCache/LMCache) | Distributed KV-cache reuse | Self-hosted inference layer below SCC | Optional |
| [GPTCache](https://github.com/zilliztech/GPTCache) | Semantic response cache | Compatible only behind strict namespaces; not a core dependency | Off |

Licenses, APIs, model support, and provider pricing can change. Review the upstream project and
license at the version selected for deployment.

## Safety boundary

The integration order is deliberate:

```text
approved sources
  -> SCC identity + policy + relevance selection
  -> stable authorized context
  -> optional compression
  -> provider cache / model gateway / model router
  -> model
  -> provider usage + workload quality gate
```

- Never compress raw or denied sources.
- Never let a semantic cache ignore tenant, task, policy, model, or source state.
- Never use a model router to broaden context access.
- Never fall back from compressor or cache failure to unrestricted source context.
- Never count a lower token total as success when the result fails the task quality threshold.

## Why these are adapters

LLMLingua can add a large PyTorch/Transformers dependency tree. vLLM and LMCache operate at the GPU
inference layer. LiteLLM, Portkey, and RouteLLM overlap with existing enterprise model gateways.
Keeping these optional makes the SCC core small, provider-neutral, and deployable to Lambda while
allowing teams to select the tools appropriate to their environment.

See [Token Optimization Framework](TOKEN_OPTIMIZATION_FRAMEWORK.md) and the
[client examples](../examples/clients/README.md).
