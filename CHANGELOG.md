# Changelog

## 0.7.1 - 2026-07-25

- Added `/v1/authorize-retrieval` to authorize RAG candidates before their content crosses the
  model boundary.
- Added fail-closed empty-result behavior, duplicate candidate rejection, and response shaping
  that never echoes denied candidate content.
- Added a secure RAG architecture comparison, concrete API example, independent security
  references, and a downloadable review checklist.
- Added external pilot and impact-evidence templates so adoption can be evaluated with tokens,
  quality, isolation, and independent confirmation rather than raw traffic alone.

## 0.7.0 - 2026-07-25

- Repositioned Secure Context Cache as a complete token-optimization framework while preserving
  the product name, secure-context architecture, `acg` CLI, and capsule API.
- Added the Measure → Select → Reuse → Compress → Route → Verify framework and `/v1/optimize`.
- Added dependency-free and optional model-tokenizer accounting, token budgets, and
  provider-usage normalization for OpenAI, Anthropic, and Amazon Bedrock.
- Added stable provider-cacheable context, scoped cache namespaces, and native provider caching
  patterns in the client examples.
- Corrected selection-plan keys so request IDs do not defeat reuse and bound cache entries to
  identity, task, policy, context, and source state.
- Added S3 manifest fingerprints and DynamoDB compiled-slice reuse for unchanged AWS contexts.
- Added an optional LLMLingua-2 post-authorization compressor with protected-term checks and safe
  fallback.
- Expanded tests for optimization plans, token budgets, source invalidation, stable prefixes, and
  provider usage.

## 0.6.0 - 2026-07-25

- Added 13 crawlable documentation, comparison, integration, benchmark, case-study, research, and
  project-identity pages with Markdown mirrors.
- Added `llms.txt`, `llms-full.txt`, explicit search/AI crawler policy, RSS, expanded sitemaps, and
  automated IndexNow notification data.
- Added reusable social-preview and animated architecture assets.
- Added OpenAI, Anthropic, LangChain, MCP, and generic REST client examples alongside Bedrock.
- Added citation, contribution, conduct, support, roadmap, issue, pull-request, and release assets.
- Added a tag-triggered GitHub Container Registry workflow.

## 0.5.0 - 2026-07-24

- Renamed the public product and repository to Secure Context Cache.
- Made secure token optimization the primary value proposition.
- Preserved Agent Context Gateway as the stable API and runtime control plane.
- Connected SecureReviewAgent as the flagship measurable token-optimization workflow.
- Updated website, clone, package, container, documentation, and deployment references.

## 0.4.0 - 2026-07-24

- Unified the product family under the Secure Context Cache Framework.
- Positioned Agent Context Gateway AI as the deployable API and AWS control plane.
- Positioned SecureReviewAgent as the flagship Infrastructure-as-Code security application.
- Added the research-to-product architecture, accepted-paper status, prototype-result guardrails,
  and consistent website messaging.

## 0.3.0 - 2026-07-22

- Added complete onboarding, architecture, API, policy, context-source, AWS IAM, Kubernetes,
  operations, troubleshooting, production-readiness, and agent-integration documentation.
- Added dependency-free Python and TypeScript clients plus an Amazon Bedrock Converse example.
- Added environment-configurable local API identity instead of requiring built-in demo credentials.
- Added custom AWS policy, allowed-task, and maximum-sensitivity deployment inputs.
- Limited AWS context synchronization to supported source types and common generated-directory
  exclusions.
- Hardened the Kubernetes evaluation manifest with Secret-based API key injection, policy mounting,
  probes, resources, and container security settings.
- Added regression coverage for API trace fields, local identity configuration, and client examples.

## 0.2.0 - 2026-07-21

- Added the end-to-end AWS evaluation deployment with API Gateway, Cognito, Lambda, encrypted S3,
  encrypted DynamoDB tables, KMS, CloudWatch Logs, context upload, and authenticated smoke testing.

## 0.1.0 - 2026-07-17

- Published the initial clean open-source Agent Context Gateway AI implementation.
