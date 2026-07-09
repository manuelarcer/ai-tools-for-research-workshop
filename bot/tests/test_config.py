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
