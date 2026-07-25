# Contributing to Secure Context Cache

Contributions are welcome when they preserve the project's central boundary: models receive only
policy-approved context, never source-store credentials or action authority.

## Start with an issue

Use GitHub Discussions for design questions and an issue for a reproducible bug or bounded feature.
Security vulnerabilities belong in the private process described in [SECURITY.md](SECURITY.md).

Good first contributions include:

- a new model-provider client that requests a capsule before model invocation;
- a parser fixture with sensitivity and freshness tests;
- documentation corrections or machine-readable examples;
- negative authorization and empty-capsule tests; and
- benchmark tooling that preserves provider usage and quality evidence.

## Development setup

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev,api]"
pytest -q
python -m compileall src tests examples
ruff check src tests examples
```

When website content changes, rebuild and verify the static discovery assets:

```bash
python scripts/build_discoverability_assets.py
pytest -q tests/test_website_seo.py
```

## Pull-request expectations

- Explain the problem and the authorization boundary affected.
- Add or update tests before changing behavior.
- Keep prototype, pilot, and production claims clearly labeled.
- Do not include credentials, company-confidential sources, or generated deployment secrets.
- Preserve stable `acg` commands, environment variables, and public API fields unless a migration
  path is documented.
- Update documentation, examples, and the changelog when behavior changes.

By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).
