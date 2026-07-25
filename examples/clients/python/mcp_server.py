#!/usr/bin/env python3
"""Expose a narrow Secure Context Cache capsule tool through MCP."""

from __future__ import annotations

from typing import Any

from acg_client import GatewayClient
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("secure-context-cache")


@mcp.tool()
def request_context_capsule(
    task_type: str,
    path: str,
    prompt: str,
    environment: str = "unknown",
    context_id: str = "default",
) -> dict[str, Any]:
    """Return policy-approved facts and audit metadata; never return gateway credentials."""
    response = GatewayClient.from_env().request(
        task_type=task_type,
        path=path,
        prompt=prompt,
        environment=environment,
        context_id=context_id,
    )
    capsule = response["capsule"]
    return {
        "request_id": capsule["request_id"],
        "audit_id": capsule["audit_id"],
        "expires_at": capsule["expires_at"],
        "facts": capsule.get("facts", []),
        "denied": capsule.get("denied", []),
        "freshness_warnings": capsule.get("freshness_warnings", []),
    }


if __name__ == "__main__":
    mcp.run()
