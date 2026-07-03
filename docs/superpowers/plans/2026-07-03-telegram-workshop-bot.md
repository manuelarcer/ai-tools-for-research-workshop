# Telegram Workshop Q&A Bot — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A single Python bot that watches one Telegram group and answers attendees' text/screenshot questions with Claude, in Spanish, grounded in this workshop repo.

**Architecture:** One long-polling `python-telegram-bot` process. Incoming group messages pass a pure trigger gate, then a handler builds a Claude request (cached workshop grounding + rolling recent-Q&A memory + text/image) and calls Sonnet 5. Sonnet returns a structured `{answer, escalate}`; on `escalate` the bot posts a short interim note and runs an Opus 4.8 call as a background task while continuing to answer others. Answers are sent as Telegram replies prefixed with the asker's first name.

**Tech Stack:** Python 3.11, `python-telegram-bot` v21+ (asyncio), `anthropic` SDK (AsyncAnthropic), `python-dotenv`, `pytest` + `pytest-asyncio`.

## Global Constraints

- Python 3.11 (repo has 3.11.10). Use `asyncio` throughout; `python-telegram-bot` is async-native.
- Default model id: `claude-sonnet-5`. Escalation model id: `claude-opus-4-8`. Never hardcode these — read from config.
- All bot-authored text to attendees is in **Spanish**, English technical terms preserved.
- The bot operates ONLY in the allowlisted `GROUP_ID`; ignore every other chat.
- Secrets come from `.env` (via `python-dotenv`); `.env` is gitignored, never committed. A committed `.env.example` documents the keys.
- Anthropic system prompt uses **prompt caching** (`cache_control: {type: "ephemeral"}`) on the large grounding block.
- New bot code lives under `bot/`. Do not restructure existing repo files.
- TDD: pure-logic units (config, gate, memory, grounding extraction, structured-answer parsing) get failing-test-first cycles. Transport wiring is verified manually against a private test group (Task 8).

---

## File Structure

- `bot/config.py` — `Config` dataclass + `Config.from_env(mapping)`. One responsibility: turn env vars into a validated config object.
- `bot/grounding.py` — load workshop files, strip the terminal-deck HTML to plain text, build the Anthropic system blocks (Spanish instructions + cached grounding).
- `bot/gate.py` — pure `should_respond(msg, cfg) -> Decision` trigger logic + `RateLimiter`.
- `bot/memory.py` — `RecentQA` rolling store of answered questions and its prompt rendering.
- `bot/claude_client.py` — build Anthropic request (grounding + memory + text/images), Sonnet structured answer, Opus escalation.
- `bot/handler.py` — orchestrate one message: gate → rate-limit → answer → send/reply → async escalation → memory update.
- `bot/bot.py` — entry point: wire `python-telegram-bot`, ID-helper mode, run long-polling.
- `bot/requirements.txt`, `bot/.env.example`, `bot/README.md` — deps, config template, setup/run instructions.
- `bot/tests/` — `test_config.py`, `test_gate.py`, `test_memory.py`, `test_grounding.py`, `test_claude_client.py`, `test_handler.py`.
- `.gitignore` — add `.env`, `__pycache__/`, `.pytest_cache/`.

---

### Task 1: Project scaffolding, dependencies, config

**Files:**
- Create: `bot/requirements.txt`, `bot/.env.example`, `bot/__init__.py`, `bot/tests/__init__.py`
- Create: `bot/config.py`
- Test: `bot/tests/test_config.py`
- Modify: `.gitignore` (append ignores)

**Interfaces:**
- Consumes: nothing.
- Produces: `Config` dataclass with fields `telegram_token: str`, `anthropic_api_key: str`, `group_id: int`, `host_user_id: int`, `model_default: str`, `model_escalate: str`, `cooldown_seconds: float`; classmethod `Config.from_env(env: Mapping[str, str]) -> Config` that raises `KeyError` for a missing required key and applies defaults for models/cooldown.

- [ ] **Step 1: Create dependency and env files**

`bot/requirements.txt`:
```
python-telegram-bot>=21,<22
anthropic>=0.40
python-dotenv>=1.0
pytest>=8.0
pytest-asyncio>=0.23
```

