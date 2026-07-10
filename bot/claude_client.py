from __future__ import annotations
import base64
import logging
from dataclasses import dataclass
from anthropic import AsyncAnthropic
from bot.memory import RecentQA

log = logging.getLogger(__name__)

_SUBMIT_TOOL = {
    "name": "submit_answer",
    "description": "Entrega la respuesta al estudiante e indica si debe escalarse a un modelo más potente.",
    "input_schema": {
        "type": "object",
        "properties": {
            "answer": {"type": "string", "description": "Respuesta en español para el grupo."},
            "escalate": {
                "type": "boolean",
                "description": (
                    "Por defecto SIEMPRE false: tú puedes responder casi todas las "
                    "preguntas del taller. Pon true SOLO como último recurso, cuando "
                    "de verdad no puedas dar una respuesta correcta y útil por ti mismo "
                    "(por ejemplo un problema muy especializado y ambiguo donde una "
                    "respuesta equivocada sería perjudicial). Ante cualquier duda, "
                    "responde tú mismo con false. Escalar es caro y lento."
                ),
            },
        },
        "required": ["answer", "escalate"],
    },
}
_MAX_TOKENS = 1024
_FALLBACK_ES = ("No pude generar una respuesta con el modelo base; "
                "lo intento con un modelo más potente.")


@dataclass
class Answer:
    text: str
    escalate: bool


def build_user_content(question_text: str, images: list[bytes], recent: RecentQA) -> list[dict]:
    content: list[dict] = []
    mem = recent.render_for_prompt()
    if mem:
        content.append({"type": "text", "text": mem})
    content.append({"type": "text", "text": f"Pregunta:\n{question_text}"})
    for raw in images:
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": base64.standard_b64encode(raw).decode("ascii"),
            },
        })
    return content


class ClaudeClient:
    def __init__(self, api_key: str, model_default: str, model_escalate: str, system_blocks: list[dict]):
        self._client = AsyncAnthropic(api_key=api_key)
        self.model_default = model_default
        self.model_escalate = model_escalate
        self.system_blocks = system_blocks

    async def answer(self, question_text: str, images: list[bytes], recent: RecentQA) -> Answer:
        content = build_user_content(question_text, images, recent)
        resp = await self._client.messages.create(
            model=self.model_default,
            max_tokens=_MAX_TOKENS,
            system=self.system_blocks,
            messages=[{"role": "user", "content": content}],
            tools=[_SUBMIT_TOOL],
            tool_choice={"type": "tool", "name": "submit_answer"},
        )
        for block in resp.content:
            if getattr(block, "type", None) == "tool_use" and block.name == "submit_answer":
                data = block.input
                return Answer(text=data["answer"], escalate=bool(data["escalate"]))
        # No submit_answer tool_use block -> recover by escalating to Opus.
        log.warning("No submit_answer tool_use block in Sonnet response; escalating.")
        return Answer(text=_FALLBACK_ES, escalate=True)

    async def escalate(self, question_text: str, images: list[bytes], recent: RecentQA) -> str:
        content = build_user_content(question_text, images, recent)
        resp = await self._client.messages.create(
            model=self.model_escalate,
            max_tokens=_MAX_TOKENS,
            system=self.system_blocks,
            messages=[{"role": "user", "content": content}],
        )
        return "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
