import asyncio
import pytest
from unittest.mock import AsyncMock
from bot.config import Config
from bot.gate import IncomingMessage, RateLimiter
from bot.memory import RecentQA
from bot.claude_client import Answer
from bot.handler import Handler

CFG = Config("t", "k", group_id=-100, host_user_id=42, cooldown_seconds=5.0)

def make(handler_client, sender, now=lambda: 100.0):
    return Handler(CFG, handler_client, RecentQA(), RateLimiter(5.0), sender, now_fn=now)

def imsg(**kw):
    base = dict(user_id=7, first_name="Ana", text="¿cómo?", has_image=False,
                mentions_bot=False, is_from_bot=False, chat_id=-100)
    base.update(kw); return IncomingMessage(**base)

@pytest.mark.asyncio
async def test_simple_answer_sends_and_remembers():
    client = AsyncMock()
    client.answer = AsyncMock(return_value=Answer("Ana: instala así", False))
    sender = AsyncMock(); sender.send = AsyncMock(return_value=555)
    h = make(client, sender)
    await h.handle(imsg(), source_message_id=200)
    sender.send.assert_awaited_once_with("Ana: instala así", 200)
    assert h.memory.recent()[-1].message_id == 555   # stored SENT id

@pytest.mark.asyncio
async def test_gated_message_does_nothing():
    client = AsyncMock(); sender = AsyncMock(); sender.send = AsyncMock()
    h = make(client, sender)
    await h.handle(imsg(is_from_bot=True), source_message_id=1)
    sender.send.assert_not_called()

@pytest.mark.asyncio
async def test_rate_limited_second_message_skipped():
    client = AsyncMock()
    client.answer = AsyncMock(return_value=Answer("Ana: x", False))
    sender = AsyncMock(); sender.send = AsyncMock(return_value=1)
    h = make(client, sender)   # now fixed at 100.0
    await h.handle(imsg(), 10)
    await h.handle(imsg(), 11)         # within cooldown -> skipped
    assert client.answer.await_count == 1

@pytest.mark.asyncio
async def test_escalation_sends_interim_then_opus_answer():
    client = AsyncMock()
    client.answer = AsyncMock(return_value=Answer("Ana: respuesta base", True))
    client.escalate = AsyncMock(return_value="Ana: respuesta Opus")
    sender = AsyncMock(); sender.send = AsyncMock(side_effect=[900, 901])
    h = make(client, sender)
    await h.handle(imsg(), source_message_id=300)
    await asyncio.gather(*h._tasks)          # let the background task finish
    texts = [c.args[0] for c in sender.send.await_args_list]
    assert "Opus" in texts[-1]               # final answer is the Opus one
    assert len(texts) == 2                    # interim + final
    client.escalate.assert_awaited_once()

@pytest.mark.asyncio
async def test_escalation_failure_falls_back_to_sonnet():
    client = AsyncMock()
    client.answer = AsyncMock(return_value=Answer("Ana: base", True))
    client.escalate = AsyncMock(side_effect=RuntimeError("opus down"))
    sender = AsyncMock(); sender.send = AsyncMock(side_effect=[900, 901])
    h = make(client, sender)
    await h.handle(imsg(), 300)
    await asyncio.gather(*h._tasks)
    assert sender.send.await_args_list[-1].args[0] == "Ana: base"   # fell back

@pytest.mark.asyncio
async def test_escalation_delivery_failure_is_contained():
    client = AsyncMock()
    client.answer = AsyncMock(return_value=Answer("Ana: base", True))
    client.escalate = AsyncMock(return_value="Ana: respuesta Opus")
    sender = AsyncMock()
    # interim send ok, final delivery raises
    sender.send = AsyncMock(side_effect=[900, RuntimeError("telegram down")])
    h = make(client, sender)
    await h.handle(imsg(), source_message_id=300)
    # must not raise even though final delivery failed inside the background task
    await asyncio.gather(*h._tasks)
    assert client.escalate.await_count == 1

@pytest.mark.asyncio
async def test_answer_call_failure_sends_error_note():
    client = AsyncMock()
    client.answer = AsyncMock(side_effect=RuntimeError("anthropic down"))
    sender = AsyncMock(); sender.send = AsyncMock(return_value=1)
    h = make(client, sender)
    await h.handle(imsg(), source_message_id=10)      # must not raise
    sender.send.assert_awaited_once()                  # Spanish error note posted
    assert h.memory.recent() == []                     # nothing remembered on failure

@pytest.mark.asyncio
async def test_direct_delivery_failure_is_contained():
    client = AsyncMock()
    client.answer = AsyncMock(return_value=Answer("Ana: x", False))
    sender = AsyncMock(); sender.send = AsyncMock(side_effect=RuntimeError("telegram down"))
    h = make(client, sender)
    await h.handle(imsg(), 10)                          # must not raise