`bot/.env.example`:
```
# Bot token from @BotFather
TELEGRAM_TOKEN=123456:ABC-your-token-here
# Anthropic API key
ANTHROPIC_API_KEY=sk-ant-...
# Single chat id of the workshop group (a negative integer). NOT attendee ids.
GROUP_ID=-1001234567890
# Your own Telegram user id (so the bot knows the teacher)
HOST_USER_ID=987654321
# Models (defaults shown; usually leave as-is)
MODEL_DEFAULT=claude-sonnet-5
MODEL_ESCALATE=claude-opus-4-8
# Per-user cooldown in seconds
COOLDOWN_SECONDS=8
```

Create empty `bot/__init__.py` and `bot/tests/__init__.py`.

- [ ] **Step 2: Append to `.gitignore`**

Add these lines to the repo-root `.gitignore`:
```
.env
__pycache__/
.pytest_cache/
```

- [ ] **Step 3: Write the failing test**

`bot/tests/test_config.py`:
```python
import pytest
from bot.config import Config

BASE = {
    "TELEGRAM_TOKEN": "tok",
    "ANTHROPIC_API_KEY": "key",
    "GROUP_ID": "-100999",
    "HOST_USER_ID": "42",
}

def test_from_env_parses_types_and_defaults():
    cfg = Config.from_env(BASE)
    assert cfg.telegram_token == "tok"
    assert cfg.group_id == -100999          # int, not str
    assert cfg.host_user_id == 42
    assert cfg.model_default == "claude-sonnet-5"
    assert cfg.model_escalate == "claude-opus-4-8"
    assert cfg.cooldown_seconds == 8.0

def test_from_env_overrides_defaults():
    env = {**BASE, "MODEL_DEFAULT": "x", "COOLDOWN_SECONDS": "2.5"}
    cfg = Config.from_env(env)
    assert cfg.model_default == "x"
    assert cfg.cooldown_seconds == 2.5

def test_missing_required_key_raises():
    env = dict(BASE)
    del env["GROUP_ID"]
    with pytest.raises(KeyError):
        Config.from_env(env)
```

- [ ] **Step 4: Run test to verify it fails**

Run: `cd bot && python -m pytest tests/test_config.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'bot.config'` (run from repo root: `python -m pytest bot/tests/test_config.py -v`).

Note: run pytest from the **repo root** so `bot` is importable as a package: `python -m pytest bot/tests/ -v`.

- [ ] **Step 5: Write minimal implementation**

`bot/config.py`:
```python
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
```

- [ ] **Step 6: Run test to verify it passes**

Run: `python -m pytest bot/tests/test_config.py -v`
Expected: PASS (3 passed).

- [ ] **Step 7: Commit**

```bash
git add bot/requirements.txt bot/.env.example bot/__init__.py bot/tests/__init__.py bot/config.py bot/tests/test_config.py .gitignore
git commit -m "feat: bot scaffolding and config loader"
```

---

### Task 2: Grounding loader and system prompt

**Files:**
- Create: `bot/grounding.py`
- Test: `bot/tests/test_grounding.py`

**Interfaces:**
- Consumes: nothing (reads files from disk given a repo root `Path`).
- Produces:
  - `extract_slide_text(html: str) -> str` — HTML to whitespace-collapsed plain text.
  - `load_grounding(repo_root: Path) -> str` — concatenation of grounding files (each under a `## <path>` header) plus extracted slide text; missing files are skipped, not fatal.
  - `SPANISH_INSTRUCTIONS: str` — the behavior/persona block.
  - `build_system(grounding_text: str) -> list[dict]` — Anthropic `system` blocks: `[{type:text, text:SPANISH_INSTRUCTIONS}, {type:text, text:grounding_text, cache_control:{type:ephemeral}}]`.

- [ ] **Step 1: Write the failing test**

