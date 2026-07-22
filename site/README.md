# Agent Context Gateway website

This directory contains the dependency-free product website for Agent Context Gateway.

## Preview locally

```bash
python -m http.server 4173 --directory site
```

Open `http://127.0.0.1:4173`.

## Publishing

The `deploy-website.yml` GitHub Actions workflow publishes this directory to GitHub Pages after
changes to `site/**` reach `main`. The site uses only relative asset paths, so it works from the
repository's Pages subpath.

The product metrics shown on the page are explicitly labeled as reproducible fixture evidence or
illustrative arithmetic. Do not convert them into universal production-savings claims.
