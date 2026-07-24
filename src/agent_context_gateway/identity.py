from __future__ import annotations

import os
from dataclasses import dataclass

from .models import AgentIdentity


@dataclass
class AgentCredential:
    identity: AgentIdentity
    api_key: str


class AgentRegistry:
    def __init__(self, credentials: dict[str, AgentCredential]) -> None:
        self.credentials = credentials

    @classmethod
    def demo(cls) -> AgentRegistry:
        return cls(
            {
                "secreviewagent": AgentCredential(
                    AgentIdentity(
                        agent_id="secreviewagent",
                        allowed_task_types=["iac_security", "code_review", "architecture_qa"],
                        max_sensitivity="high",
                    ),
                    "demo-secreviewagent-key",
                ),
                "onboarding": AgentCredential(
                    AgentIdentity(
                        agent_id="onboarding",
                        allowed_task_types=["onboarding", "architecture_qa"],
                        max_sensitivity="low",
                    ),
                    "demo-onboarding-key",
                ),
            }
        )

    @classmethod
    def from_env_or_demo(cls) -> AgentRegistry:
        """Build one local-runtime credential from environment, or use demo identities.

        AWS mode does not use this registry; API Gateway verifies Cognito JWTs and
        the runtime derives identity from the verified claims.
        """
        api_key = os.getenv("ACG_LOCAL_API_KEY")
        if not api_key:
            return cls.demo()
        agent_id = os.getenv("ACG_LOCAL_AGENT_ID", "local-agent")
        allowed_task_types = [
            item.strip()
            for item in os.getenv(
                "ACG_LOCAL_ALLOWED_TASK_TYPES",
                "code_review,iac_security,incident_triage,onboarding,architecture_qa",
            ).split(",")
            if item.strip()
        ]
        max_sensitivity = os.getenv("ACG_LOCAL_MAX_SENSITIVITY", "high")
        return cls(
            {
                agent_id: AgentCredential(
                    AgentIdentity(
                        agent_id=agent_id,
                        allowed_task_types=allowed_task_types,
                        max_sensitivity=max_sensitivity,
                        owner="local-runtime",
                    ),
                    api_key,
                )
            }
        )

    def authenticate(self, agent_id: str, api_key: str) -> AgentIdentity:
        credential = self.credentials.get(agent_id)
        if credential is None or credential.api_key != api_key:
            raise PermissionError("invalid agent credentials")
        return credential.identity
