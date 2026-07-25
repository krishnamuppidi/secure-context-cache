# Amazon Bedrock Token Optimization with Secure Context Cache

> Request an approved capsule before Bedrock Converse, keep AWS credentials outside prompts, and evaluate provider usage with the same quality gate.

Canonical URL: https://krishnamuppidi.github.io/secure-context-cache/aws-bedrock-token-optimization/
Source code: https://github.com/krishnamuppidi/secure-context-cache

## Separate AWS authority from model context

A Bedrock client can obtain an Agent Context Gateway capsule using its workload identity, then pass the released facts to the selected model. The model does not receive AWS credentials, Cognito secrets, gateway bearer tokens, or direct S3 access.

Secure Context Cache reduces and governs enterprise context. Bedrock model selection, inference profiles, provider caching features, quotas, and pricing remain separate controls. The repository's Converse example demonstrates the intended boundary.

- Use IAM roles or short-lived workload credentials.
- Store approved source material in a separately governed location.
- Attach audit IDs and source references to review records.
- Use CloudWatch and provider usage fields for production measurement.

## Benchmark cost and quality together

Compare a full approved baseline with the capsule path across the same tasks and model configuration. Record input and output usage, latency, price assumptions, required-fact recall, false positives, and unauthorized release.

If a capsule saves tokens but misses a dependency or control, expand the graph or selection policy. Do not weaken the acceptance threshold to preserve a savings percentage.

- Version model identifiers, policy, source hashes, and task sets.
- Separate on-demand, cached, and provisioned cost assumptions.
- Retain raw provider usage for reproducibility.
- Label prototype, pilot, and production evidence accurately.

## Related resources

- [Secure Context Cache Documentation](https://krishnamuppidi.github.io/secure-context-cache/docs/)
- [Prompt Caching vs. Context Caching for AI Agents](https://krishnamuppidi.github.io/secure-context-cache/prompt-caching-vs-context-caching/)
- [Secure Context Cache Benchmark and Evaluation Method](https://krishnamuppidi.github.io/secure-context-cache/secure-context-cache-benchmark/)

## Evidence boundary

Prototype and fixture results are not universal production claims. A production pilot must use provider-reported usage, a labeled task set, and an agreed quality threshold.
