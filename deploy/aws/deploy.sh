#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
repo_root=$(cd "$script_dir/../.." && pwd)
terraform_dir="$script_dir/terraform"
package_dir="$repo_root/build/aws-lambda-package"
build_venv="$repo_root/build/aws-lambda-build-venv"
package_zip="$repo_root/build/acg-lambda.zip"
deployment_env="$script_dir/.acg-deployment.env"

auto_approve=false
if [[ "${1:-}" == "--auto-approve" ]]; then
  auto_approve=true
elif [[ -n "${1:-}" ]]; then
  echo "Usage: $0 [--auto-approve]" >&2
  exit 2
fi

for command_name in aws curl openssl python3 terraform zip; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Missing required command: $command_name" >&2
    exit 1
  fi
done

aws_region=${AWS_REGION:-${AWS_DEFAULT_REGION:-us-east-1}}
project=${ACG_PROJECT:-agent-context-gateway}
environment=${ACG_ENVIRONMENT:-dev}
context_id=${ACG_CONTEXT_ID:-default}
context_dir=${ACG_CONTEXT_DIR:-$repo_root/examples/sample_repo}
smoke_task_type=${ACG_SMOKE_TASK_TYPE:-iac_security}
if [[ -n "${ACG_SMOKE_PATH:-}" ]]; then
  smoke_path=$ACG_SMOKE_PATH
elif [[ "$context_dir" == "$repo_root/examples/sample_repo" ]]; then
  smoke_path=terraform/prod/payments/lambda.tf
