# MCP Context Optimization with Policy-Scoped Capsules

> Expose one authenticated capsule tool through MCP so the host can request approved facts without receiving broad source credentials.

Canonical URL: https://krishnamuppidi.github.io/secure-context-cache/mcp-context-optimization/
Source code: https://github.com/krishnamuppidi/secure-context-cache

## Put policy behind the MCP tool

MCP makes tools and resources available to AI hosts, but tool availability is not the same as authorization to every enterprise fact. A broad repository resource can still create excessive token use and cross-context exposure.

A Secure Context Cache MCP server accepts a task type, path, environment, and prompt; authenticates to Agent Context Gateway outside the model; and returns only the capsule facts, references, expiry, and audit ID. Secrets remain in the server process or host credential store.

- Expose a narrow request_capsule tool instead of a raw source browser.
- Validate task and path inputs before calling the gateway.
- Return denials as metadata without revealing denied content.
- Do not expose bearer tokens, API keys, or cloud credentials in tool results.

```text
result = request_capsule(
    task_type="iac_security",
    path="terraform/prod/payments/lambda.tf",
    environment="prod",
)
return {"facts": result["facts"], "audit_id": result["audit_id"]}
```

## Evaluate MCP context as a security boundary

Measure tokens and quality with and without the capsule tool, but also test unauthorized paths, malformed arguments, prompt injection, stale sources, and repeated calls. The MCP host should not convert a denied capsule into a broader fallback.

Use one workload identity per host or agent in production, short token lifetimes, rate limits, and audit correlation between the MCP invocation and the gateway decision.

## Related resources

- [Secure Context Cache Documentation](https://krishnamuppidi.github.io/secure-context-cache/docs/)
- [Enterprise AI Agent Memory Security](https://krishnamuppidi.github.io/secure-context-cache/enterprise-ai-agent-memory-security/)
- [AI Agent Context Gateway](https://krishnamuppidi.github.io/secure-context-cache/ai-agent-context-gateway/)

## Evidence boundary

Prototype and fixture results are not universal production claims. A production pilot must use provider-reported usage, a labeled task set, and an agreed quality threshold.
