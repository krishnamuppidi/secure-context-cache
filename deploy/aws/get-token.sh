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

response=$(curl --fail --silent --show-error \
  --user "$ACG_CLIENT_ID:$ACG_CLIENT_SECRET" \
  --data-urlencode "grant_type=client_credentials" \
  --data-urlencode "scope=$ACG_SCOPE" \
  "$ACG_TOKEN_URL")
TOKEN_RESPONSE="$response" python3 -c \
  'import json, os; print(json.loads(os.environ["TOKEN_RESPONSE"])["access_token"])'

