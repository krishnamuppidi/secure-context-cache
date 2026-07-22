# AWS Deployer IAM

The deployment identity creates and manages IAM, KMS, S3, DynamoDB, Lambda, CloudWatch Logs,
Cognito, and API Gateway resources. Prefer a short-lived role dedicated to an evaluation account.

`deploy/aws/deployer-policy.example.json` is a service-scoped starting policy. Replace:

- `<ACCOUNT_ID>` with the target account ID; and
- `<PROJECT>` with the `ACG_PROJECT` prefix, default `agent-context-gateway`.

Validate the rendered JSON:

```bash
sed \
  -e 's/<ACCOUNT_ID>/123456789012/g' \
  -e 's/<PROJECT>/agent-context-gateway/g' \
  deploy/aws/deployer-policy.example.json \
  > /tmp/acg-deployer-policy.json
python -m json.tool /tmp/acg-deployer-policy.json >/dev/null
```

Have the AWS account administrator review and attach it to a short-lived deployment role. Do not
automatically apply a repository policy in an account you do not control.

## Why Some Resources Use `*`

KMS keys, S3 buckets with generated suffixes, API Gateway resources, and Cognito resources do not
have final ARNs before Terraform creates them. Several create/list/tag APIs also require wildcard
resource scope. The example therefore limits actions by service but uses `Resource: "*"` for the
dynamic resource group.

For stronger controls:

- deploy into a dedicated account or sandbox organizational unit;
- apply an SCP or permission boundary denying unrelated regions and destructive account actions;
- require project/environment request tags where the AWS API supports tag-on-create conditions;
- restrict the deployment session to one region;
- keep the IAM role and `iam:PassRole` resource prefix narrow; and
- remove permissions after deployment if a separate operations role owns updates.

## Validate Before Deployment

```bash
aws sts get-caller-identity
export EXPECTED_AWS_ACCOUNT_ID=123456789012
terraform -chdir=deploy/aws/terraform init
terraform -chdir=deploy/aws/terraform plan \
  -var="expected_aws_account_id=$EXPECTED_AWS_ACCOUNT_ID"
```

The wrapper supplies additional package variables automatically; use `deploy.sh` for the real plan.
Run it without `--auto-approve` first.

Provider versions and AWS APIs evolve. If deployment reports a denied action, inspect the exact
CloudTrail event, add only the required action/resource, and update the reviewed policy. Do not
respond by granting blanket administrator access in a production account.

## Runtime Role

Terraform creates a separate Lambda execution role. It can list/read the created context bucket,
read/write the three created DynamoDB tables, use the created KMS key, and write Lambda logs. It
cannot upload source context, manage infrastructure, or read arbitrary S3 buckets.
