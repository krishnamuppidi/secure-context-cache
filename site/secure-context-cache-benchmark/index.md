# Secure Context Cache Benchmark and Evaluation Method

> The public fixture proves the release and measurement path. It does not prove universal production savings; a production pilot must join provider usage with accepted-result quality.

Canonical URL: https://krishnamuppidi.github.io/secure-context-cache/secure-context-cache-benchmark/
Source code: https://github.com/krishnamuppidi/secure-context-cache

## What the public fixture demonstrates

The local sample repository produces two file-level context slices. For an Infrastructure-as-Code security task, one slice is released and one unrelated slice is denied. Derived facts across both slices total a deterministic estimate of 32 whitespace-separated words; the capsule contains 16, producing a displayed 50% reduction.

The field names use tokens, but the fixture estimator is a word-count proxy. It is not a provider tokenizer, invoice measurement, or production-quality benchmark. Its purpose is to make the selection, denial, capsule, audit, and metrics artifacts reproducible.

- One released slice and one denied slice.
- Source hash, freshness, policy version, expiry, and audit ID.
- Deterministic 32-to-16 estimate for the included fixture.
- No claim of 50% production cost or quality-equivalent savings.

```text
acg demo --repo examples/sample_repo --out build/demo
python -m json.tool build/demo/context-capsule.json
python -m json.tool build/demo/audit-record.json
python -m json.tool build/demo/metrics.json
```

## Design the production benchmark

Use a labeled task set and compare changed-files-only, full approved context, relevance-only retrieval, and policy-scoped capsules. Hold model and settings constant. Capture raw provider usage, pricing timestamp, latency, must-find recall, false positives, reviewer agreement, overrides, stale-context rate, and prohibited-context release.

The separate 24-task deterministic research prototype reported a 75.3% average context-size reduction, 95.8% task success, and 98.6% required-fact coverage. These are prototype measurements, not independent field evidence. Production claims should be based on provider and reviewer records from an organization-controlled pilot.

- Publish task and dataset versions or a privacy-preserving manifest.
- Store raw JSON/CSV results and the exact evaluation commit.
- Predefine acceptance and zero-unauthorized-release thresholds.
- Report failures and confidence intervals, not only averages.

## Related resources

- [How to Reduce LLM Token Cost Without Losing Answer Quality](https://krishnamuppidi.github.io/secure-context-cache/reduce-llm-token-cost/)
- [SecureReviewAgent: A Governed IaC AI Security Case Study](https://krishnamuppidi.github.io/secure-context-cache/securereviewagent-case-study/)
- [Secure Context Cache Documentation](https://krishnamuppidi.github.io/secure-context-cache/docs/)

## Evidence boundary

Prototype and fixture results are not universal production claims. A production pilot must use provider-reported usage, a labeled task set, and an agreed quality threshold.
