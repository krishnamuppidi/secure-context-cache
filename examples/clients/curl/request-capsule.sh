#!/usr/bin/env bash
set -euo pipefail

: "${ACG_API_URL:?Set ACG_API_URL}"
: "${ACG_BEARER_TOKEN:?Set ACG_BEARER_TOKEN}"

curl --fail-with-body --silent --show-error \
  "${ACG_API_URL%/}/v1/capsules" \
  -H "authorization: Bearer ${ACG_BEARER_TOKEN}" \
  -H "content-type: application/json" \
  --data '{
    "context_id": "platform-docs",
    "task_type": "architecture_qa",
    "path": "README.md",
    "prompt": "Explain the context authorization boundary",
    "agent_id": "documentation-agent",
    "user": "developer",
    "environment": "unknown"
  }'
