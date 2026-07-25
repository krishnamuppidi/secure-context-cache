# Secure Context Cache Documentation

> Start with the architecture, run the local demo, integrate an agent, and evaluate secure token optimization with explicit quality and authorization gates.

Canonical URL: https://krishnamuppidi.github.io/secure-context-cache/docs/
Source code: https://github.com/krishnamuppidi/secure-context-cache

## Choose the shortest path to a working capsule

Secure Context Cache compiles approved repository, policy, runbook, and service facts into reusable slices. Agent Context Gateway authenticates a workload, applies task and sensitivity policy, and returns a short-lived capsule containing only the facts allowed for that request.

New evaluators should run the deterministic local fixture before deploying infrastructure. The fixture makes the release and denial boundary visible without requiring a cloud account or model-provider credential.

- Run the local quick start and inspect the capsule, audit record, and metrics JSON.
- Read the architecture and policy guides before uploading organization-owned material.
- Use one client example to place the capsule before the model invocation.
- Compare the optimized path with a generous approved baseline using the same tasks and quality rubric.

```text
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
acg demo --repo examples/sample_repo --out build/demo
pytest -q
```

## Documentation map

The repository remains the source of truth for exact commands, APIs, environment variables, and security limitations. This website provides crawlable explanations and routes agents and engineers to the canonical files.

Production adoption requires organization-specific source governance, identity, policy review, monitoring, retention, adversarial testing, and an acceptance threshold for answer quality.

- Getting Started, API Reference, Architecture, and Agent Integration
- Policy Guide, Context Sources, Security, and Production Readiness
- AWS, Kubernetes, operations, troubleshooting, and deployer IAM
- Benchmark method, comparisons, provider integration patterns, and SecureReviewAgent case study

## Related resources

- [Secure Context Cache Benchmark and Evaluation Method](https://krishnamuppidi.github.io/secure-context-cache/secure-context-cache-benchmark/)
- [AI Context Engineering for Reliable Enterprise Agents](https://krishnamuppidi.github.io/secure-context-cache/ai-context-engineering/)
- [SecureReviewAgent: A Governed IaC AI Security Case Study](https://krishnamuppidi.github.io/secure-context-cache/securereviewagent-case-study/)

## Evidence boundary

Prototype and fixture results are not universal production claims. A production pilot must use provider-reported usage, a labeled task set, and an agreed quality threshold.
