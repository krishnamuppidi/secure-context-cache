#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
repo_root=$(cd "$script_dir/../.." && pwd)
deployment_env="$script_dir/.acg-deployment.env"
if [[ ! -f "$deployment_env" ]]; then
  echo "Missing $deployment_env. Run deploy.sh first." >&2
  exit 1
fi
set -a
# shellcheck disable=SC1090
source "$deployment_env"
set +a

context_dir=${1:-$repo_root/examples/sample_repo}
context_id=${2:-$ACG_CONTEXT_ID}
if [[ ! -d "$context_dir" ]]; then
  echo "Context directory does not exist: $context_dir" >&2
  exit 1
fi
if [[ ! "$context_id" =~ ^[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}$ ]]; then
  echo "Invalid context_id: $context_id" >&2
  exit 1
fi

aws_args=(--region "$ACG_AWS_REGION")
if [[ -n "${AWS_PROFILE:-}" ]]; then
  aws_args+=(--profile "$AWS_PROFILE")
fi
aws "${aws_args[@]}" s3 sync "$context_dir" \
  "s3://$ACG_CONTEXT_BUCKET/sources/$context_id/" \
  --delete \
  --exclude '.git/*' \
  --exclude '.venv/*' \
  --exclude 'build/*' \
  --exclude '__pycache__/*'
echo "Uploaded $context_dir to context_id '$context_id'."