`bot/tests/test_grounding.py`:
```python
from pathlib import Path
from bot.grounding import extract_slide_text, load_grounding, build_system, SPANISH_INSTRUCTIONS


def test_extract_slide_text_strips_tags_and_scripts():
    html = "<html><head><style>.x{color:red}</style><script>var a=1</script>"\
           "</head><body><h1>Hola</h1><p>Mundo  &amp; más</p></body></html>"
    out = extract_slide_text(html)
    assert "Hola" in out
    assert "Mundo & más" in out
    assert "color:red" not in out
    assert "var a=1" not in out
    assert "<" not in out

def test_load_grounding_concatenates_existing_and_skips_missing(tmp_path):
    (tmp_path / "README.md").write_text("readme body", encoding="utf-8")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "workshop-plan.md").write_text("plan body", encoding="utf-8")
    text = load_grounding(tmp_path)
    assert "readme body" in text
    assert "plan body" in text
    assert "## README.md" in text          # header present
    # missing files (exercise, deck) simply absent, no crash
    assert "exercise" not in text or "beer" not in text

def test_build_system_marks_grounding_cacheable():
    blocks = build_system("GROUNDING")
    assert blocks[0]["text"] == SPANISH_INSTRUCTIONS
    assert blocks[1]["text"] == "GROUNDING"
    assert blocks[1]["cache_control"] == {"type": "ephemeral"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest bot/tests/test_grounding.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'bot.grounding'`.

- [ ] **Step 3: Write minimal implementation**

`bot/grounding.py`:
```python
from __future__ import annotations
import html as html_lib
import re
from pathlib import Path

# Files pulled into the grounding context, relative to repo root.
GROUNDING_FILES = [
    "README.md",
    "docs/workshop-plan.md",
    "exercise/beer-lambert/README.md",
    "exercise/beer-lambert/SKILL.md.template",
    "slide-deck-handoff.md",
]
SLIDE_HTML = "taller-ia-alt3-terminal.html"

SPANISH_INSTRUCTIONS = (
    "Eres un asistente del taller 'Inteligencia Artificial para la Investigación'. "
    "Respondes preguntas de estudiantes y personal de investigación durante el taller en vivo.\n"
    "Reglas:\n"
    "- Responde en ESPAÑOL, conservando términos técnicos en inglés cuando corresponda.\n"
    "- Sé conciso: respuestas de tamaño chat, directas y accionables.\n"
    "- Mantén el hilo del taller: la IA amplifica el juicio del investigador, no lo reemplaza; "
    "recuerda verificar fuentes y resultados.\n"
    "- Basa tus respuestas en el material del taller que aparece abajo; si algo no está cubierto, dilo.\n"
    "- Si te comparten una captura de pantalla (error, terminal, UI), interprétala y ayuda a resolver.\n"
    "- Comienza SIEMPRE tu respuesta con el nombre de quien pregunta (te lo indican en el mensaje)."
)

_TAG_RE = re.compile(r"<[^>]+>")
_DROP_RE = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
_WS_RE = re.compile(r"\s+")


def extract_slide_text(html: str) -> str:
    no_blocks = _DROP_RE.sub(" ", html)
    no_tags = _TAG_RE.sub(" ", no_blocks)
    unescaped = html_lib.unescape(no_tags)
    return _WS_RE.sub(" ", unescaped).strip()


def load_grounding(repo_root: Path) -> str:
    parts: list[str] = []
    for rel in GROUNDING_FILES:
        p = repo_root / rel
        if p.exists():
            parts.append(f"## {rel}\n{p.read_text(encoding='utf-8')}")
    deck = repo_root / SLIDE_HTML
    if deck.exists():
        parts.append(f"## {SLIDE_HTML} (texto de las diapositivas)\n"
                     + extract_slide_text(deck.read_text(encoding="utf-8")))
    return "\n\n".join(parts)


def build_system(grounding_text: str) -> list[dict]:
    return [
        {"type": "text", "text": SPANISH_INSTRUCTIONS},
        {"type": "text", "text": grounding_text, "cache_control": {"type": "ephemeral"}},
    ]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest bot/tests/test_grounding.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add bot/grounding.py bot/tests/test_grounding.py
git commit -m "feat: workshop grounding loader and system prompt"
```

---

### Task 3: Trigger gate and rate limiter

