from __future__ import annotations
from dataclasses import dataclass
from bot.config import Config

TRIVIAL_WORDS = {
    "gracias", "ok", "okay", "vale", "listo", "perfecto", "genial",
    "👍", "🙏", "👌", "si", "sí", "no",
}


@dataclass
class IncomingMessage:
    user_id: int
    first_name: str
    text: str
    has_image: bool
    mentions_bot: bool
    is_from_bot: bool
    chat_id: int


@dataclass
class Decision:
    respond: bool
    reason: str


def _is_trivial(text: str, has_image: bool) -> bool:
    if has_image:
        return False
    s = text.strip()
    if not s:
        return True
    if not any(ch.isalnum() for ch in s):     # emoji / punctuation only
        return True
    if s.lower() in TRIVIAL_WORDS:
        return True
    return False


def should_respond(msg: IncomingMessage, cfg: Config) -> Decision:
    if msg.is_from_bot:
        return Decision(False, "own message")
    if msg.chat_id != cfg.group_id:
        return Decision(False, "not the workshop group")
    if msg.mentions_bot:
        return Decision(True, "explicit mention")
    if msg.user_id == cfg.host_user_id:
        return Decision(False, "host message (teaching)")
    if _is_trivial(msg.text, msg.has_image):
        return Decision(False, "trivial message")
    return Decision(True, "attendee question")


class RateLimiter:
    def __init__(self, cooldown_seconds: float):
        self.cooldown = cooldown_seconds
        self._last: dict[int, float] = {}

    def allow(self, user_id: int, now: float) -> bool:
        last = self._last.get(user_id)
        if last is not None and now - last < self.cooldown:
            return False
        self._last[user_id] = now
        return True
