from __future__ import annotations
from collections import deque
from dataclasses import dataclass


@dataclass
class AnsweredQ:
    question: str
    answer_summary: str
    message_id: int
    timestamp: float


_HEADER = (
    "Preguntas respondidas recientemente (de más antigua a más reciente). "
    "Si la nueva pregunta es esencialmente un DUPLICADO de una muy reciente, "
    "NO la respondas de nuevo: indica que ya la respondiste y referencia el "
    "message_id para que el bot haga un reply-link. Si la respuesta previa quedó "
    "MUY ATRÁS (más de 4 mensajes), da un resumen corto y referencia el message_id.\n"
)


class RecentQA:
    def __init__(self, maxlen: int = 10):
        self._items: deque[AnsweredQ] = deque(maxlen=maxlen)

    def add(self, item: AnsweredQ) -> None:
        self._items.append(item)

    def recent(self) -> list[AnsweredQ]:
        return list(self._items)

    def render_for_prompt(self) -> str:
        if not self._items:
            return ""
        lines = [_HEADER]
        for i, a in enumerate(self._items, 1):
            lines.append(
                f"{i}. [message_id={a.message_id} ts={a.timestamp:.0f}] "
                f"P: {a.question} | R(resumen): {a.answer_summary}"
            )
        return "\n".join(lines)
