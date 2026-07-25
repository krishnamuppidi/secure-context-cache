from __future__ import annotations

import argparse
from pathlib import Path

from .capsule import build_capsule
from .gateway import AgentContextGateway
from .identity import AgentRegistry
from .ingest import scan_repo
from .insights import generate_context_insights
from .io import read_json, write_json
from .metrics import compute_metrics
from .models import ContextGraph, ContextNode, ContextSlice, DeniedSlice, ReleasedFact, TaskRequest
from .optimization import build_optimization_plan
from .slices import build_slices


def graph_from_json(path: Path) -> ContextGraph:
    raw = read_json(path)
    return ContextGraph(
        root=raw["root"],
        generated_at=raw["generated_at"],
        nodes=[ContextNode(**item) for item in raw["nodes"]],
        edges=[],
    )


def slices_from_json(path: Path) -> list[ContextSlice]:
    return [ContextSlice(**item) for item in read_json(path)]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Agent Context Gateway - deployable control plane for Secure Context Cache"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    ingest = sub.add_parser("ingest", help="Build a context graph from a repository")
    ingest.add_argument("repo", type=Path)
    ingest.add_argument("--out", type=Path, default=Path("build/context-graph.json"))

    slice_cmd = sub.add_parser("slice", help="Build policy-scoped context slices")
    slice_cmd.add_argument("graph", type=Path)
    slice_cmd.add_argument("--out", type=Path, default=Path("build/context-slices.json"))

    capsule_cmd = sub.add_parser("capsule", help="Build a task-scoped context capsule")
    capsule_cmd.add_argument("slices", type=Path)
    capsule_cmd.add_argument("--task-type", default="iac_security")
    capsule_cmd.add_argument("--path", required=True)
    capsule_cmd.add_argument("--prompt", required=True)
    capsule_cmd.add_argument("--agent-id", default="secreviewagent")
    capsule_cmd.add_argument("--api-key", default="demo-secreviewagent-key")
    capsule_cmd.add_argument("--environment", default="unknown")
    capsule_cmd.add_argument("--out", type=Path, default=Path("build/context-capsule.json"))
    capsule_cmd.add_argument("--audit-out", type=Path, default=Path("build/audit-record.json"))

    insights_cmd = sub.add_parser("insights", help="Generate context release insights for a capsule")
    insights_cmd.add_argument("capsule", type=Path)
    insights_cmd.add_argument("--out", type=Path, default=Path("build/context-insights.json"))

    demo = sub.add_parser("demo", help="Run full demo flow")
    demo.add_argument("--repo", type=Path, default=Path("examples/sample_repo"))
    demo.add_argument("--out", type=Path, default=Path("build/demo"))

    optimize = sub.add_parser(
        "optimize",
        help="Build a secure token-optimization plan and stable provider-cacheable context",
    )
    optimize.add_argument("--repo", type=Path, default=Path("examples/sample_repo"))
    optimize.add_argument("--task-type", default="iac_security")
    optimize.add_argument("--path", required=True)
    optimize.add_argument("--prompt", required=True)
    optimize.add_argument("--agent-id", default="secreviewagent")
    optimize.add_argument("--api-key", default="demo-secreviewagent-key")
    optimize.add_argument("--environment", default="unknown")
    optimize.add_argument("--context-id", default="default")
    optimize.add_argument("--provider", default="generic")
    optimize.add_argument("--model", default="")
    optimize.add_argument("--tokenizer", default="word")
    optimize.add_argument("--token-budget", type=int)
    optimize.add_argument("--out", type=Path, default=Path("build/optimization.json"))

    args = parser.parse_args()
    if args.command == "ingest":
        graph = scan_repo(args.repo)
        write_json(args.out, graph.to_dict())
    elif args.command == "slice":
        graph = graph_from_json(args.graph)
        slices = build_slices(graph)
        write_json(args.out, [item.to_dict() for item in slices])
    elif args.command == "capsule":
        registry = AgentRegistry.demo()
        identity = registry.authenticate(args.agent_id, args.api_key)
        slices = slices_from_json(args.slices)
        task = TaskRequest(
            task_type=args.task_type,
            path=args.path,
            prompt=args.prompt,
            agent_id=args.agent_id,
            environment=args.environment,
        )
        capsule = build_capsule(task, identity, slices)
        metrics = compute_metrics(capsule, slices)
        write_json(args.out, capsule.to_dict())
        write_json(
            args.audit_out,
            {
                "audit_id": capsule.audit_id,
                "request_id": capsule.request_id,
                "released_slice_ids": [item.slice_id for item in capsule.facts],
                "denied": [item.__dict__ for item in capsule.denied],
                "metrics": metrics.to_dict(),
            },
        )
    elif args.command == "insights":
        raw = read_json(args.capsule)
        capsule = build_capsule(
            TaskRequest(**raw["task"]),
            AgentRegistry.demo().authenticate(raw["task"]["agent_id"], "demo-secreviewagent-key"),
            [],
        )
        capsule.facts = [ReleasedFact(**item) for item in raw.get("facts", [])]
        capsule.denied = [DeniedSlice(**item) for item in raw.get("denied", [])]
        insights = generate_context_insights(capsule)
        write_json(args.out, [item.to_dict() for item in insights])
    elif args.command == "demo":
        result = AgentContextGateway().run_demo(args.repo, args.out)
        print(
            f"capsule_facts={len(result.capsule.facts)} denied={len(result.capsule.denied)} "
            f"cache_hit={result.capsule.cache_hit} audit_id={result.capsule.audit_id}"
        )
    elif args.command == "optimize":
        gateway = AgentContextGateway()
        _graph, slices = gateway.load_context(args.repo, context_id=args.context_id)
        task = TaskRequest(
            task_type=args.task_type,
            path=args.path,
            prompt=args.prompt,
            agent_id=args.agent_id,
            environment=args.environment,
            context_id=args.context_id,
            provider=args.provider,
            model=args.model,
            tokenizer=args.tokenizer,
            token_budget=args.token_budget,
        )
        capsule, metrics = gateway.request_capsule(task, slices, api_key=args.api_key)
        plan = build_optimization_plan(capsule, metrics, task)
        write_json(
            args.out,
            {
                "capsule": capsule.to_dict(),
                "metrics": metrics.to_dict(),
                "optimization": plan.to_dict(),
            },
        )
        print(
            f"full={metrics.full_context_tokens} capsule={metrics.capsule_tokens} "
            f"reduction={metrics.token_reduction_percent}% "
            f"budget={metrics.token_budget_status} out={args.out}"
        )


if __name__ == "__main__":
    main()
