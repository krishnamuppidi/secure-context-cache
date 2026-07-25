# Prompt Caching vs. Context Caching for AI Agents

> Prompt caching discounts repeated provider input; context caching decides which enterprise facts should be assembled and authorized before that input is sent.

Canonical URL: https://krishnamuppidi.github.io/secure-context-cache/prompt-caching-vs-context-caching/
Source code: https://github.com/krishnamuppidi/secure-context-cache

## The two caches solve different problems

Provider prompt caching can reduce the price or processing overhead of repeated input prefixes. It is valuable when a stable prompt segment is sent repeatedly to the same provider under compatible cache rules.

Secure context caching operates earlier. It ingests approved sources, normalizes facts, tracks versions and sensitivity, and assembles a task-scoped capsule. It can reduce the input that reaches any model while preserving the reason each fact was released.

- Prompt caching optimizes repeated provider input.
- Context caching optimizes enterprise knowledge preparation and selection.
- Prompt caching does not by itself authorize sensitive context.
- Context caching does not replace provider cache accounting.

## Use both when the workload supports both

A strong design can build a small policy-approved capsule, place stable instructions and schemas in a provider-cacheable prefix, and keep volatile task facts outside that prefix. Each context release still needs a current authorization decision even when the underlying slice was previously cached.

Measure provider cache reads and writes separately from capsule reduction. Also record freshness, source hashes, policy version, quality, and denied context so a lower bill cannot hide a broader exposure or stale answer.

- Invalidate or version source-backed slices when approved sources change.
- Reevaluate authorization for every task and identity.
- Keep credentials and action authority outside both caches.
- Fail closed when no approved context is available.

## Related resources

- [Secure Context Caching for Enterprise AI Agents](https://krishnamuppidi.github.io/secure-context-cache/secure-context-caching/)
- [OpenAI Token Optimization with Secure Context Capsules](https://krishnamuppidi.github.io/secure-context-cache/openai-token-optimization/)
- [Amazon Bedrock Token Optimization with Secure Context Cache](https://krishnamuppidi.github.io/secure-context-cache/aws-bedrock-token-optimization/)

## Evidence boundary

Prototype and fixture results are not universal production claims. A production pilot must use provider-reported usage, a labeled task set, and an agreed quality threshold.
