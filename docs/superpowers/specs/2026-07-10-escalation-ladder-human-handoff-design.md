# Escalation Ladder with Human Handoff — Design

**Date:** 2026-07-10
**Feature:** Extend the Telegram workshop bot so a persistently stuck user is escalated to Opus, and — if Opus also fails to resolve it after a bounded number of tries — handed off to the human host instead of escalating further.

## Goal

Add a three-tier response ladder keyed per user:

1. **Sonnet answers** (default, high bar — unchanged).
2. **Stuck ~3× on the same issue** → escalate to **Opus** (Sonnet's judgment, from the user's recent-message history).
3. **Still stuck after 2 Opus calls** → stop escalating; deliver Sonnet's best answer plus a note, and **@-mention the host** so they can intervene when free.

## Per-user state

A new `bot/user_state.py` holds one record per Telegram `user_id`:

- `messages`: the user's last `MAX_HISTORY = 5` message texts (fed to Sonnet to judge repetition).
- `opus_calls`: how many Opus escalations have happened this window.
- `handed_off`: whether the host has already been pinged this episode.
- `last_activity`: timestamp; if the user is idle longer than `WINDOW_SECONDS = 20*60`, the record resets on next access (a fresh struggle starts clean).

`UserStates.get(user_id, now)` returns the record, resetting it if stale, and refreshes `last_activity` to `now`.

## Detection split (soft entry, hard ceiling)

- **Entry to Opus** is Sonnet's soft judgment: the `submit_answer` tool's `escalate` field description gains a clause — set `true` if this same user has asked about the same unresolved problem ~3 times. The user's recent messages are rendered into the request so Sonnet can see the repetition.
- **Ceiling** is a hard deterministic count in the handler: `MAX_OPUS_CALLS = 2`. This bounds cost to at most 2 Opus calls per stuck user per 20-minute window.

## Handler ladder (when `answer.escalate` and `cfg.escalation_enabled`)

- `opus_calls < 2` → increment, send interim note, run Opus in background (existing async path).
- `opus_calls == 2` and not `handed_off` → set `handed_off`; deliver Sonnet's answer to the user, then send a handoff note that mentions the host.
- already `handed_off` → deliver Sonnet's answer only (no Opus, no re-ping).

If `escalation_enabled` is false, none of this fires — Sonnet's answer is delivered directly.

## Host mention

Built from the existing `HOST_USER_ID` as a Telegram text-mention: markdown `[el instructor](tg://user?id=<HOST_USER_ID>)`. The HTML renderer's link rule is extended to accept `tg://user?id=<digits>` (in addition to http/https), so it renders to `<a href="tg://user?id=…">el instructor</a>` — which notifies the host even if they have no @username. The host is pinged once per episode.

Handoff message (Spanish):
> {name}: esto quizá necesite ayuda más directa. Avisé a [el instructor](tg://user?id=…) para que lo revise cuando pueda.

## Files touched

- Create `bot/user_state.py` (+ `bot/tests/test_user_state.py`).
- `bot/claude_client.py`: `build_user_content`/`answer` gain a `user_history: str` param; extend the `escalate` tool description.
- `bot/handler.py`: accept a `UserStates` (default-constructed if not injected); implement the ladder + handoff.
- `bot/formatting.py`: allow the `tg://user?id=` link scheme.
- Tests for each; `bot/.env.example`/README unchanged (no new config — window and ceiling are code constants).

## Out of scope

- Cross-issue disambiguation: Opus-call count is per user, not per distinct issue. Two different hard issues in one window share the ceiling. Acceptable for a single live workshop.
- Persisting state across bot restarts (in-memory only).