**Files:**
- Create: `bot/gate.py`
- Test: `bot/tests/test_gate.py`

**Interfaces:**
- Consumes: `Config` (Task 1) — uses `group_id`, `host_user_id`, `cooldown_seconds`.
- Produces:
  - `@dataclass IncomingMessage` with: `user_id: int`, `first_name: str`, `text: str`, `has_image: bool`, `mentions_bot: bool`, `is_from_bot: bool`, `chat_id: int`.
  - `@dataclass Decision` with: `respond: bool`, `reason: str`.
  - `should_respond(msg: IncomingMessage, cfg: Config) -> Decision` — pure.
  - `RateLimiter(cooldown_seconds: float)` with `allow(user_id: int, now: float) -> bool`.

- [ ] **Step 1: Write the failing test**

`bot/tests/test_gate.py`:
```python
from bot.config import Config
from bot.gate import IncomingMessage, should_respond, RateLimiter

CFG = Config(telegram_token="t", anthropic_api_key="k",
             group_id=-100, host_user_id=42, cooldown_seconds=5.0)

def msg(**kw):
    base = dict(user_id=7, first_name="Ana", text="¿cómo instalo opencode?",
                has_image=False, mentions_bot=False, is_from_bot=False, chat_id=-100)
    base.update(kw)
    return IncomingMessage(**base)

def test_answers_normal_attendee_question():
    assert should_respond(msg(), CFG).respond is True

def test_ignores_other_chats():
    assert should_respond(msg(chat_id=-999), CFG).respond is False

def test_ignores_own_messages():
    assert should_respond(msg(is_from_bot=True), CFG).respond is False

def test_ignores_host_by_default():
    assert should_respond(msg(user_id=42), CFG).respond is False

def test_answers_host_when_mentioned():
    assert should_respond(msg(user_id=42, mentions_bot=True), CFG).respond is True

def test_ignores_trivial_ack():
    assert should_respond(msg(text="gracias")).respond is False if False else \
        should_respond(msg(text="gracias"), CFG).respond is False

def test_ignores_emoji_only():
    assert should_respond(msg(text="👍👍"), CFG).respond is False

def test_image_is_never_trivial():
    assert should_respond(msg(text="", has_image=True), CFG).respond is True

def test_mention_beats_trivial():
    assert should_respond(msg(text="ok", mentions_bot=True), CFG).respond is True

def test_rate_limiter_blocks_within_cooldown():
    rl = RateLimiter(5.0)
    assert rl.allow(7, now=100.0) is True
    assert rl.allow(7, now=102.0) is False    # within cooldown
    assert rl.allow(7, now=106.0) is True     # cooldown elapsed
    assert rl.allow(9, now=102.0) is True     # different user
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest bot/tests/test_gate.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'bot.gate'`.

- [ ] **Step 3: Write minimal implementation**

`bot/gate.py`:
```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest bot/tests/test_gate.py -v`
Expected: PASS (10 passed).

- [ ] **Step 5: Commit**

```bash
git add bot/gate.py bot/tests/test_gate.py
git commit -m "feat: trigger gate and per-user rate limiter"
```

---

### Task 4: Recent-Q&A memory

**Files:**
- Create: `bot/memory.py`
- Test: `bot/tests/test_memory.py`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `@dataclass AnsweredQ` with: `question: str`, `answer_summary: str`, `message_id: int`, `timestamp: float`.
  - `RecentQA(maxlen: int = 10)` with `add(item: AnsweredQ) -> None`, `recent() -> list[AnsweredQ]` (oldest→newest), `render_for_prompt() -> str`.
  - `render_for_prompt()` returns `""` when empty; otherwise a numbered list including each question, its `message_id`, and `timestamp`, with a header instructing the model how to dedup (repeat-recently → point to `message_id`; buried >4 back → short recap + `message_id`).

- [ ] **Step 1: Write the failing test**

