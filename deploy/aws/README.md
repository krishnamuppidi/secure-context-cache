# AWS Deployment Guide

`deploy.sh` provisions a secure evaluation stack and proves it with a live authenticated request.
It derives the AWS account from the active credentials; no account ID is hard-coded.

Use Bash on Linux, macOS, or WSL. Read [AWS Deployer IAM](../../docs/DEPLOYER_IAM.md) before granting
permissions and [Context Sources](../../docs/CONTEXT_SOURCES.md) before uploading company material.

## Resources

- API Gateway HTTP API for a managed HTTPS endpoint.
- Cognito user pool, OAuth resource server, domain, and confidential machine client.
- Lambda running the FastAPI application through Mangum.
- KMS key and alias.
- Private S3 bucket with versioning, KMS encryption, and public-access blocking.
- Three KMS-encrypted DynamoDB on-demand tables for slices, cache, and audits.
- IAM execution role restricted to the created bucket, tables, and key.
- CloudWatch log group with configurable retention.

## Configuration

Environment variables accepted by `deploy.sh`:

- `AWS_PROFILE`: optional AWS CLI profile.
- `AWS_REGION`: defaults to `us-east-1`.
- `EXPECTED_AWS_ACCOUNT_ID`: optional account safety guard.
- `ACG_PROJECT`: defaults to `agent-context-gateway`.
- `ACG_ENVIRONMENT`: defaults to `dev`.
- `ACG_CONTEXT_DIR`: directory uploaded as context; defaults to the sample repository.
- `ACG_CONTEXT_ID`: logical context name; defaults to `default`.
- `ACG_POLICY_FILE`: JSON policy packaged into Lambda; defaults to `config/policy.example.json`.
- `ACG_ALLOWED_TASK_TYPES`: comma-separated tasks granted to the generated client.
- `ACG_MAX_SENSITIVITY`: `low`, `medium`, or `high`; defaults to `high`.
- `ACG_SMOKE_TASK_TYPE`: defaults to `iac_security` and must appear in `ACG_ALLOWED_TASK_TYPES`.
- `ACG_SMOKE_PATH`: defaults to the included Terraform example.

The smoke task/path must release at least one fact under the selected policy and sensitivity limit;
deployment fails rather than treating an all-denied capsule as successful.

Without `--auto-approve`, Terraform shows the plan and asks for confirmation.

Example:

```bash
export AWS_PROFILE=my-profile
export AWS_REGION=us-east-1
export EXPECTED_AWS_ACCOUNT_ID=123456789012
export ACG_CONTEXT_DIR=/absolute/path/to/approved-export
export ACG_CONTEXT_ID=payments-platform
export ACG_POLICY_FILE=/absolute/path/to/policy.json
export ACG_ALLOWED_TASK_TYPES=code_review,iac_security,architecture_qa
export ACG_MAX_SENSITIVITY=high
./deploy/aws/deploy.sh
```

## Direct API Use

After deployment:

```bash
set -a
source deploy/aws/.acg-deployment.env
set +a
token=$(./deploy/aws/get-token.sh)
```

Request a capsule:

```bash
curl -sS "$ACG_API_URL/v1/capsules" \
  -H "authorization: Bearer $token" \
  -H 'content-type: application/json' \
  -d '{
    "context_id": "default",
    "task_type": "iac_security",
    "path": "terraform/prod/payments/lambda.tf",
    "prompt": "Review this change",
    "environment": "prod"
  }'
```

Change the endpoint to `/v1/insights` to include context-derived insights.

For complete fields, responses, error behavior, and client code, see
[API Reference](../../docs/API_REFERENCE.md) and
[Agent Integration](../../docs/AGENT_INTEGRATION.md).

## Context Layout

`upload-context.sh` synchronizes files to:

```text
s3://<context-bucket>/sources/<context-id>/...
```

Requests can select only a validated context ID. The application does not accept a production
filesystem path or arbitrary S3 bucket/key. This prevents callers from using the API as a general
filesystem or S3 reader.

Upload scripts include only `.tf`, `.tfvars`, `.yaml`, `.yml`, `.json`, `.md`, `.py`, and `.go`
files. This is not secret scanning; curate and inspect source before upload.

## Credential Handling

- AWS credentials remain in the caller's AWS CLI environment/profile and are used only by AWS CLI
  and Terraform.
- Lambda receives no AWS access keys; the SDK uses its execution role.
- API clients receive a Cognito client ID and secret. The generated local configuration is mode
  `600` and ignored by Git.
- Prefer separate machine clients and a secrets manager for long-lived production integrations.

## Persistence

- S3 stores source context.
- `context-slices` records derived, source-hashed slices.
- `context-cache` records released slice IDs and hit counts by normalized task key.
- `audit-events` records every successful authenticated gateway decision and token metrics.

## Operations

Health:

```bash
curl -sS "$(terraform -chdir=deploy/aws/terraform output -raw health_url)"
```

Lambda logs:

```bash
function_name=$(terraform -chdir=deploy/aws/terraform output -raw lambda_function_name)
aws logs tail "/aws/lambda/$function_name" --follow
```

Re-run `deploy.sh` to update application code or Terraform. Re-run `upload-context.sh` to update only
context files.

Use [Operations Runbook](../../docs/OPERATIONS_RUNBOOK.md) for updates, rollback, credential
rotation, backup/recovery, incidents, and capacity limits.

## Cost and Teardown

The stack uses serverless/on-demand services, but it creates billable AWS resources. KMS keys have a
recurring charge even at low traffic. Configure AWS Budgets before a long-running pilot.

Remove the stack:

```bash
./deploy/aws/destroy.sh
```

The evaluation bucket uses `force_destroy = true`, so Terraform can remove uploaded context during
teardown. Enable Cognito deletion protection and change S3 lifecycle/deletion policy before using
the stack for durable production data.

## Troubleshooting

See [Troubleshooting](../../docs/TROUBLESHOOTING.md) for account guards, permissions, Lambda health,
Cognito tokens, API errors, empty capsules, context updates, timeouts, policy loading, and teardown.

## Production Boundary

The stack creates one shared evaluation client and synchronously scans the selected S3 prefix on
every request. It does not configure WAF, alarms, budgets, remote Terraform state, immutable audit
export, approval-service integration, or disaster recovery. Complete the
[Production Readiness Checklist](../../docs/PRODUCTION_READINESS.md) before broader use.
