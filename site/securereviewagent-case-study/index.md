# SecureReviewAgent: A Governed IaC AI Security Case Study

> Infrastructure review is a useful first benchmark because required facts, prohibited context, findings, and reviewer acceptance can be labeled.

Canonical URL: https://krishnamuppidi.github.io/secure-context-cache/securereviewagent-case-study/
Source code: https://github.com/krishnamuppidi/secure-context-cache

## Why IaC review needs more than a diff

A Terraform change may depend on IAM relationships, network boundaries, environment, ownership, data classification, deployment controls, and prior exceptions. Sending the entire enterprise map is expensive and creates unnecessary exposure; sending only the changed file can miss required dependencies.

SecureReviewAgent requests a capsule for the changed path and task. Agent Context Gateway authenticates the workload, selects approved facts, denies unrelated slices, and returns provenance and an audit ID. The model reviews the change using that capsule.

- Changed resources and local dependencies.
- Relevant IAM, network, policy, ownership, and environment facts.
- Denied unrelated topology and secret-adjacent material.
- Review findings tied to sources and a capsule audit record.

## Make the review measurable

Create pull requests with labeled must-find issues and benign controls. Compare changed-files-only, full approved context, retrieval-only, and policy-scoped capsule paths. Record provider usage, security issue recall, false positives, reviewer acceptance, and prohibited-context release.

The current public fixture validates the boundary and artifacts but does not establish a production savings percentage or equal review quality. The next evidence milestone is a provider-measured, human-reviewed replay set.

- Fail closed when no context is approved.
- Keep deployment authority outside the review model.
- Require human approval for high-risk actions.
- Use the case study to improve policy and context coverage.

## Related resources

- [AI-Assisted Infrastructure-as-Code Security Review](https://krishnamuppidi.github.io/secure-context-cache/iac-ai-security-review/)
- [Secure Context Cache Benchmark and Evaluation Method](https://krishnamuppidi.github.io/secure-context-cache/secure-context-cache-benchmark/)
- [Enterprise AI Agent Memory Security](https://krishnamuppidi.github.io/secure-context-cache/enterprise-ai-agent-memory-security/)

## Evidence boundary

Prototype and fixture results are not universal production claims. A production pilot must use provider-reported usage, a labeled task set, and an agreed quality threshold.