`bot/tests/test_memory.py`:
```python
from bot.memory import AnsweredQ, RecentQA

def q(i):
    return AnsweredQ(question=f"pregunta {i}", answer_summary=f"resumen {i}",
                     message_id=1000 + i, timestamp=float(i))

def test_rolling_cap_keeps_newest():
    m = RecentQA(maxlen=3)
    for i in range(5):
        m.add(q(i))
    ids = [a.message_id for a in m.recent()]
    assert ids == [1002, 1003, 1004]          # oldest dropped, order preserved

def test_render_empty_is_blank():
    assert RecentQA().render_for_prompt() == ""

def test_render_includes_question_and_message_id():
    m = RecentQA()
    m.add(q(1))
    out = m.render_for_prompt()
    assert "pregunta 1" in out
    assert "1001" in out                      # message_id referenced
    assert "reply" in out.lower() or "responder" in out.lower()  # dedup guidance present
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest bot/tests/test_memory.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'bot.memory'`.

- [ ] **Step 3: Write minimal implementation**

`bot/memory.py`:
```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest bot/tests/test_memory.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add bot/memory.py bot/tests/test_memory.py
git commit -m "feat: rolling recent-Q&A memory for dedup"
```

---

### Task 5: Claude client (Sonnet answer + Opus escalation)

**Files:**
- Create: `bot/claude_client.py`
- Test: `bot/tests/test_claude_client.py`

**Interfaces:**
- Consumes: `RecentQA` (Task 4), system blocks from `build_system` (Task 2).
- Produces:
  - `@dataclass Answer` with `text: str`, `escalate: bool`.
  - `build_user_content(question_text: str, images: list[bytes], recent: RecentQA) -> list[dict]` — Anthropic user-content blocks: recent-memory text block (if any) + question text block + one base64 image block per image (media_type `image/jpeg`).
  - `class ClaudeClient(api_key, model_default, model_escalate, system_blocks)` with:
    - `async answer(question_text, images, recent) -> Answer` — Sonnet call, forced `submit_answer` tool, returns parsed `Answer`.
    - `async escalate(question_text, images, recent) -> str` — Opus call, plain text.
  - Uses `anthropic.AsyncAnthropic`. The `submit_answer` tool schema: `{answer: string, escalate: boolean}`, `tool_choice={"type":"tool","name":"submit_answer"}`.

- [ ] **Step 1: Write the failing test** (mocks the Anthropic client — no network)

`bot/tests/test_claude_client.py`:
```python
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
    assert client._client.messages.create.call_args.kwargs["model"] == "opus-x"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest bot/tests/test_claude_client.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'bot.claude_client'`.

- [ ] **Step 3: Write minimal implementation**

`bot/claude_client.py`:
```python
from __future__ import annotations
import base64
from dataclasses import dataclass
from anthropic import AsyncAnthropic
from bot.memory import RecentQA

_SUBMIT_TOOL = {
    "name": "submit_answer",
    "description": "Entrega la respuesta al estudiante e indica si debe escalarse a un modelo más potente.",
    "input_schema": {
        "type": "object",
        "properties": {
            "answer": {"type": "string", "description": "Respuesta en español para el grupo."},
            "escalate": {
                "type": "boolean",
                "description": "true si la pregunta excede tu confianza y conviene un modelo más potente.",
            },
        },
        "required": ["answer", "escalate"],
    },
}
_MAX_TOKENS = 1024


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
        # Defensive fallback: no tool block -> treat as non-escalated empty
        return Answer(text="", escalate=False)

    async def escalate(self, question_text: str, images: list[bytes], recent: RecentQA) -> str:
        content = build_user_content(question_text, images, recent)
        resp = await self._client.messages.create(
            model=self.model_escalate,
            max_tokens=_MAX_TOKENS,
            system=self.system_blocks,
            messages=[{"role": "user", "content": content}],
        )
        return "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest bot/tests/test_claude_client.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add bot/claude_client.py bot/tests/test_claude_client.py
git commit -m "feat: Claude client with Sonnet answer and Opus escalation"
```

---

### Task 6: Handler orchestration (with async escalation)

**Files:**
- Create: `bot/handler.py`
- Test: `bot/tests/test_handler.py`

