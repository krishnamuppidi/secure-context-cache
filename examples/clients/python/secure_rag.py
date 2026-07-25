#!/usr/bin/env python3
"""Authorize retrieved candidates before sending context to a model."""

from __future__ import annotations

from acg_client import GatewayClient, build_context_block


def main() -> None:
    candidates = [
        {
            "candidate_id": "terraform-kms-guidance",
            "content": "Production Lambda functions must use a customer-managed KMS key.",
            "refs": ["terraform/prod/payments/lambda.tf"],
            "sensitivity": "high",
            "environment": "prod",
            "score": 0.94,
        },
        {
            "candidate_id": "restricted-incident",
            "content": "Restricted incident material must never be placed in the model prompt.",
            "refs": ["incidents/restricted.md"],
            "sensitivity": "restricted",
            "environment": "prod",
            "score": 0.91,
        },
    ]
    response = GatewayClient.from_env().authorize_retrieval(
        candidates=candidates,
        task_type="iac_security",
        path="terraform/prod/payments/lambda.tf",
        prompt="Review the production Lambda configuration",
        environment="prod",
        provider="openai",
    )
    if response["retrieval"]["fail_closed"]:
        raise RuntimeError("No candidate was authorized; refusing unrestricted retrieval fallback")

    # Only this bounded block should be passed to the model.
    print(build_context_block(response))


if __name__ == "__main__":
    main()
