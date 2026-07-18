#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
terraform_dir="$script_dir/terraform"
deployment_env="$script_dir/.acg-deployment.env"
if [[ -f "$deployment_env" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$deployment_env"
  set +a
fi

aws_region=${ACG_AWS_REGION:-${AWS_REGION:-${AWS_DEFAULT_REGION:-us-east-1}}}
project=${ACG_PROJECT:-agent-context-gateway}
environment=${ACG_ENVIRONMENT:-dev}
aws_args=(--region "$aws_region")
if [[ -n "${AWS_PROFILE:-}" ]]; then
  aws_args+=(--profile "$AWS_PROFILE")
fi
account_id=$(aws "${aws_args[@]}" sts get-caller-identity --query Account --output text)

terraform -chdir="$terraform_dir" destroy \
  -var="aws_region=$aws_region" \
  -var="project=$project" \
  -var="environment=$environment" \
  -var="expected_aws_account_id=$account_id" \
  -var="lambda_package_path=$(cd "$script_dir/../.." && pwd)/build/acg-lambda.zip"
