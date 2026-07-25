# Enterprise AI Agent Memory Security

> Shared memory becomes an attack-path oracle when every agent can query the full enterprise map. Release task-scoped views instead.

Canonical URL: https://krishnamuppidi.github.io/secure-context-cache/enterprise-ai-agent-memory-security/
Source code: https://github.com/krishnamuppidi/secure-context-cache

## The memory layer is part of the trust boundary

Persistent agent memory may contain service topology, privileged paths, owners, incident procedures, data stores, and policy exceptions. Compromise of one agent or one retrieval credential can turn that memory into a broad map of the enterprise.

Secure Context Cache separates canonical storage from task-scoped release. Slices carry sensitivity and scope; an authenticated workload requests a defined task; policy releases derived facts or citations; and the capsule expires. The model never receives source-store credentials.

- Authenticate each workload rather than trusting a self-asserted agent name.
- Bind context to task, path, environment, sensitivity, and approval.
- Redact secrets and prefer derived facts over raw source.
- Log denials and approval-required items without exposing their contents.

## Keep knowledge separate from authority

Knowing that a production role exists does not grant permission to assume it. Cloud credentials, deployment tokens, and write authority belong in a separate action-control path with their own identity, policy, and approvals.

Red-team the context layer for prompt injection in source documents, stale evidence replay, cross-tenant retrieval, path traversal, approval spoofing, and empty-capsule fallback. Fail closed when context cannot be authorized.

- Rotate workload credentials and isolate audit storage.
- Verify source hashes and freshness before release.
- Test negative cases alongside successful tasks.
- Do not treat an audit record as proof that a model conclusion is correct.

## Related resources

- [Least-Privilege Context for AI Agents](https://krishnamuppidi.github.io/secure-context-cache/least-privilege-ai-context/)
- [Secure RAG Architecture: Authorization vs. Retrieval](https://krishnamuppidi.github.io/secure-context-cache/rag-vs-secure-context-cache/)
- [SecureReviewAgent: A Governed IaC AI Security Case Study](https://krishnamuppidi.github.io/secure-context-cache/securereviewagent-case-study/)

## Evidence boundary

Prototype and fixture results are not universal production claims. A production pilot must use provider-reported usage, a labeled task set, and an agreed quality threshold.
