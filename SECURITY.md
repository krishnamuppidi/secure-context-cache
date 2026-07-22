# Security Model

Agent Context Gateway is designed around deny-by-default context release.

## Trust Boundaries

- The model is not trusted with authority.
- The gateway is responsible for selecting and releasing context.
- Policy decides which slices can be released to an agent for a task.
- Audit records capture every release and denial.
- Production deployments should replace demo credentials with enterprise identity.

## Public AWS Deployment

The automated AWS path uses API Gateway HTTPS with a Cognito JWT authorizer. Source context is
loaded only from the deployment's private S3 bucket under a validated `sources/<context-id>/`
prefix. Lambda uses a scoped IAM role; deployer AWS credentials are not copied into the runtime.
Derived slices, cache entries, and audit events are persisted in KMS-encrypted DynamoDB tables.

The generated Cognito client is intended for an evaluation or pilot. Use a distinct confidential
client per agent or workload in production, store client secrets in a managed secrets service, and
map each client to explicit task and sensitivity policy.

## What the Framework Protects Against

- Unnecessary release of full repository or infrastructure memory.
- Agent misuse of high-sensitivity architecture facts.
- Token waste from repeatedly sending full context.
- Inconsistent review quality caused by missing task context.
- Lack of records showing what context an agent saw.

## What It Does Not Do By Itself

- It does not replace SAST, IaC scanners, or cloud posture tools.
- It does not prove that model output is correct.
- It does not approve privileged changes.
- It does not provide production-grade encryption in demo mode.
- It does not inspect every possible repository format or prevent sensitive source material from
  being uploaded by an authorized deployer.

## Production Requirements

- Use KMS/Vault-backed envelope encryption.
- Use SSO/OIDC or workload identity for agents.
- Store audit records in immutable storage.
- Integrate policy with OPA, Cedar, or an internal policy service.
- Red-team prompt-injection, over-broad context, and cross-agent leakage scenarios.
- Add WAF/rate limits, budgets, alarms, remote encrypted Terraform state, and organization-specific
  retention controls.

Operationalize these requirements with the [Policy Guide](docs/POLICY_GUIDE.md),
[AWS Deployer IAM](docs/DEPLOYER_IAM.md), [Operations Runbook](docs/OPERATIONS_RUNBOOK.md), and
[Production Readiness Checklist](docs/PRODUCTION_READINESS.md).
