from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPLOY = ROOT / "deploy" / "aws" / "deploy.sh"


def _run(extra_env: dict[str, str], tmp_path: Path) -> subprocess.CompletedProcess[str]:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir(exist_ok=True)
    for command in ("aws", "curl", "openssl", "terraform", "zip"):
        executable = fake_bin / command
        executable.write_text("#!/usr/bin/env sh\nexit 99\n")
        executable.chmod(0o755)
    return subprocess.run(
        [str(DEPLOY), "--auto-approve"],
        cwd=ROOT,
        env={**os.environ, "PATH": f"{fake_bin}:{os.environ['PATH']}", **extra_env},
        capture_output=True,
        text=True,
        check=False,
    )


def test_deploy_rejects_missing_context_before_aws_call(tmp_path: Path) -> None:
    result = _run({"ACG_CONTEXT_DIR": "/definitely/missing/acg-context"}, tmp_path)

    assert result.returncode == 1
    assert "Context directory does not exist" in result.stderr


def test_deploy_requires_policy_to_be_json_object(tmp_path: Path) -> None:
    policy = tmp_path / "policy.json"
    policy.write_text("[]")

    result = _run({"ACG_POLICY_FILE": str(policy)}, tmp_path)

    assert result.returncode == 1
    assert "Policy file must contain one valid JSON object" in result.stderr


def test_deploy_requires_smoke_task_to_be_granted(tmp_path: Path) -> None:
    result = _run({"ACG_ALLOWED_TASK_TYPES": "architecture_qa"}, tmp_path)

    assert result.returncode == 1
    assert "ACG_SMOKE_TASK_TYPE must be included" in result.stderr
