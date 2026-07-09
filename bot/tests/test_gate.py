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
    assert should_respond(msg(text="gracias"), CFG).respond is False

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
