"""Per-user struggle tracking for the escalation ladder.

One record per Telegram user id holds their recent messages (so the model can
judge whether they keep asking the same unresolved question), how many Opus
escalations have happened, and whether the host has already been pinged. A
record resets when the user has been idle longer than the window, so a fresh
question later starts clean.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass, field

WINDOW_SECONDS = 20 * 60      # reset a user's record after this much idle time
MAX_HISTORY = 5               # recent messages kept per user for the model
MAX_OPUS_CALLS = 2            # hard ceiling before handing off to the host

_HISTORY_HEADER = (
    "Mensajes recientes de este MISMO usuario (para juzgar si sigue atascado en "
    "el mismo problema tras varios intentos):"
)


@dataclass
class UserState:
    messages: deque = field(default_factory=lambda: deque(maxlen=MAX_HISTORY))
    opus_calls: int = 0
    handed_off: bool = False
    last_activity: float = 0.0

    def render_history(self) -> str:
        """Render the user's prior messages for the prompt (\"\" if none)."""
        if not self.messages:
            return ""
        lines = [_HISTORY_HEADER]
        for i, text in enumerate(self.messages, 1):
            lines.append(f"{i}. {text}")
        return "\n".join(lines)


class UserStates:
    def __init__(self, window_seconds: float = WINDOW_SECONDS):
        self.window = window_seconds
        self._by_user: dict[int, UserState] = {}

    def get(self, user_id: int, now: float) -> UserState:
        """Return this user's record, resetting it if idle past the window.

        Refreshes ``last_activity`` to ``now`` so the record stays alive while
        the user is active. Callers mutate the returned object directly.
        """
        st = self._by_user.get(user_id)
        if st is None or (now - st.last_activity) > self.window:
            st = UserState()
            self._by_user[user_id] = st
        st.last_activity = now
        return st