**Interfaces:**
- Consumes: `Config`, `should_respond`/`IncomingMessage` (Task 3), `RateLimiter` (Task 3), `RecentQA`/`AnsweredQ` (Task 4), `ClaudeClient`/`Answer` (Task 5).
- Produces:
  - `class Sender(Protocol)` — `async send(text: str, reply_to_message_id: int) -> int` returns the sent message's id.
  - `class Handler(cfg, client, memory, rate_limiter, sender, now_fn=time.monotonic)` with `async handle(msg: IncomingMessage, source_message_id: int) -> None`.
  - Behavior: gate → rate-limit (uses `now_fn()`); on non-escalated answer, `sender.send(answer.text, source_message_id)`, then `memory.add(...)` with the SENT message id; on escalated answer, send the interim note, spawn `asyncio.create_task` running `client.escalate(...)` then `sender.send(final, source_message_id)` and `memory.add(...)`. Escalation task must catch exceptions and fall back to sending the Sonnet `answer.text`.
  - Expose the spawned task via `self._tasks: set` so tests can await it.

- [ ] **Step 1: Write the failing test**

`bot/tests/test_handler.py`:
```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest bot/tests/test_handler.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'bot.handler'`.

- [ ] **Step 3: Write minimal implementation**

`bot/handler.py`:
```python
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

    async def handle(self, msg: IncomingMessage, source_message_id: int,
                     images: list[bytes] | None = None) -> None:
        images = images or []
        if not should_respond(msg, self.cfg).respond:
            return
        if not self.rate_limiter.allow(msg.user_id, self.now_fn()):
            return
        answer = await self.client.answer(msg.text, images, self.memory)
        if answer.escalate:
            await self.sender.send(_INTERIM.format(name=msg.first_name), source_message_id)
            task = asyncio.create_task(
                self._finish_escalation(msg, source_message_id, images, answer))
            self._tasks.add(task)
            task.add_done_callback(self._tasks.discard)
        else:
            await self._deliver(msg, source_message_id, answer.text)

    async def _finish_escalation(self, msg: IncomingMessage, source_message_id: int,
                                 images: list[bytes], base: Answer) -> None:
        try:
            final = await self.client.escalate(msg.text, images, self.memory)
            if not final:
                final = base.text
        except Exception:
            log.exception("Opus escalation failed; falling back to Sonnet answer")
            final = base.text
        await self._deliver(msg, source_message_id, final)

    async def _deliver(self, msg: IncomingMessage, source_message_id: int, text: str) -> None:
        sent_id = await self.sender.send(text, source_message_id)
        self.memory.add(AnsweredQ(
            question=msg.text,
            answer_summary=text[:_SUMMARY_LEN],
            message_id=sent_id,
            timestamp=self.now_fn(),
        ))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest bot/tests/test_handler.py -v`
Expected: PASS (5 passed).

- [ ] **Step 5: Run the full suite**

Run: `python -m pytest bot/tests/ -v`
Expected: PASS (all tasks 1–6 green).

- [ ] **Step 6: Commit**

```bash
git add bot/handler.py bot/tests/test_handler.py
git commit -m "feat: message handler with async Opus escalation and fallback"
```

---

### Task 7: Telegram transport and entry point

**Files:**
- Create: `bot/bot.py`
- (No unit test — this is the integration wiring; verified manually in Task 8.)

**Interfaces:**
- Consumes: everything above.
- Produces: runnable `python -m bot.bot` (long-polling) and `python -m bot.bot --print-ids` (ID-helper mode that logs `chat_id`/`user_id`/`first_name` of every incoming message so the host can capture `GROUP_ID` and `HOST_USER_ID`).
- Behavior:
  - On start: load `.env`, build `Config`, `load_grounding(repo_root)`, `build_system(...)`, construct `ClaudeClient`, `RecentQA`, `RateLimiter`, `Handler`.
  - Message handler: convert a Telegram `Update` into `IncomingMessage` + downloaded image bytes; detect mention by bot username or reply-to-bot; call `Handler.handle`.
  - `Sender` implementation posts via `context.bot.send_message(chat_id, text, reply_to_message_id=...)` and returns `message_id`.

- [ ] **Step 1: Write the entry point**

