from __future__ import annotations

from pathlib import Path

from .models import ContextEdge, ContextGraph, ContextNode, file_sha256, stable_id, utc_now

INFRA_SUFFIXES = {".tf", ".tfvars", ".yaml", ".yml", ".json", ".md", ".py", ".go"}


def infer_environment(path: Path) -> str:
    lowered = str(path).lower()
    for env in ("prod", "production", "stage", "staging", "dev", "test"):
        if f"/{env}/" in lowered or lowered.startswith(f"{env}/"):
            return "prod" if env == "production" else "stage" if env == "staging" else env
    return "unknown"


def infer_sensitivity(path: Path, text: str) -> str:
    lowered = f"{path} {text}".lower()
    if any(term in lowered for term in ("iam", "role", "policy", "secret", "kms", "token", "prod")):
        return "high"
    if any(term in lowered for term in ("vpc", "security_group", "database", "rds", "lambda")):
        return "medium"
    return "low"


def scan_repo(repo: Path) -> ContextGraph:
    repo = repo.resolve()
    nodes: list[ContextNode] = []
    edges: list[ContextEdge] = []
    root_id = stable_id("repo", str(repo))
    nodes.append(ContextNode(id=root_id, kind="repository", name=repo.name, path=".", sensitivity="low"))

    for file_path in sorted(repo.rglob("*")):
        if not file_path.is_file() or file_path.suffix not in INFRA_SUFFIXES:
            continue
        rel = file_path.relative_to(repo)
        text = file_path.read_text(errors="ignore")[:4000]
        node_id = stable_id("file", str(rel), text[:256])
        sensitivity = infer_sensitivity(rel, text)
        env = infer_environment(rel)
        nodes.append(
            ContextNode(
                id=node_id,
                kind="file",
                name=rel.name,
                path=str(rel),
                environment=env,
                sensitivity=sensitivity,
                metadata={
                    "source_system": "git",
                    "source_hash": file_sha256(file_path),
                    "parser_version": "demo-file-scanner-v1",
                    "freshness_timestamp": utc_now(),
                    "sha_hint": stable_id(text[:512]),
                },
            )
        )
        edges.append(ContextEdge(source=root_id, target=node_id, relation="contains", sensitivity=sensitivity))
    return ContextGraph(root=str(repo), generated_at=utc_now(), nodes=nodes, edges=edges)
