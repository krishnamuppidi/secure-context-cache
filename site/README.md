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
