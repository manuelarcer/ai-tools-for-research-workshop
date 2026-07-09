from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping


@dataclass
class Config:
    telegram_token: str
    anthropic_api_key: str
    group_id: int
    host_user_id: int
    model_default: str = "claude-sonnet-5"
    model_escalate: str = "claude-opus-4-8"
    cooldown_seconds: float = 8.0

    @classmethod
    def from_env(cls, env: Mapping[str, str]) -> "Config":
        return cls(
            telegram_token=env["TELEGRAM_TOKEN"],
            anthropic_api_key=env["ANTHROPIC_API_KEY"],
            group_id=int(env["GROUP_ID"]),
            host_user_id=int(env["HOST_USER_ID"]),
            model_default=env.get("MODEL_DEFAULT", "claude-sonnet-5"),
            model_escalate=env.get("MODEL_ESCALATE", "claude-opus-4-8"),
            cooldown_seconds=float(env.get("COOLDOWN_SECONDS", "8")),
        )
