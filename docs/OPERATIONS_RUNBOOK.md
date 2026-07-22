# Operations Runbook

This runbook covers the AWS evaluation stack. Adapt it to the organization's incident, retention,
change, and access-management standards before production.

## Record the Deployment

Capture these non-secret values in the service inventory:

```bash
terraform -chdir=deploy/aws/terraform output
```

Record account, region, project, environment, API URL, context bucket, DynamoDB tables, Lambda
function, policy version, source owner, and operations owner. Do not copy the sensitive Cognito
client secret or Terraform state into tickets, wikis, chat, or model prompts.

`deploy/aws/.acg-deployment.env` contains a client secret and is mode `600`. Terraform state also
contains sensitive values. Store production state in an encrypted remote backend with locking,
versioning, least-privilege access, and audit logs.

## Health and Logs

```bash
set -a
source deploy/aws/.acg-deployment.env
set +a
curl -fsS "$ACG_HEALTH_URL"
function_name=$(terraform -chdir=deploy/aws/terraform output -raw lambda_function_name)
aws logs tail "/aws/lambda/$function_name" --since 30m
```

For live troubleshooting, add `--follow`. Avoid logging tokens, client secrets, request prompts, or
raw context.

## Functional Check

```bash
./deploy/aws/invoke.sh \
  iac_security \
  terraform/prod/payments/lambda.tf \
  "Operations verification" \
  "$ACG_CONTEXT_ID"
```

Verify HTTP success, expected policy version, at least one released fact for the known test path,
an audit ID, and a matching item in the audit table.

## Routine Checks

At an organization-defined interval:

- check API error rate, Lambda duration/throttles/errors/concurrency, and log anomalies;
- check DynamoDB throttles and KMS access-denied events;
- review S3 object inventory/version growth and context ownership;
- inspect capsule denial rates, freshness warnings, token estimates, and cache-hit telemetry;
- review Cognito client use and credential age;
- confirm CloudWatch log retention and budget alerts; and
- run an authenticated positive test plus unauthorized/forbidden negative tests.

The Terraform module does not create alarms, dashboards, WAF rules, or budgets. Add them before
production.

## Update Context Only

```bash
./deploy/aws/upload-context.sh /absolute/path/to/approved-export payments-platform
./deploy/aws/invoke.sh \
  architecture_qa \
  README.md \
  "Verify the refreshed context" \
  payments-platform
```

The upload synchronizes with `--delete`. Review the path and context ID first. Record the approved
source commit/export manifest and verify source hashes in the returned capsule.

## Update Code, Terraform, or Policy

1. Review repository changes and release notes.
2. Back up remote Terraform state and record the current Lambda code/package hash.
3. Set the same `ACG_PROJECT`, `ACG_ENVIRONMENT`, region, context ID, identity limits, and policy path
   used by the deployment.
4. Run tests and Terraform validation.
5. Run `./deploy/aws/deploy.sh` without auto-approval.
6. Review the plan for replacements, data deletion, IAM expansion, or endpoint/client changes.
7. Approve, then verify health, OAuth, capsule request, denials, audit persistence, and logs.
8. Monitor errors and latency through the rollback window.

The deployment script uploads the selected context again and runs a live authenticated smoke test.

## Rollback

- Application regression: restore the prior Git revision, rebuild, and run `deploy.sh` with the
  original deployment variables.
- Policy regression: point `ACG_POLICY_FILE` to the prior version and redeploy.
- Context regression: restore prior S3 object versions or upload the prior curated export.
- Terraform regression: do not manually delete resources first; review state and plan with an
  experienced Terraform operator.

Test rollback before production. The current repository does not automate blue/green Lambda or
policy rollout.

## Credential Rotation

The evaluation module creates one confidential Cognito client. Cognito client secrets are not
rotated in place. Replacing that client changes the client ID/secret and can interrupt consumers.

For production, extend the design to support two overlapping clients or one workload identity per
agent. Create the new identity, grant the minimum context/task scope, update consumers through a
secret manager, verify traffic, revoke the old identity, and preserve audit continuity. Do not send
new credentials through email or chat.

Local/Kubernetes API keys should be generated randomly, stored in a secret manager, rotated by
rolling the server and clients, and never shared across unrelated agents.

## Backup and Recovery

- S3 versioning protects prior source object versions, but the evaluation bucket is force-destroyed
  during teardown.
- DynamoDB point-in-time recovery is enabled for slices, cache, and audits.
- KMS key deletion has a seven-day waiting period.
- Terraform state must be backed up separately and protected as sensitive.

Define and test recovery procedures for S3 versions, DynamoDB point-in-time restore to new tables,
Terraform state, Cognito configuration, and KMS access. The module does not automatically reconnect
Lambda to restored tables.

## Incident Response

If credentials or context may be exposed:

1. stop affected clients and preserve logs/audit IDs;
2. revoke or replace the compromised client/API key;
3. restrict API access while investigating;
4. inspect CloudTrail, API Gateway, Cognito, Lambda, KMS, S3, and DynamoDB events;
5. identify released capsules and downstream model traces;
6. rotate downstream credentials if raw source contained secrets;
7. remove/replace affected context and verify S3 versions/retention requirements; and
8. document scope, decisions, recovery, and preventive changes.

Do not delete evidence or logs during investigation.

## Capacity and Limits

Each AWS request materializes the full selected S3 prefix and scans it synchronously. Lambda timeout
is 29 seconds because API Gateway has a 30-second integration limit. Measure object count, download
time, scan time, memory, and request latency with representative context.

Split large domains across context IDs or implement asynchronous ingestion/persistent slice reads
before scaling. Raising Lambda memory may improve CPU/network performance but does not remove API
Gateway's synchronous timeout.

## Teardown

```bash
./deploy/aws/destroy.sh
```

Review the plan carefully. Teardown removes the bucket and object versions, tables and PITR history,
Cognito client, API, Lambda, logs, and schedules the KMS key for deletion. Export any records subject
to retention before approval.
