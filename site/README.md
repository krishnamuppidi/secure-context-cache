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

The homepage and five topic guides are crawlable static pages with unique titles, descriptions,
canonical URLs, Open Graph/Twitter metadata, and Schema.org JSON-LD:

- `llm-token-optimization/`
- `secure-context-caching/`
- `least-privilege-ai-context/`
- `ai-agent-context-gateway/`
- `iac-ai-security-review/`

`robots.txt` permits crawling and points to `sitemap.xml`. The sitemap lists every public page.
When a page is added or renamed, update the sitemap, homepage learning cards, related-page links,
and `tests/test_website_seo.py` together.
