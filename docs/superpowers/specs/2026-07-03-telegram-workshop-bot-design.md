# Telegram Workshop Q&A Bot — Design

**Date:** 2026-07-03
**Project:** "Inteligencia Artificial para la Investigación" — live workshop, university in Mexico, mixed grad-student/research-staff audience.
**Goal:** A Telegram group where attendees post questions and screenshots during the workshop, and a Claude-powered bot answers them — in Spanish, grounded in the workshop material — with the lowest possible setup friction for both attendees and the host.

---

## 1. One-line summary

A single Python script (`python-telegram-bot` + Anthropic SDK) runs from the host's laptop, watches one Telegram group, and answers attendees' text/image questions with Claude, grounded in this repo's workshop content.

## 2. Success criteria

- An attendee joins the group via one QR/link and can ask a question or paste a screenshot with no further setup.
- The host's setup is: get a bot token, fill a `.env`, run `python bot.py`.
- The bot answers attendees' questions in Spanish, consistent with what the workshop taught (same tools, same exercise, same framing).
- The bot understands screenshots (errors, terminal output, UI).
- Group stays readable: no answering trivial chatter, no spam, no duplicate answers to the same question.

## 3. Architecture

**Chosen approach:** single Python script, long-polling, bare Anthropic Messages API (not the Agent SDK). Runs in a terminal on the host's laptop during the session.

Rejected alternatives:
- *Claude Agent SDK bot* — lets the bot read files on demand / run tools, but adds moving parts and latency. Overkill for pure Q&A. Revisit only if the bot later needs to *do* things, not just answer.
- *No-code (n8n/Make)* — the custom logic (image handling, dedup, model escalation) is exactly what these tools make awkward.

### Components

1. **Telegram transport** (`python-telegram-bot`, long-polling)
   - Bot added to the workshop group; **privacy mode OFF** so it receives all group messages.
   - Only operates in the allowlisted `GROUP_ID`; ignores DMs and other chats.

2. **Trigger / gate logic** — decides whether a given message deserves a reply.

3. **Context builder** — assembles the Claude request: cached workshop grounding + rolling recent-Q&A memory + the current message (text and/or image).

4. **Claude client** — Sonnet 5 by default; escalates to Opus 4.8 when the answer flags low confidence.

5. **Response sender** — posts the answer to the group as a Telegram *reply* to the asker's message; prefixes with the asker's first name.

6. **Recent-Q&A memory** — in-memory rolling list of the last ~10 answered questions (text, timestamp, Telegram message ID) used for dedup.

## 4. Behavior rules (the trigger gate)

Evaluated per incoming group message:

- **Ignore** the bot's own messages.
- **Ignore trivial messages:** emoji-only, stickers, or one-word acknowledgements ("gracias", "ok", "listo").
- **Host messages** (`from_user.id == HOST_USER_ID`): ignored **by default** (the host is teaching, not asking) **unless** the message @-mentions or names the bot → then answer immediately. Host's own answers to attendees are treated as *complementary* to the bot's; no suppression, no grace delay.
- **Attendee message** (text and/or image, non-trivial): **answer immediately** (no grace delay).
- **Explicit summon:** anyone @-mentioning or naming the bot → answer.
- **Rate limit:** light per-user cooldown (e.g., one in-flight request per user + short cooldown) so no single person can spam the API.

## 5. The Claude call

- **Default model:** Claude Sonnet 5 (`claude-sonnet-5`) — fast, cheap, strong vision, right for live Q&A.
- **Escalation (asynchronous):** the request asks Claude to return a structured result: `{ answer, escalate }`. If `escalate` is true (question beyond confident scope), the bot does **not** block:
  1. It posts a short interim reply to the asker — e.g., *"María: buena pregunta, la escalo a un modelo más potente (Opus) y te respondo en un momento."*
  2. It fires the **Opus 4.8** (`claude-opus-4-8`) call as a background task (`asyncio.create_task`).
  3. The main loop **keeps answering other attendees' questions** while Opus works.
  4. When Opus returns, the bot posts the full answer as a Telegram **reply to the original question** (so it threads correctly even if the chat has moved on).
  - No separate triage call — the escalation judgment rides along with the first Sonnet answer, so Opus only fires on genuinely hard questions. No manual override command.
