#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
deployment_env="$script_dir/.acg-deployment.env"
if [[ ! -f "$deployment_env" ]]; then
  echo "Missing $deployment_env. Run deploy.sh first." >&2
  exit 1
fi
set -a
# shellcheck disable=SC1090
source "$deployment_env"
set +a

task_type=${1:-iac_security}
task_path=${2:-terraform/prod/payments/lambda.tf}
prompt=${3:-Review this context for security and operational blast-radius risk}
context_id=${4:-$ACG_CONTEXT_ID}
token=$("$script_dir/get-token.sh")
payload=$(CONTEXT_ID="$context_id" TASK_TYPE="$task_type" TASK_PATH="$task_path" TASK_PROMPT="$prompt" \
  python3 -c 'import json, os; print(json.dumps({"context_id": os.environ["CONTEXT_ID"], "task_type": os.environ["TASK_TYPE"], "path": os.environ["TASK_PATH"], "prompt": os.environ["TASK_PROMPT"], "environment": "prod"}))')
curl --fail --silent --show-error \
  -X POST "$ACG_API_URL/v1/capsules" \
  -H "authorization: Bearer $token" \
  -H "content-type: application/json" \
  --data "$payload" | python3 -m json.tool

