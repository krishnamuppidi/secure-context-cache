# Secure Context Cache website

This directory contains the dependency-free product website for Secure Context Cache, its
deployable Agent Context Gateway control plane, and its flagship SecureReviewAgent
application.

## Preview locally

```bash
python -m http.server 4173 --directory site
```

Open `http://127.0.0.1:4173`.

## Publishing

The `deploy-website.yml` GitHub Actions workflow publishes this directory to GitHub Pages after
changes to `site/**` reach `main`. The site uses only relative asset paths, so it works from the
repository's Pages subpath.

The commercial message leads with secure token optimization: reduce repeated input tokens by
assembling the smallest policy-approved capsule that preserves required facts. SecureReviewAgent is
the first practical benchmark. Agent Context Gateway is the deployable API and AWS control plane.

The 32-to-16-token result is explicitly labeled as a deterministic fixture estimate. The calculator
is illustrative arithmetic. Do not convert either into a provider-billed production benchmark or a
universal savings claim. Company pilots should use provider-reported usage and count savings only
when the optimized run meets an agreed quality threshold.

## Website analytics

The site uses the public GA4 measurement ID `G-9C5B48SR3B`. Analytics is optional and remains
disabled until a visitor allows it. The site does not send names, email addresses, form contents,
query strings, or full outbound URLs. Advertising storage, advertising personalization, and Google
Signals are disabled.

Meaningful aggregate events include GitHub resource clicks, pilot-email clicks, token-calculator
use, developer-example tabs, and code-example copies. Treat these as website awareness or
evaluation signals, not verified product adoption.

## Search visibility

The homepage, technical guides, documentation, comparisons, integrations, benchmark, case study,
research page, and project-identity page are crawlable static pages with unique titles,
descriptions, canonical URLs, social metadata, and Schema.org JSON-LD.

- `llm-token-optimization/`
- `secure-context-caching/`
- `least-privilege-ai-context/`
- `ai-agent-context-gateway/`
- `iac-ai-security-review/`
- `docs/`
- `reduce-llm-token-cost/`
- `prompt-caching-vs-context-caching/`
- `rag-vs-secure-context-cache/`
- `ai-context-engineering/`
- `enterprise-ai-agent-memory-security/`
- `mcp-context-optimization/`
- `openai-token-optimization/`
- `aws-bedrock-token-optimization/`
- `secure-context-cache-benchmark/`
- `securereviewagent-case-study/`
- `about/`
- `research/secure-context-cache-paper/`

`robots.txt` explicitly permits major search and answer-engine crawlers and points to XML and text
sitemaps. `llms.txt` is the concise machine-readable index; `llms-full.txt` consolidates public
technical explanations; `feed.xml` advertises updates; and `indexnow-urls.json` supports
post-deployment IndexNow notifications.

Generated discovery pages and machine-readable assets come from
`scripts/build_discoverability_assets.py`. When its page catalog changes, run the script and update
the homepage learning cards when a new resource should be featured.
