import asyncio
import pytest
from unittest.mock import AsyncMock
from bot.config import Config
from bot.gate import IncomingMessage, RateLimiter
from bot.memory import RecentQA
from bot.claude_client import Answer
from bot.handler import Handler
from bot.user_state import UserStates

CFG = Config("t", "k", group_id=-100, host_user_id=42, cooldown_seconds=5.0)

def make(handler_client, sender, now=lambda: 100.0, cfg=CFG, user_states=None):
    return Handler(cfg, handler_client, RecentQA(), RateLimiter(5.0), sender,
                   now_fn=now, user_states=user_states)

def imsg(**kw):
    base = dict(user_id=7, first_name="Ana", text="¿cómo?", has_image=False,
                mentions_bot=False, is_from_bot=False, chat_id=-100)
    base.update(kw); return IncomingMessage(**base)

@pytest.mark.asyncio
async def test_escalation_disabled_delivers_sonnet_answer_directly():
    # cfg with escalation off: even if Sonnet flags escalate, no Opus call, no interim
    cfg_off = Config("t", "k", group_id=-100, host_user_id=42, cooldown_seconds=5.0,
                     escalation_enabled=False)
    client = AsyncMock()
    client.answer = AsyncMock(return_value=Answer("Ana: respuesta base", True))  # escalate=True
    client.escalate = AsyncMock()
    sender = AsyncMock(); sender.send = AsyncMock(return_value=777)
    h = make(client, sender, cfg=cfg_off)
    await h.handle(imsg(), source_message_id=200)
    sender.send.assert_awaited_once_with("Ana: respuesta base", 200)   # Sonnet answer, once
    client.escalate.assert_not_awaited()                               # Opus never called
    assert not h._tasks                                                # no background task
    assert h.memory.recent()[-1].message_id == 777

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


# --- escalation ladder (Opus tiers + human handoff) ---

@pytest.mark.asyncio
async def test_users_prior_messages_passed_to_answer():
    client = AsyncMock()
    client.answer = AsyncMock(return_value=Answer("Ana: ok", False))
    sender = AsyncMock(); sender.send = AsyncMock(return_value=1)
    us = UserStates()
    us.get(7, now=100.0).messages.append("intento previo")
    h = make(client, sender, user_states=us)
    await h.handle(imsg(text="otra vez"), source_message_id=10)
    history_arg = client.answer.call_args.args[3]       # user_history is 4th positional
    assert "intento previo" in history_arg
    assert "otra vez" not in history_arg                # current msg not yet in history


@pytest.mark.asyncio
async def test_escalation_increments_opus_counter():
    client = AsyncMock()
    client.answer = AsyncMock(return_value=Answer("Ana: base", True))
    client.escalate = AsyncMock(return_value="Ana: opus")
    sender = AsyncMock(); sender.send = AsyncMock(side_effect=[900, 901])
    us = UserStates()
    h = make(client, sender, user_states=us)
    await h.handle(imsg(), source_message_id=10)
    await asyncio.gather(*h._tasks)
    assert us.get(7, now=100.0).opus_calls == 1


@pytest.mark.asyncio
async def test_ceiling_reached_hands_off_to_host():
    client = AsyncMock()
    client.answer = AsyncMock(return_value=Answer("Ana: base", True))   # still flags escalate
    client.escalate = AsyncMock()
    sender = AsyncMock(); sender.send = AsyncMock(side_effect=[900, 901])
    us = UserStates()
    us.get(7, now=100.0).opus_calls = 2                 # already hit the ceiling
    h = make(client, sender, user_states=us)
    await h.handle(imsg(), source_message_id=300)
    client.escalate.assert_not_awaited()               # no 3rd Opus call
    assert not h._tasks
    texts = [c.args[0] for c in sender.send.await_args_list]
    assert texts[0] == "Ana: base"                     # Sonnet answer delivered
    assert "tg://user?id=42" in texts[1]               # host pinged in handoff note
    assert us.get(7, now=100.0).handed_off is True


@pytest.mark.asyncio
async def test_after_handoff_only_answers_no_reping():
    client = AsyncMock()
    client.answer = AsyncMock(return_value=Answer("Ana: base", True))
    client.escalate = AsyncMock()
    sender = AsyncMock(); sender.send = AsyncMock(return_value=555)
    us = UserStates()
    st = us.get(7, now=100.0); st.opus_calls = 2; st.handed_off = True
    h = make(client, sender, user_states=us)
    await h.handle(imsg(), source_message_id=300)
    client.escalate.assert_not_awaited()
    sender.send.assert_awaited_once_with("Ana: base", 300)   # answer only, no ping