`bot/bot.py`:
```python
from __future__ import annotations
import argparse
import logging
import sys
from pathlib import Path
from dotenv import dotenv_values
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

from bot.config import Config
from bot.grounding import load_grounding, build_system
from bot.claude_client import ClaudeClient
from bot.gate import IncomingMessage, RateLimiter
from bot.memory import RecentQA
from bot.handler import Handler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("bot")

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_config() -> Config:
    env = {**dotenv_values(REPO_ROOT / ".env"), **dotenv_values(REPO_ROOT / "bot" / ".env")}
    if not env:
        log.error("No .env found. Copy bot/.env.example to .env and fill it in.")
        sys.exit(1)
    return Config.from_env(env)


async def _print_ids(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    m = update.effective_message
    if m and update.effective_user:
        log.info("chat_id=%s user_id=%s name=%s text=%r",
                 m.chat_id, update.effective_user.id, update.effective_user.first_name, m.text)


def _build_handler(cfg: Config) -> Handler:
    grounding = load_grounding(REPO_ROOT)
    client = ClaudeClient(cfg.anthropic_api_key, cfg.model_default, cfg.model_escalate,
                          build_system(grounding))
    return Handler(cfg, client, RecentQA(), RateLimiter(cfg.cooldown_seconds), sender=None)  # sender set per-update


async def _on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cfg: Config = context.application.bot_data["cfg"]
    handler: Handler = context.application.bot_data["handler"]
    tg_msg = update.effective_message
    user = update.effective_user
    if tg_msg is None or user is None:
        return

    bot_username = (context.bot.username or "").lower()
    text = tg_msg.text or tg_msg.caption or ""
    mentions_bot = (
        bool(bot_username) and f"@{bot_username}" in text.lower()
    ) or (
        tg_msg.reply_to_message is not None
        and tg_msg.reply_to_message.from_user is not None
        and tg_msg.reply_to_message.from_user.id == context.bot.id
    )

    images: list[bytes] = []
    if tg_msg.photo:
        photo = tg_msg.photo[-1]            # largest size
        tg_file = await context.bot.get_file(photo.file_id)
        images.append(bytes(await tg_file.download_as_bytearray()))

    imsg = IncomingMessage(
        user_id=user.id,
        first_name=user.first_name or "amig@",
        text=text,
        has_image=bool(images),
        mentions_bot=mentions_bot,
        is_from_bot=bool(user.is_bot),
        chat_id=tg_msg.chat_id,
    )

    async def send(reply_text: str, reply_to_message_id: int) -> int:
        sent = await context.bot.send_message(
            chat_id=tg_msg.chat_id, text=reply_text, reply_to_message_id=reply_to_message_id)
        return sent.message_id

    handler.sender = _CallableSender(send)
    await handler.handle(imsg, source_message_id=tg_msg.message_id, images=images)


class _CallableSender:
    def __init__(self, fn):
        self._fn = fn
    async def send(self, text: str, reply_to_message_id: int) -> int:
        return await self._fn(text, reply_to_message_id)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--print-ids", action="store_true",
                        help="Log chat_id/user_id of every message and exit-less run (for setup).")
    args = parser.parse_args()

    cfg = _load_config()
    app = Application.builder().token(cfg.telegram_token).build()

    if args.print_ids:
        app.add_handler(MessageHandler(filters.ALL, _print_ids))
        log.info("ID helper mode: send a message in your group. Ctrl-C to stop.")
        app.run_polling()
        return

    handler = _build_handler(cfg)
    app.bot_data["cfg"] = cfg
    app.bot_data["handler"] = handler
    app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, _on_message))
    log.info("Bot running. Group allowlist=%s host=%s", cfg.group_id, cfg.host_user_id)
    app.run_polling()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Smoke-check it imports and parses args (no token needed)**

Run: `python -c "import bot.bot as b; b.argparse and print('import ok')"`
Expected: prints `import ok` (verifies no syntax/import errors; does not start polling).

- [ ] **Step 3: Commit**

```bash
git add bot/bot.py
git commit -m "feat: Telegram transport, entry point, and --print-ids setup mode"
```

---

### Task 8: Setup docs and manual integration verification

**Files:**
- Create: `bot/README.md`

**Interfaces:**
- Consumes: everything. Produces: human setup instructions + a manual test checklist. No automated test.

- [ ] **Step 1: Write `bot/README.md`**

````markdown
# Workshop Q&A Bot (Telegram)

Answers attendees' text/screenshot questions during the "Inteligencia Artificial
para la Investigación" workshop, in Spanish, grounded in this repo.

## One-time setup

1. **Create the bot:** message [@BotFather](https://t.me/BotFather) → `/newbot`,
   copy the token. Then `/setprivacy` → **Disable** (so the bot can read group messages).
2. **Install deps** (from repo root):
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r bot/requirements.txt
   ```
