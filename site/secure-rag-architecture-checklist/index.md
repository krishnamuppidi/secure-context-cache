# Secure RAG Architecture Review Checklist

> Use this implementation-neutral checklist to review whether a RAG system enforces authorization before model access and measures security with answer quality.

Canonical URL: https://krishnamuppidi.github.io/secure-context-cache/secure-rag-architecture-checklist/
Source code: https://github.com/krishnamuppidi/secure-context-cache

## Identity and isolation

Record the actor that initiated the task and the workload identity that calls retrieval and authorization services. Preserve the mapping in audit records without exposing bearer tokens or credentials to the model.

- Propagate verified end-user and workload identities.
- Enforce tenant boundaries in storage, retrieval, and authorization.
- Bind cache namespaces to identity, tenant, policy, and source state.
- Test cross-user, cross-agent, and cross-tenant access attempts.

## Authorization before prompt construction

Treat every retrieved chunk as a candidate. Evaluate identity, task, path, environment, sensitivity, freshness, approval state, and source governance before serializing any candidate into a model message.

- Run deterministic policy outside the model.
- Return denied IDs and reasons without returning denied content.
- Fail closed when the authorized candidate set is empty.
- Never let model output or prompt text override a deny decision.

## Injection, provenance, and freshness

Retrieved text is untrusted data even when the source is approved. Separate instructions from data, retain source references and hashes, and expire or invalidate context when policy or source state changes.

- Test direct and indirect prompt injection in retrieved content.
- Preserve source references, versions, hashes, and parser versions.
- Set capsule TTLs and explicit freshness thresholds.
- Keep source and index credentials outside model-visible context.

## Measure accepted results

A secure system can still be unusable, and a token-efficient system can still be insecure. Compare against the same approved baseline and count savings only when the result meets the agreed task-quality threshold.

- Capture provider-reported input, cached-input, and output usage.
- Measure must-find recall, reviewer acceptance, and false positives.
- Set a zero-tolerance threshold for prohibited-context release.
- Retain task, policy, source, model, and evaluator versions.

- [Download the one-page Secure RAG review checklist (PDF)](https://krishnamuppidi.github.io/secure-context-cache/assets/secure-rag-architecture-review-checklist.pdf)
- [Open the secure RAG architecture guide](https://krishnamuppidi.github.io/secure-context-cache/rag-vs-secure-context-cache/)

## Related resources

- [Secure RAG Architecture: Authorization vs. Retrieval](https://krishnamuppidi.github.io/secure-context-cache/rag-vs-secure-context-cache/)
- [Secure Context Cache Benchmark and Evaluation Method](https://krishnamuppidi.github.io/secure-context-cache/secure-context-cache-benchmark/)
- [Secure Context Cache Documentation](https://krishnamuppidi.github.io/secure-context-cache/docs/)

## Evidence boundary

Prototype and fixture results are not universal production claims. A production pilot must use provider-reported usage, a labeled task set, and an agreed quality threshold.
