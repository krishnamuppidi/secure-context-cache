# Secure RAG Architecture: Authorization vs. Retrieval

> Secure RAG treats retrieved chunks as candidates, then applies deterministic authorization before any candidate content crosses the model boundary.

Canonical URL: https://krishnamuppidi.github.io/secure-context-cache/rag-vs-secure-context-cache/
Source code: https://github.com/krishnamuppidi/secure-context-cache

## What is secure RAG?

Secure RAG is a retrieval-augmented generation architecture in which retrieved content is only a candidate set. A deterministic authorization layer evaluates the requesting identity, task, resource path, environment, sensitivity, freshness, source approval, and policy before releasing content to the model.

Semantic similarity answers whether a chunk may be relevant. It does not prove that an agent may see a document, tenant, incident, production environment, or secret-adjacent runbook. Secure Context Cache adds that missing release decision while retaining provenance and token measurements.

- Retrieval supplies candidates; it does not grant access.
- Authorization runs outside the model and before prompt construction.
- Denied content stays out of model-visible context and response payloads.
- Fail-closed behavior prevents unrestricted fallback from an empty authorized result.

## Traditional RAG, secure RAG, and SCC

Secure RAG strengthens retrieval with an authorization layer. Secure Context Cache implements that boundary and also provides token measurement, compiled-context reuse, provider-cacheable prefixes, optional compression, routing adapters, expiring capsules, and audit evidence.

| Capability | Traditional RAG | Secure RAG | Secure Context Cache |
| --- | --- | --- | --- |
| Semantic retrieval | Yes | Yes | Optional input stage |
| User or agent identity | Sometimes | Required | Required |
| Task authorization | Rare | Yes | Built in |
| Path and environment policy | Rare | Possible | Built in |
| Sensitivity enforcement | Metadata dependent | Required | Policy evaluated |
| Denied-item audit | Rare | Recommended | Built in |
| Expiring model context | Rare | Possible | Capsule TTL |
| Token optimization | Incidental | Possible | Primary measurement |
| Provenance and hashes | Varies | Recommended | Preserved |

## Authorize candidates with one API call

The application performs retrieval, then sends candidate content and security metadata to `/v1/authorize-retrieval`. The response returns an approved capsule plus candidate IDs and reasons for denials. Denied content is never echoed.

If no candidate passes, `fail_closed` is true, the stable context is empty, and unrestricted fallback is explicitly prohibited. The caller must stop or use a separately authorized recovery path.

```text
POST /v1/authorize-retrieval
{
  "task_type": "iac_security",
  "path": "terraform/prod/payments/lambda.tf",
  "environment": "prod",
  "candidates": [
    {"candidate_id": "rag-1", "content": "KMS control...", "refs": ["terraform/prod/payments/lambda.tf"], "sensitivity": "high"},
    {"candidate_id": "rag-2", "content": "Incident detail...", "refs": ["incidents/restricted.md"], "sensitivity": "restricted"}
  ]
}

retrieval.authorized_candidate_ids = ["rag-1"]
retrieval.denied_candidates = [{"candidate_id": "rag-2", "sensitivity": "restricted", "reason": "..."}]
retrieval.unrestricted_fallback_allowed = false
```

## When to use each architecture

Use traditional RAG for public or uniformly authorized corpora where relevance is the main risk. Add secure RAG when users, agents, tenants, tasks, paths, or environments have different access boundaries. Use Secure Context Cache when the workload also needs measurable token optimization, reusable compiled context, provenance, expiry, and release audits.

Keep action authorization separate from context authorization. Even an authorized fact does not grant permission to execute a tool, modify infrastructure, or access another system.

- Public knowledge base: relevance-first RAG may be enough.
- Enterprise multi-tenant assistant: secure RAG is the minimum boundary.
- Repeated governed agent workflow: SCC adds reusable token optimization.
- High-risk actions: require a separate action-policy decision.

## Independent security guidance

The design aligns with independent guidance that treats authorization, tenant isolation, prompt injection, and agent identity as separate controls. These sources support the architecture; they do not endorse Secure Context Cache.

- [AWS Security: authorization mechanisms for data used in generative AI](https://aws.amazon.com/blogs/security/implement-effective-data-authorization-mechanisms-to-secure-your-data-used-in-generative-ai-applications/)
- [AWS Architecture: secure multi-tenant RAG with Verified Permissions](https://aws.amazon.com/blogs/architecture/secure-multi-tenant-rag-with-amazon-bedrock-and-verified-permissions/)
- [OWASP GenAI: prompt injection risk](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)
- [NIST NCCoE: software and AI agent identity and authorization concept paper](https://www.nccoe.nist.gov/sites/default/files/2026-02/accelerating-the-adoption-of-software-and-ai-agent-identity-and-authorization-concept-paper.pdf)

## Related resources

- [Secure RAG Architecture Review Checklist](https://krishnamuppidi.github.io/secure-context-cache/secure-rag-architecture-checklist/)
- [Least-Privilege Context for AI Agents](https://krishnamuppidi.github.io/secure-context-cache/least-privilege-ai-context/)
- [Enterprise AI Agent Memory Security](https://krishnamuppidi.github.io/secure-context-cache/enterprise-ai-agent-memory-security/)

## Evidence boundary

Prototype and fixture results are not universal production claims. A production pilot must use provider-reported usage, a labeled task set, and an agreed quality threshold.
