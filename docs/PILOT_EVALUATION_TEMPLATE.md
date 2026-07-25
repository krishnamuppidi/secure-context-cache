# Secure Context Cache Pilot Evaluation Template

Use this template for an organization-controlled evaluation. Replace every placeholder and retain
raw evidence where privacy and organizational policy permit. A completed template is evaluation
evidence, not proof of universal performance or independent adoption by itself.

## Evaluator and Scope

- Evaluator name and role:
- Organization or independent affiliation:
- Evaluation dates:
- Workload and business objective:
- Secure Context Cache version and commit:
- Deployment environment:
- Model provider and exact model version:
- Token-pricing source and effective date:
- Dataset or privacy-preserving task manifest:
- Evaluator relationship to the project:

## Predefined Acceptance Gates

- Required-fact recall threshold:
- Reviewer-acceptance threshold:
- Maximum false-positive rate:
- Prohibited-context release threshold: **0**
- Maximum latency or cost:
- Stop conditions:

Define these gates before running the comparison. Do not lower a quality or isolation threshold
after seeing the token result.

## Paired Baselines

Run the same labeled tasks with the same model settings:

1. Full approved context.
2. Retrieval-only context.
3. Secure Context Cache policy-scoped context.
4. Optional provider caching, compression, or routing variants.

Record input, cached-input, cache-write, and output tokens; latency; model cost; required-fact
recall; false positives; reviewer decision; stale-context use; and prohibited-context release.

## Results

| Metric | Full approved | Retrieval only | SCC | Acceptance gate |
| --- | ---: | ---: | ---: | ---: |
| Accepted tasks / total |  |  |  |  |
| Input tokens |  |  |  |  |
| Cached-input tokens |  |  |  |  |
| Output tokens |  |  |  |  |
| Cost per accepted result |  |  |  |  |
| Median / p95 latency |  |  |  |  |
| Required-fact recall |  |  |  |  |
| False-positive rate |  |  |  |  |
| Prohibited releases |  |  |  | 0 |

## Reproducibility and Evidence

- Raw provider usage export:
- Task manifest and expected results:
- Policy version and source-manifest hashes:
- Model and runtime configuration:
- Audit-record location:
- Reviewer records:
- Failures and exclusions:
- Reproduction instructions:

## Independent Confirmation

- Evaluator conclusion:
- Material limitations:
- Permission to name the evaluator or organization:
- Permission to quote the conclusion:
- Confirmation method and date:

Do not publish private data, credentials, customer names, or evaluator identity without explicit
permission.
