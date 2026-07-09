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
