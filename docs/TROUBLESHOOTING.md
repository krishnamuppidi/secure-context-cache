# Troubleshooting

Start with the exact runtime, account, region, context ID, policy version, and failing request ID.
Never paste credentials, deployment environment files, Terraform state, raw context, or tokens into
an issue or model prompt.

## `acg: command not found`

Activate the environment and install the project:

```bash
. .venv/bin/activate
pip install -e ".[dev]"
acg --help
```

As a source-tree fallback:

```bash
PYTHONPATH=src python -m agent_context_gateway.cli --help
```

## Local API Returns `401`

The request is missing `x-agent-api-key`. Send the same value supplied to the server through
`ACG_LOCAL_API_KEY`.

## Local API Returns `403 invalid agent credentials`

The request body `agent_id` must match `ACG_LOCAL_AGENT_ID`. If the server has no
`ACG_LOCAL_API_KEY`, only the documented demo identities are available; restart it with a generated
non-demo key for network testing.

## Local API Rejects `repo`

Set `ACG_ALLOWED_REPO_ROOT` before starting Uvicorn. The requested absolute directory must be that
root or a descendant and must exist inside the server/container filesystem.

## Deployment Stops at Account Guard

```bash
aws sts get-caller-identity
printf '%s\n' "$EXPECTED_AWS_ACCOUNT_ID"
```

Select the intended profile/account. Do not weaken the guard merely to make deployment continue.

## Terraform Reports Missing Permissions

Review [AWS Deployer IAM](DEPLOYER_IAM.md). Inspect the denied CloudTrail event and add only the
required action/resource to the reviewed deployment role. Confirm `iam:PassRole` permits only the
gateway Lambda role.

## Terraform Cannot Find the Lambda ZIP

Run `deploy/aws/deploy.sh`; it builds `build/acg-lambda.zip` before Terraform. Direct Terraform
commands require a valid `lambda_package_path` and matching hash.

## Health Check Fails After Apply

```bash
function_name=$(terraform -chdir=deploy/aws/terraform output -raw lambda_function_name)
aws logs tail "/aws/lambda/$function_name" --since 15m
curl -v "$(terraform -chdir=deploy/aws/terraform output -raw health_url)"
```

Check package build errors, missing Lambda environment variables, KMS/IAM denial, and API Gateway
integration errors.

## Cognito Token Request Fails

- Confirm the generated environment file exists and is mode `600`.
- Load it with `set -a; source deploy/aws/.acg-deployment.env; set +a`.
- Check region, token URL, client ID, client secret, and scope without printing secret values.
- Re-run `deploy.sh` if Terraform replaced the Cognito client.
- Confirm system time is correct.

Get a fresh token with:

```bash
./deploy/aws/get-token.sh >/dev/null && echo "token request succeeded"
```

## AWS API Returns `401`

The JWT is missing, expired, issued by another pool, has the wrong audience, or lacks the required
scope. Get a fresh token from `get-token.sh` and use the API URL from the same deployment.

## API Returns `403`

For local mode, verify agent ID and API key. For policy behavior, note that slice denials normally
return `200`; a transport `403` indicates identity/authentication permission failure.

## Context ID Returns `404`

```bash
set -a
source deploy/aws/.acg-deployment.env
set +a
aws s3 ls "s3://$ACG_CONTEXT_BUCKET/sources/<context-id>/" --recursive
```

Upload the context with `upload-context.sh` and use the exact ID. The ID cannot contain slash or
spaces.

## Capsule Has No Released Facts

Inspect `capsule.denied` in the successful response. Common reasons are:

- task type not granted to the identity;
- task sensitivity limit is too low;
- requested path does not match a slice reference;
- environment/task relevance does not match; or
- restricted context requires a trusted approval.

Do not solve this by sending the full repository directly to the model. Correct identity, policy,
context classification, or request scope.

## Freshness Warning Appears Immediately

Freshness is generated at scan time. Verify the policy's `max_slice_age_days` and timestamp format.
If stale slices persist in audit/table views, upload current context and make a new request.

## Request Times Out or Returns `502`/`504`

The AWS runtime downloads and scans the selected prefix synchronously. Check Lambda duration and
memory, object count, total context size, S3/KMS latency, and logs. Reduce/split the curated context.
The Lambda timeout must remain below API Gateway's integration limit for this synchronous design.

## Context Update Leaves Unexpected Files

`upload-context.sh` synchronizes supported suffixes with `--delete`. Verify the exact prefix and list
current and versioned objects. S3 versioning retains prior versions even after current objects are
deleted. Unsupported files from deployments predating suffix filtering may need an explicitly
reviewed cleanup.

## Custom Policy Is Ignored

Set an absolute `ACG_POLICY_FILE` before process startup or `deploy.sh`. Local API requires restart;
AWS requires redeployment because the policy is packaged into Lambda. Confirm the response's
`policy_version` matches the intended file.

## Destroy Fails

Use the same profile, account, region, project, and environment as deployment. Resolve deletion
protection, IAM, state drift, and KMS scheduling errors explicitly. Do not manually empty or delete
resources until the Terraform plan/state impact is understood.

## Collect a Safe Diagnostic Bundle

Safe items include:

- Git commit and application version;
- account ID only, region, project, and environment;
- redacted Terraform plan/error;
- HTTP status and request/audit IDs;
- policy version;
- Lambda error messages with prompts/context/credentials removed; and
- object counts and sizes without filenames when names are sensitive.

Never include `.acg-deployment.env`, Terraform state, access tokens, client secrets, API keys, raw
source files, or full capsule facts from confidential context.
