# Context Sources

The gateway accepts curated repositories, documentation directories, and infrastructure trees. The
deployer is responsible for deciding what may enter the context store.

## Supported Files

The scanner supports:

- Terraform: `.tf`, `.tfvars`
- YAML: `.yaml`, `.yml`
- JSON: `.json`
- Markdown: `.md`
- Python: `.py`
- Go: `.go`

AWS upload scripts include only these suffixes and exclude `.git`, `.venv`, `build`, and
`__pycache__` directories. Local scanning also ignores unsupported suffixes.

`.tfvars`, JSON, YAML, source code, and Markdown can still contain secrets or regulated data. File
type filtering is not content inspection.

## What the Scanner Reads

For each supported file, the scanner:

- hashes the complete file for provenance;
- reads the first 4,000 text characters for sensitivity inference;
- derives environment from path terms such as `prod`, `stage`, `dev`, and `test`;
- creates file-level scope and operational relevance facts; and
- records a freshness timestamp at scan time.

The capsule returns derived facts and source references, not raw file content or credential values.
The AWS runtime still stores the uploaded source file in encrypted S3 and downloads it into Lambda's
temporary directory while processing a request.

## Curate Before Upload

Use a dedicated export directory when the source repository contains material that the gateway does
not need:

```bash
mkdir -p /safe/agent-context/payments
# Copy only approved architecture, IaC, runbooks, and metadata into that directory.
export ACG_CONTEXT_DIR=/safe/agent-context/payments
export ACG_CONTEXT_ID=payments-platform
./deploy/aws/deploy.sh
```

Before upload:

1. remove credentials, tokens, private keys, state files, secrets, and personal data;
2. inspect `.tfvars`, YAML, JSON, Markdown, Python, and Go files;
3. include only the task domains the target agent needs;
4. use a separate context ID for materially different trust boundaries; and
5. verify the active AWS account and region.

Do not point the uploader at a home directory, workspace root, secrets directory, Terraform state
directory, or broad shared drive.

## Context IDs

A context ID is 1-64 characters and may contain letters, numbers, dot, underscore, or hyphen. It
maps to this private S3 prefix:

```text
sources/<context-id>/
```

The API validates the ID and cannot read an arbitrary bucket or key. Use stable, non-secret names
such as `payments-platform` or `developer-docs-v2`.

## Upload and Replacement

Initial deployment:

```bash
export ACG_CONTEXT_DIR=/absolute/path/to/approved-export
export ACG_CONTEXT_ID=payments-platform
./deploy/aws/deploy.sh
```

Update without redeploying application code:

```bash
./deploy/aws/upload-context.sh /absolute/path/to/approved-export payments-platform
```

The scripts use `aws s3 sync --delete` within the selected context prefix. Supported files removed
from the local export are deleted from the current S3 view. S3 versioning is enabled in the
evaluation stack, so prior object versions remain until the bucket is destroyed or lifecycle rules
remove them.

Always verify the context ID and local path before running an update.

## Freshness and Versioning

Freshness timestamps represent scan time, not the source repository commit time. Source hashes let
operators correlate a released fact with file contents. For stronger provenance, include an
approved manifest containing repository URL, commit SHA, export time, and owner in the curated
source directory.

The current API processes the latest S3 object versions. It does not accept an S3 version ID or Git
commit selector. Use separate context IDs for controlled parallel versions when necessary.

## Size and Performance

The current AWS runtime lists and downloads the complete selected prefix, then scans it for every
request. There is no enforced repository-size, object-count, or file-size quota in the application.
API Gateway and Lambda impose request-duration limits, so start with a small curated source and
measure latency before expanding it.

For large estates, use preprocessing to produce compact approved manifests, split domains across
context IDs, or implement asynchronous ingestion and persistent slice retrieval before production.

## Deletion and Recovery

`destroy.sh` removes the evaluation bucket and all object versions because Terraform uses
`force_destroy = true`. For durable production data, remove force-destroy behavior, define retention
and legal-hold requirements, enable backup monitoring, and test object-version restoration.
