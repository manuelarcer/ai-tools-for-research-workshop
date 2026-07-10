import pytest
from unittest.mock import AsyncMock, MagicMock
from bot.claude_client import ClaudeClient, Answer, build_user_content
from bot.memory import RecentQA, AnsweredQ


def test_build_user_content_includes_memory_and_images():
    m = RecentQA()
    m.add(AnsweredQ("q", "r", 1001, 1.0))
    content = build_user_content("¿cómo instalo?", [b"\xff\xd8jpegbytes"], m)
    kinds = [b["type"] for b in content]
    assert "text" in kinds
    assert kinds.count("image") == 1
    img = next(b for b in content if b["type"] == "image")
    assert img["source"]["type"] == "base64"
    assert img["source"]["media_type"] == "image/jpeg"
    # question text present in some text block
    assert any("cómo instalo" in b["text"] for b in content if b["type"] == "text")


def test_build_user_content_includes_user_history_when_given():
    content = build_user_content("otra vez", [], RecentQA(), user_history="hist: intento previo")
    assert any("intento previo" in b["text"] for b in content if b["type"] == "text")


def test_build_user_content_omits_empty_user_history():
    content = build_user_content("hola", [], RecentQA())     # no user_history
    text_blocks = [b["text"] for b in content if b["type"] == "text"]
    assert text_blocks == ["Pregunta:\nhola"]                # only the question block


def _tool_response(answer, escalate):
    block = MagicMock()
    block.type = "tool_use"
    block.name = "submit_answer"
    block.input = {"answer": answer, "escalate": escalate}
    resp = MagicMock()
    resp.content = [block]
    return resp


@pytest.mark.asyncio
async def test_answer_parses_tool_output():
    client = ClaudeClient("k", "sonnet-x", "opus-x", system_blocks=[{"type": "text", "text": "s"}])
    client._client = MagicMock()
    client._client.messages = MagicMock()
    client._client.messages.create = AsyncMock(return_value=_tool_response("Ana: instala así", False))
    ans = await client.answer("¿cómo?", [], RecentQA())
    assert isinstance(ans, Answer)
    assert ans.text == "Ana: instala así"
    assert ans.escalate is False
    # called with the default (sonnet) model and forced tool
    kwargs = client._client.messages.create.call_args.kwargs
    assert kwargs["model"] == "sonnet-x"
    assert kwargs["tool_choice"]["name"] == "submit_answer"
    assert kwargs["system"] == [{"type": "text", "text": "s"}]


@pytest.mark.asyncio
async def test_answer_without_tool_block_escalates():
    block = MagicMock(); block.type = "text"; block.text = "no tool here"
    resp = MagicMock(); resp.content = [block]
    client = ClaudeClient("k", "sonnet-x", "opus-x", system_blocks=[{"type": "text", "text": "s"}])
    client._client = MagicMock()
    client._client.messages = MagicMock()
    client._client.messages.create = AsyncMock(return_value=resp)
    ans = await client.answer("¿algo?", [], RecentQA())
    assert ans.escalate is True
    assert ans.text                      # non-empty fallback, not blank


@pytest.mark.asyncio
async def test_escalate_uses_opus_and_returns_text():
    block = MagicMock(); block.type = "text"; block.text = "respuesta Opus"
    resp = MagicMock(); resp.content = [block]
    client = ClaudeClient("k", "sonnet-x", "opus-x", system_blocks=[{"type": "text", "text": "s"}])
    client._client = MagicMock()
    client._client.messages = MagicMock()
    client._client.messages.create = AsyncMock(return_value=resp)
    out = await client.escalate("¿pregunta difícil?", [], RecentQA())
    assert out == "respuesta Opus"
    kwargs = client._client.messages.create.call_args.kwargs
    assert kwargs["model"] == "opus-x"
    assert kwargs["system"] == [{"type": "text", "text": "s"}]
