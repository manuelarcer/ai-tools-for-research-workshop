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
from bot.formatting import render_html
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
    try:
        return Config.from_env(env)
    except KeyError as e:
        log.error("Missing required .env key: %s", e.args[0])
        sys.exit(1)


def _load_token() -> str:
    env = {**dotenv_values(REPO_ROOT / ".env"), **dotenv_values(REPO_ROOT / "bot" / ".env")}
    token = env.get("TELEGRAM_TOKEN")
    if not token:
        log.error("No TELEGRAM_TOKEN found. Copy bot/.env.example to .env and set TELEGRAM_TOKEN.")
        sys.exit(1)
    return token


async def _print_ids(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    m = update.effective_message
    if m and update.effective_user:
        log.info("chat_id=%s user_id=%s name=%s text=%r",
                 m.chat_id, update.effective_user.id, update.effective_user.first_name, m.text)


async def _on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.error("Unhandled error in update processing", exc_info=context.error)


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
    image_failed = False
    if tg_msg.photo:
        try:
            photo = tg_msg.photo[-1]            # largest size
            tg_file = await context.bot.get_file(photo.file_id)
            images.append(bytes(await tg_file.download_as_bytearray()))
        except Exception:
            log.exception("Failed to download photo; answering text-only")
            image_failed = True

    if image_failed:
        text = (text + "\n[No pude leer la imagen adjunta.]").strip()

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
        # Render the model's Markdown as Telegram HTML (bold, code blocks, ...).
        # If Telegram rejects the HTML, fall back to plain text so the answer
        # always gets through.
        try:
            sent = await context.bot.send_message(
                chat_id=tg_msg.chat_id, text=render_html(reply_text)[:4096],
                reply_to_message_id=reply_to_message_id, parse_mode="HTML")
        except Exception:
            log.warning("HTML send failed; retrying as plain text")
            sent = await context.bot.send_message(
                chat_id=tg_msg.chat_id, text=reply_text[:4096],
                reply_to_message_id=reply_to_message_id)
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
                        help="Log chat_id/user_id of every message (for setup).")
    args = parser.parse_args()

    if args.print_ids:
        app = Application.builder().token(_load_token()).build()
        app.add_handler(MessageHandler(filters.ALL, _print_ids))
        log.info("ID helper mode: send a message in your group. Ctrl-C to stop.")
        app.run_polling()
        return

    cfg = _load_config()
    app = Application.builder().token(cfg.telegram_token).build()
    handler = _build_handler(cfg)
    app.bot_data["cfg"] = cfg
    app.bot_data["handler"] = handler
    app.add_handler(MessageHandler(
        (filters.TEXT | filters.PHOTO) & ~filters.COMMAND & filters.Chat(cfg.group_id),
        _on_message))
    app.add_error_handler(_on_error)
    log.info("Bot running. Group allowlist=%s host=%s", cfg.group_id, cfg.host_user_id)
    app.run_polling()


if __name__ == "__main__":
    main()
