from __future__ import annotations
import asyncio
import logging
import time
from typing import Protocol
from bot.config import Config
from bot.gate import IncomingMessage, should_respond, RateLimiter
from bot.memory import RecentQA, AnsweredQ
from bot.claude_client import ClaudeClient, Answer

log = logging.getLogger(__name__)

_INTERIM = ("{name}: buena pregunta, la escalo a un modelo más potente (Opus) "
            "y te respondo en un momento.")
_ERROR_ES = ("{name}: tuve un problema técnico al generar la respuesta. "
             "Por favor intenta de nuevo en un momento.")
_SUMMARY_LEN = 200


class Sender(Protocol):
    async def send(self, text: str, reply_to_message_id: int) -> int:
        ...


class Handler:
    def __init__(self, cfg: Config, client: ClaudeClient, memory: RecentQA,
                 rate_limiter: RateLimiter, sender: Sender, now_fn=time.monotonic):
        self.cfg = cfg
        self.client = client
        self.memory = memory
        self.rate_limiter = rate_limiter
        self.sender = sender
        self.now_fn = now_fn
        self._tasks: set[asyncio.Task] = set()

    async def _safe_send(self, text: str, reply_to_message_id: int) -> None:
        try:
            await self.sender.send(text, reply_to_message_id)
        except Exception:
            log.exception("Failed to send message to chat")

    async def handle(self, msg: IncomingMessage, source_message_id: int,
                     images: list[bytes] | None = None) -> None:
        images = images or []
        if not should_respond(msg, self.cfg).respond:
            return
        if not self.rate_limiter.allow(msg.user_id, self.now_fn()):
            return
        try:
            answer = await self.client.answer(msg.text, images, self.memory)
        except Exception:
            log.exception("Answer generation failed")
            await self._safe_send(_ERROR_ES.format(name=msg.first_name), source_message_id)
            return
        if answer.escalate:
            await self._safe_send(_INTERIM.format(name=msg.first_name), source_message_id)
            task = asyncio.create_task(
                self._finish_escalation(msg, source_message_id, images, answer))
            self._tasks.add(task)
            task.add_done_callback(self._tasks.discard)
        else:
            try:
                await self._deliver(msg, source_message_id, answer.text)
            except Exception:
                log.exception("Failed to deliver answer")

    async def _finish_escalation(self, msg: IncomingMessage, source_message_id: int,
                                 images: list[bytes], base: Answer) -> None:
        try:
            final = await self.client.escalate(msg.text, images, self.memory)
            if not final:
                final = base.text
        except Exception:
            log.exception("Opus escalation failed; falling back to Sonnet answer")
            final = base.text
        try:
            await self._deliver(msg, source_message_id, final)
        except Exception:
            log.exception("Failed to deliver escalated answer to chat")

    async def _deliver(self, msg: IncomingMessage, source_message_id: int, text: str) -> None:
        sent_id = await self.sender.send(text, source_message_id)
        self.memory.add(AnsweredQ(
            question=msg.text,
            answer_summary=text[:_SUMMARY_LEN],
            message_id=sent_id,
            timestamp=self.now_fn(),
        ))