3. **Config:** `cp bot/.env.example .env` and fill `TELEGRAM_TOKEN` and `ANTHROPIC_API_KEY`.
4. **Get the IDs:** create your workshop group, add the bot, then run:
   ```bash
   python -m bot.bot --print-ids
   ```
   Send a message in the group. The log prints `chat_id=` (that's `GROUP_ID`) and,
   from your own message, `user_id=` (that's `HOST_USER_ID`). Put both in `.env`. Ctrl-C.

## Run (during the workshop)

```bash
python -m bot.bot
```

Attendees just join the group (share a QR/invite link) and post questions or screenshots.

## Manual test checklist (run against a PRIVATE test group before the workshop)
- [ ] Attendee text question → bot replies in Spanish, prefixed with the name.
- [ ] Attendee posts a screenshot (e.g., a terminal error) → bot interprets it.
- [ ] Post "gracias" / an emoji → bot stays silent.
- [ ] Post as the host (you) without naming the bot → bot stays silent.
- [ ] @-mention the bot as the host → bot replies.
- [ ] Ask a hard/out-of-scope question → bot posts the "escalo a Opus" note, then a fuller answer.
- [ ] Ask the same question twice quickly → second time the bot points back to the first answer.
- [ ] Spam several messages fast from one account → rate limit throttles.
````

- [ ] **Step 2: Full suite green**

Run: `python -m pytest bot/tests/ -v`
Expected: PASS (all unit tests across tasks 1–6).

- [ ] **Step 3: Commit**

```bash
git add bot/README.md
git commit -m "docs: bot setup guide and manual test checklist"
```

- [ ] **Step 4: Manual integration run (host, pre-workshop)**

Follow `bot/README.md` against a private test group and walk the checklist. This is a
human verification step — not automated. Record any failures as new tasks.

---

## Self-Review

**Spec coverage:**
- §3 architecture (single script, long-polling, bare API) → Tasks 1–7. ✓
- §4 trigger rules (own/trivial/host/mention/attendee) → Task 3 `should_respond`; rate limit → Task 3 `RateLimiter` + Task 6 wiring. ✓
- §5 Sonnet default + async Opus escalation + grounding + caching + images + recent-memory dedup → Tasks 2, 4, 5, 6. ✓
- §6 reply + first-name prefix → Spanish instruction (Task 2) prefixes the name; transport sends as reply (Task 7). ✓
- §7 config keys → Task 1 `.env.example` + `Config`. ✓
- §8 setup/run + ID capture → Task 7 `--print-ids` + Task 8 README. ✓
- §9 error handling (retry/never crash, escalation fallback, no posting outside group) → Task 6 fallback, Task 3 group gate. Note: per-call retry/backoff is delegated to the Anthropic SDK's built-in retries (default) — acceptable for a one-off workshop; documented here rather than hand-rolled.
- §10 testing (unit for pure logic, manual integration) → Tasks 1–6 unit tests, Task 8 checklist. ✓
- §11 out-of-scope items → none implemented. ✓

**Placeholder scan:** No TBD/TODO in code steps; all code blocks complete.

**Type consistency:** `IncomingMessage`, `Decision`, `Answer`, `AnsweredQ`, `Config`, `RecentQA.add/recent/render_for_prompt`, `ClaudeClient.answer/escalate`, `Handler.handle`, `Sender.send` names are consistent across Tasks 3–7. `Handler.handle(msg, source_message_id, images)` signature matches its Task 7 caller.