else
  smoke_file=$(find "$context_dir" -type f \
    \( -name '*.tf' -o -name '*.tfvars' -o -name '*.yaml' -o -name '*.yml' \
       -o -name '*.json' -o -name '*.md' -o -name '*.py' -o -name '*.go' \) \
    -print -quit)
  if [[ -z "$smoke_file" ]]; then
    echo "Context directory has no supported files for the smoke test: $context_dir" >&2
    exit 1
  fi
  smoke_path=${smoke_file#"$context_dir"/}
fi

if [[ ! -d "$context_dir" ]]; then
  echo "Context directory does not exist: $context_dir" >&2
  exit 1
fi
if [[ ! "$context_id" =~ ^[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}$ ]]; then
  echo "ACG_CONTEXT_ID must use letters, numbers, dot, underscore, or hyphen (max 64)." >&2
  exit 1
fi

aws_args=()
if [[ -n "${AWS_PROFILE:-}" ]]; then
  aws_args+=(--profile "$AWS_PROFILE")
fi
aws_args+=(--region "$aws_region")

account_id=$(aws "${aws_args[@]}" sts get-caller-identity --query Account --output text)
if [[ -n "${EXPECTED_AWS_ACCOUNT_ID:-}" && "$EXPECTED_AWS_ACCOUNT_ID" != "$account_id" ]]; then
  echo "Credential safety check failed: expected $EXPECTED_AWS_ACCOUNT_ID, authenticated to $account_id." >&2
  exit 1
fi

echo "Deploying Agent Context Gateway to AWS account $account_id in $aws_region"
echo "Uploading context '$context_id' from $context_dir"

case "$package_dir" in
  "$repo_root"/build/*) ;;
  *) echo "Unsafe package directory: $package_dir" >&2; exit 1 ;;
esac
rm -rf -- "$package_dir"
case "$build_venv" in
  "$repo_root"/build/*) ;;
  *) echo "Unsafe build virtual environment: $build_venv" >&2; exit 1 ;;
esac
rm -rf -- "$build_venv"
rm -f -- "$package_zip"
mkdir -p "$package_dir" "$(dirname "$package_zip")" "$package_dir/config"

python3 -m venv "$build_venv"
"$build_venv/bin/pip" install --quiet --disable-pip-version-check --upgrade pip
"$build_venv/bin/pip" install --quiet --disable-pip-version-check \
  --target "$package_dir" "$repo_root[aws]"
cp "$repo_root/config/policy.example.json" "$package_dir/config/policy.json"
(cd "$package_dir" && zip -qr "$package_zip" .)
package_hash=$(openssl dgst -sha256 -binary "$package_zip" | openssl base64 -A)

terraform -chdir="$terraform_dir" init -input=false
terraform -chdir="$terraform_dir" fmt -check
terraform -chdir="$terraform_dir" validate

apply_args=()
if [[ "$auto_approve" == "true" ]]; then
  apply_args+=(-auto-approve)
fi
terraform -chdir="$terraform_dir" apply "${apply_args[@]}" \
  -var="aws_region=$aws_region" \
  -var="project=$project" \
  -var="environment=$environment" \
  -var="expected_aws_account_id=$account_id" \
  -var="lambda_package_path=$package_zip" \
  -var="lambda_package_hash=$package_hash"

api_url=$(terraform -chdir="$terraform_dir" output -raw api_url)
health_url=$(terraform -chdir="$terraform_dir" output -raw health_url)
context_bucket=$(terraform -chdir="$terraform_dir" output -raw context_bucket)
client_id=$(terraform -chdir="$terraform_dir" output -raw cognito_client_id)
client_secret=$(terraform -chdir="$terraform_dir" output -raw cognito_client_secret)
token_url=$(terraform -chdir="$terraform_dir" output -raw cognito_token_url)
scope=$(terraform -chdir="$terraform_dir" output -raw cognito_scope)

aws "${aws_args[@]}" s3 sync "$context_dir" \
  "s3://$context_bucket/sources/$context_id/" \
  --delete \
  --exclude '.git/*' \
  --exclude '.venv/*' \
  --exclude 'build/*' \
  --exclude '__pycache__/*'

health_ok=false
for _attempt in $(seq 1 30); do
  if curl --fail --silent --show-error "$health_url" >/dev/null; then
    health_ok=true
    break
  fi
  sleep 2
done
if [[ "$health_ok" != "true" ]]; then
  echo "Deployment completed, but health verification failed: $health_url" >&2
  exit 1
fi

token_response=$(curl --fail --silent --show-error \
  --user "$client_id:$client_secret" \
  --data-urlencode "grant_type=client_credentials" \
  --data-urlencode "scope=$scope" \
  "$token_url")
access_token=$(TOKEN_RESPONSE="$token_response" python3 -c \
  'import json, os; print(json.loads(os.environ["TOKEN_RESPONSE"])["access_token"])')

smoke_payload=$(CONTEXT_ID="$context_id" TASK_TYPE="$smoke_task_type" TASK_PATH="$smoke_path" \
  python3 -c 'import json, os; print(json.dumps({"context_id": os.environ["CONTEXT_ID"], "task_type": os.environ["TASK_TYPE"], "path": os.environ["TASK_PATH"], "prompt": "Verify the deployed Agent Context Gateway", "environment": "prod"}))')
smoke_response=$(curl --fail --silent --show-error \
  -X POST "$api_url/v1/capsules" \
  -H "authorization: Bearer $access_token" \
  -H "content-type: application/json" \
  --data "$smoke_payload")
SMOKE_RESPONSE="$smoke_response" python3 -c \
  'import json, os; d=json.loads(os.environ["SMOKE_RESPONSE"]); print(f"Authenticated smoke test passed: audit_id={d[\"capsule\"][\"audit_id\"]}")'

umask 077
{
  printf 'ACG_AWS_ACCOUNT_ID=%s\n' "$account_id"
  printf 'ACG_AWS_REGION=%s\n' "$aws_region"
  printf 'ACG_API_URL=%s\n' "$api_url"
  printf 'ACG_HEALTH_URL=%s\n' "$health_url"
  printf 'ACG_CONTEXT_BUCKET=%s\n' "$context_bucket"
  printf 'ACG_CONTEXT_ID=%s\n' "$context_id"
  printf 'ACG_CLIENT_ID=%s\n' "$client_id"
  printf 'ACG_CLIENT_SECRET=%s\n' "$client_secret"
  printf 'ACG_TOKEN_URL=%s\n' "$token_url"
  printf 'ACG_SCOPE=%s\n' "$scope"
  printf 'AWS_PROFILE=%s\n' "${AWS_PROFILE:-}"
} >"$deployment_env"
chmod 600 "$deployment_env"

echo
echo "Deployment complete."
echo "API: $api_url"
echo "Health: $health_url"
echo "Context bucket: s3://$context_bucket/sources/$context_id/"
echo "Client configuration (mode 600): $deployment_env"
echo "Invoke it with: $script_dir/invoke.sh"
