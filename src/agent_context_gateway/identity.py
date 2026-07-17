from __future__ import annotations

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
    def demo(cls) -> "AgentRegistry":
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

    def authenticate(self, agent_id: str, api_key: str) -> AgentIdentity:
        credential = self.credentials.get(agent_id)
        if credential is None or credential.api_key != api_key:
            raise PermissionError("invalid agent credentials")
        return credential.identity

