# Workshop Q&A Bot (Telegram)

Answers attendees' text and screenshot questions during the "Inteligencia Artificial
para la Investigación" workshop, in Spanish, grounded in this repo's material.

This guide is written to be followed start-to-finish with no prior bot experience.
Budget ~15 minutes for first-time setup.

---

## What you'll end up with

- A Telegram **bot account** (created via BotFather) added to your **workshop group**.
- The bot **running on your laptop** (a Python program in a terminal window) during the
  session. It watches the group, and whenever an attendee asks something or posts a
  screenshot, it replies in Spanish.
- Attendees need to do **nothing** except join the group and type. No accounts, no keys.

You (the host) need three secret values, all stored in one local file called `.env`:
a **Telegram bot token**, an **Anthropic API key**, and later two **ID numbers**.

> **About `.env` and secrets:** the `.env` file holds your private keys. It is
> deliberately **not** committed to git (it's in `.gitignore`) and must **never** be
> pushed or shared. The repo only contains `bot/.env.example`, a template with fake
> values. You copy that template to `.env` on your own machine and fill in the real values.

---

## Step 1 — Create the bot with BotFather

BotFather is Telegram's official tool for making bots. It's itself a bot you chat with.

1. Open Telegram (phone or desktop). In search, type **`BotFather`** and open the one
   with the blue **verified checkmark** (`@BotFather`).
2. Press **Start** (or send `/start`).
3. Send **`/newbot`**.
4. It asks for a **name** — this is the display name shown in the group, e.g.
   `Asistente Taller IA`. Type it and send.
5. It asks for a **username** — must be unique and **end in `bot`**, e.g.
   `taller_ia_qa_bot`. Type it and send. If taken, try another.
6. BotFather replies with a **token** that looks like:
   ```
   8123456789:AAHk3l...long-random-string...
   ```
   **Copy it and keep it private.** This is your `TELEGRAM_TOKEN`.

### Step 1b — Let the bot read all group messages (important)

By default a bot in a group only sees messages that mention it or are commands. This bot
must see **every** message to answer questions. Turn that on:

7. In the BotFather chat, send **`/setprivacy`**.
8. It asks which bot — select yours (tap the button with your `@username`).
9. Send **`Disable`**.
   You should see: *"Privacy mode is disabled for <yourbot>."*

> If you skip this, the bot will appear to ignore most questions.

*(Optional polish, via BotFather: `/setdescription`, `/setabouttext`, `/setuserpic`.)*

---

## Step 2 — Get an Anthropic API key

This is what lets the bot call Claude (the model that writes the answers).

1. Go to **<https://console.anthropic.com>** and sign in (or create an account).
2. Open **API keys** (left sidebar) → **Create Key**.
3. Copy the key (starts with `sk-ant-...`). This is your `ANTHROPIC_API_KEY`.
   Keep it private — same rules as the Telegram token.

> Billing: the bot uses Claude Sonnet by default (cheap) and only escalates hard
> questions to Opus. A single workshop typically costs a few dollars at most, but make
> sure your Anthropic account has credit / a payment method.

---

## Step 3 — Install the bot on your laptop

You need **Python 3.11+**. Check with `python3 --version`.

Open a terminal, go to the repo folder (the one containing the `bot/` directory), then:

```bash
# create an isolated Python environment (once)
python3 -m venv .venv

# activate it (do this each new terminal session)
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows PowerShell

# install the bot's dependencies (once)
pip install -r bot/requirements.txt
```

When the environment is active your prompt shows `(.venv)` at the start.

---

## Step 4 — Create your `.env` file

```bash
cp bot/.env.example .env
```

Open `.env` in any text editor and fill in the two values you have so far:

```
TELEGRAM_TOKEN=8123456789:AAHk3l...        # from Step 1
ANTHROPIC_API_KEY=sk-ant-...               # from Step 2
GROUP_ID=                                   # leave blank for now (Step 6)
HOST_USER_ID=                               # leave blank for now (Step 6)
```

Leave `MODEL_DEFAULT`, `MODEL_ESCALATE`, and `COOLDOWN_SECONDS` at their defaults.

> The `.env` file lives at the **repo root** (next to the `bot/` folder), not inside `bot/`.

---

## Step 5 — Create the workshop group and add the bot

1. In Telegram: **New Group**.
2. Give it a name (e.g. "Taller IA — Preguntas").
3. Add members: add **yourself** and search your bot by its **`@username`** to add it too.
   (You can add attendees now or share an invite link later.)

---

## Step 6 — Capture the two ID numbers

The bot needs to know **which group** to serve (`GROUP_ID`) and **which person is you**,
the teacher (`HOST_USER_ID`). A built-in helper prints them for you.

1. With `.env` filled in (token only is enough for this step), run:
   ```bash
   python -m bot.bot --print-ids
   ```
2. In the Telegram group, **send any message** (e.g. "hola").
3. Watch the terminal. You'll see a line like:
   ```
   chat_id=-1001234567890 user_id=987654321 name=Juan text='hola'
   ```
   - `chat_id` (the negative number) → this is your **`GROUP_ID`**.
   - `user_id` (from *your own* message) → this is your **`HOST_USER_ID`**.
4. Press **Ctrl-C** to stop the helper.
5. Put both numbers into `.env`:
   ```
   GROUP_ID=-1001234567890
   HOST_USER_ID=987654321
   ```

---

## Step 7 — Run the bot

```bash
python -m bot.bot
```

You should see: `Bot running. Group allowlist=... host=...`. Leave this terminal window
open — the bot only works while this program is running. Now post a question in the group
and it should reply.

To stop: **Ctrl-C**.

> Keep your laptop awake and online during the workshop. The bot runs locally; if the
> laptop sleeps or loses internet, it stops answering until it's back.

---

## Test it before the workshop (private group)

Make a throwaway private group with just you and the bot, then walk this checklist:

- [ ] Attendee text question → bot replies in Spanish, prefixed with the name.
- [ ] Post a screenshot (e.g. a terminal error) → bot interprets the image.
- [ ] Post "gracias" / an emoji → bot stays silent.
- [ ] Post as the host (you) *without* naming the bot → bot stays silent.
- [ ] @-mention the bot as the host → bot replies.
- [ ] Ask a hard/out-of-scope question → bot posts the "escalo a Opus" note, then a fuller answer.
- [ ] Ask the same question twice quickly → the second time it points back to the first answer.
- [ ] Send several messages fast from one account → the rate limit throttles.

---

## What the bot knows (grounding)

At startup the bot loads a set of workshop files into its context so its answers match
what you taught. The file list is at the top of **`bot/grounding.py`**
(`GROUNDING_FILES` and `SLIDE_HTML`). Missing files are skipped with a warning, so you can
add or swap documents as your materials are finalized — just update that list.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Bot ignores most messages | You skipped **Step 1b** — run `/setprivacy` → `Disable` in BotFather. |
| `Missing required .env key: GROUP_ID` | Fill in `GROUP_ID`/`HOST_USER_ID` (Step 6). |
| `No TELEGRAM_TOKEN found` | Your `.env` is missing or the token line is blank. |
| Bot replies in the wrong/another chat, or not at all | Confirm `GROUP_ID` matches the group (re-run `--print-ids`). The bot only serves that one group. |
| `--print-ids` shows nothing | Make sure the bot is **in** the group and you actually sent a message there. |
| Import or "module not found" errors | Activate the venv (`source .venv/bin/activate`) and re-run `pip install -r bot/requirements.txt`. |
| Answers seem generic / ignore the workshop | Check `bot/grounding.py` points at real files; warnings about "Grounding file not found" appear at startup. |
