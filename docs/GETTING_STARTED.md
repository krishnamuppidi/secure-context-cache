# Getting Started

This guide takes a new operator from clone to a verified request. Choose one runtime:

| Runtime | Best for | Identity | Context source | Persistence |
| --- | --- | --- | --- | --- |
| CLI | Learning and offline evaluation | Built-in demo identity | Local directory | JSON files |
| Local API | Integration development | API key | Allowed local directory | In-memory cache |
| Docker | Reproducible local API | API key | Image sample or read-only mount | In-memory cache |
| AWS | Controlled shared pilot | Cognito OAuth client | Private KMS-encrypted S3 | DynamoDB and S3 |
| Kubernetes | Local-runtime cluster evaluation | Kubernetes Secret/API key | Image sample or mounted directory | Pod-local memory |

The AWS path is the recommended shared evaluation. The Kubernetes manifest runs the local runtime;
it is not a replacement for the AWS persistence and identity controls.

## Prerequisites

- Git and Python 3.11 or newer.
- For Docker: Docker Engine or Docker Desktop.
- For AWS: AWS CLI, Terraform 1.5 or newer, `curl`, `openssl`, and `zip` on Linux, macOS, or WSL.
- For Kubernetes: `kubectl`, a cluster, and a container registry or local image loader.

## Clone and Install

```bash
git clone https://github.com/krishnamuppidi/secure-context-cache.git
cd secure-context-cache
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

PowerShell activation is `.venv\\Scripts\\Activate.ps1`. The AWS helper scripts require a Bash
environment; use WSL on Windows.

## Run the Offline Demo

```bash
acg demo --repo examples/sample_repo --out build/demo
```

A successful run prints a capsule fact count, denial count, cache state, and audit ID. It creates:

- `context-graph.json`: scanned source manifest;
- `context-slices.json`: derived policy units;
- `context-capsule.json`: facts released for the task;
- `context-insights.json`: deterministic observations about the released capsule;
- `audit-record.json`: decision and provenance record; and
- `metrics.json`: estimated full-context and released-capsule token counts.
- `optimization-plan.json`: stable model context, provider-cache namespace, token budget, and
  optimization-lever status.

Inspect the decision:

```bash
python -m json.tool build/demo/context-capsule.json
python -m json.tool build/demo/audit-record.json
python -m json.tool build/demo/metrics.json
```

The scanner derives path, environment, sensitivity, provenance, and policy facts. It does not place
raw file contents or secrets in a capsule.

## Run Individual CLI Stages

```bash
acg ingest examples/sample_repo --out build/context-graph.json
acg slice build/context-graph.json --out build/context-slices.json
acg capsule build/context-slices.json \
  --task-type iac_security \
  --path terraform/prod/payments/lambda.tf \
  --prompt "Review this change" \
  --environment prod \
  --out build/context-capsule.json \
  --audit-out build/audit-record.json
acg insights build/context-capsule.json --out build/context-insights.json
```

The CLI credentials are demo-only. Do not reuse them in a networked deployment.

## Run the Local API

Install the API dependencies and supply a non-demo local credential:

```bash
pip install -e ".[api,dev]"
export ACG_LOCAL_AGENT_ID=local-agent
export ACG_LOCAL_API_KEY="$(openssl rand -hex 32)"
export ACG_LOCAL_ALLOWED_TASK_TYPES=code_review,iac_security,architecture_qa
export ACG_LOCAL_MAX_SENSITIVITY=high
export ACG_ALLOWED_REPO_ROOT="$(pwd)/examples/sample_repo"
uvicorn agent_context_gateway.api:app --reload
```

In another terminal, use the same API key:

```bash
curl -sS http://127.0.0.1:8000/health
curl -sS http://127.0.0.1:8000/v1/capsules \
  -H 'content-type: application/json' \
  -H "x-agent-api-key: $ACG_LOCAL_API_KEY" \
  -d '{
    "task_type": "iac_security",
    "path": "terraform/prod/payments/lambda.tf",
    "prompt": "Review this change",
    "agent_id": "local-agent",
    "user": "local-developer",
    "environment": "prod"
  }' | python -m json.tool
```

Local interactive OpenAPI documentation is available at `http://127.0.0.1:8000/docs`.

To scan another directory, set `ACG_ALLOWED_REPO_ROOT` to that directory before starting the server
and include its absolute path as `repo` in the request. The API rejects paths outside the allowed
root.

## Run with Docker

```bash
docker build -t secure-context-cache:0.7.0 .
export ACG_LOCAL_API_KEY="$(openssl rand -hex 32)"
docker run --rm -p 8080:8080 \
  -e ACG_LOCAL_AGENT_ID=local-agent \
  -e ACG_LOCAL_API_KEY="$ACG_LOCAL_API_KEY" \
  -e ACG_LOCAL_ALLOWED_TASK_TYPES=code_review,iac_security,architecture_qa \
  -e ACG_ALLOWED_REPO_ROOT=/contexts/repo \
  -v /absolute/path/to/repository:/contexts/repo:ro \
  secure-context-cache:0.7.0
```

Call `http://127.0.0.1:8080/v1/capsules` with `agent_id` set to `local-agent`, the API key header,
and `repo` set to `/contexts/repo`.

## Deploy the AWS Evaluation Stack

Follow [AWS Deployment](../deploy/aws/README.md). The short path is:

```bash
export AWS_PROFILE=my-profile
export AWS_REGION=us-east-1
export EXPECTED_AWS_ACCOUNT_ID=123456789012
export ACG_CONTEXT_DIR=/absolute/path/to/repository
export ACG_CONTEXT_ID=payments-platform
./deploy/aws/deploy.sh --auto-approve
./deploy/aws/invoke.sh \
  iac_security \
  terraform/prod/payments/lambda.tf \
  "Review this change" \
  payments-platform
```

Do not use `--auto-approve` until you are comfortable with the Terraform plan and target account.

## Next Steps

- [Agent Integration](AGENT_INTEGRATION.md)
- [API Reference](API_REFERENCE.md)
- [Policy Guide](POLICY_GUIDE.md)
- [Context Sources](CONTEXT_SOURCES.md)
- [Kubernetes](KUBERNETES.md)
- [Operations Runbook](OPERATIONS_RUNBOOK.md)
- [Troubleshooting](TROUBLESHOOTING.md)

## Cleanup

Local artifacts are under `build/` and ignored by Git. Remove the AWS evaluation stack with:

```bash
./deploy/aws/destroy.sh
```

Terraform shows a destruction plan and requests confirmation. The evaluation S3 bucket uses
`force_destroy`; teardown removes uploaded context and is not appropriate for durable production
data without changing the lifecycle design.