- **Grounding (system prompt):** at startup, load and concatenate into the system prompt:
  - `README.md`
  - `exercise/` contents (the opencode build + Beer-Lambert exercise)
  - The slide text extracted from `taller-ia-alt3-terminal.html` (the terminal reference deck)
  - `slide-deck-handoff.md`
  - A Spanish instruction block: answer in Spanish, keep English technical terms, be concise (chat-sized), keep the workshop's "AI amplifies, does not replace judgment / verify your sources" framing, prefix the reply with the asker's first name.
  - Wrapped with **prompt caching** so this large context is near-free across many calls.
- **Images:** Telegram photos are downloaded and passed to Claude vision as base64 image blocks alongside the text.
- **Recent-Q&A memory in the prompt:** the last ~10 answered Q&A pairs (text + timestamp + relative message position) are included, with instructions:
  - If the new question is essentially a repeat answered **very recently** → do not re-answer; reply-link to the earlier message with a one-liner ("ya lo respondí arriba 👆").
  - If that earlier answer is **buried (>4 messages back)** → give a short recap **and** reply-link to the full answer.
  - The reply-link is a real Telegram reply to the stored message ID, so "refer to the earlier answer" is a clickable jump, not just a timestamp.

## 6. Response format

- Sent as a Telegram **reply** to the asker's message.
- Opens with the asker's **first name** (e.g., *"María: ..."*).
- Spanish, concise, English technical terms preserved.
- Length-capped so replies stay chat-sized (long answers truncated with a note or split).

## 7. Configuration

`.env` file (never committed):

| Key | Meaning |
|---|---|
| `TELEGRAM_TOKEN` | Bot token from BotFather |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `GROUP_ID` | The **single** chat ID of the workshop group (one negative integer). Allowlist — bot ignores everything else. NOT individual attendee IDs. |
| `HOST_USER_ID` | The host's own Telegram user ID (so the bot knows which messages are the teacher's) |
| `MODEL_DEFAULT` | Default model id (`claude-sonnet-5`) |
| `MODEL_ESCALATE` | Escalation model id (`claude-opus-4-8`) |

## 8. Setup & running

- **Attendees:** join the group via one QR/link the host projects. That is their entire setup.
- **Host:**
  1. Create bot via BotFather, get token, disable privacy mode.
  2. Add bot to the group; capture `GROUP_ID` and `HOST_USER_ID` (a one-time helper mode in the script can print IDs of incoming messages).
  3. Fill `.env`.
  4. `python bot.py` in a terminal.
- **Hosting:** laptop during the session is sufficient. Optional later: a tiny always-on host (Fly/Railway/VPS) if the bot should be live before/after the workshop.

## 9. Error handling & safety

- API failures: quiet retry with backoff; never crash the bot on a single failed answer.
- Background escalation failure: if the async Opus call fails after retries, fall back to posting Sonnet's original answer as the reply (so the asker is never left with only the "escalating..." note).
- Image download failures: fall back to text-only answer, note the image couldn't be read.
- Bot never posts outside `GROUP_ID`.
- No secrets committed; `.env` gitignored.
- Graceful shutdown on Ctrl-C.

## 10. Testing strategy

- **Unit:** trigger-gate logic (trivial-message filter, host rules, mention detection, rate limit) tested as pure functions over synthetic message objects.
- **Unit:** dedup/recent-memory logic — given a recent-Q&A list and a new question, assert the correct action (answer / reply-link-only / recap+link) via a mocked Claude response.
- **Integration (manual, pre-workshop):** run against a private test group — post text, post a screenshot, post a repeat question, post as host, @-mention the bot, verify each path.

## 11. Out of scope (YAGNI)

- Persistent database / analytics of questions (in-memory only).
- Multi-group / multi-workshop support.
- Voice messages, documents/PDFs (images + text only).
- The bot performing actions beyond answering (no code execution, no browsing).
- Web dashboard.
