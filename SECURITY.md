# Security Model

Agent Context Gateway is designed around deny-by-default context release.

## Trust Boundaries

- The model is not trusted with authority.
- The gateway is responsible for selecting and releasing context.
- Policy decides which slices can be released to an agent for a task.
- Audit records capture every release and denial.
- Production deployments should replace demo credentials with enterprise identity.

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

## Production Requirements

- Use KMS/Vault-backed envelope encryption.
- Use SSO/OIDC or workload identity for agents.
- Store audit records in immutable storage.
- Integrate policy with OPA, Cedar, or an internal policy service.
- Red-team prompt-injection, over-broad context, and cross-agent leakage scenarios.
