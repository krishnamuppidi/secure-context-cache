# Changelog

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
