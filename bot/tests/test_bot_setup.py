import pytest
import bot.bot as botmod


def test_load_token_returns_token(monkeypatch):
    monkeypatch.setattr(botmod, "dotenv_values", lambda p: {"TELEGRAM_TOKEN": "tok"} if str(p).endswith(".env") else {})
    assert botmod._load_token() == "tok"


def test_load_token_missing_exits(monkeypatch):
    monkeypatch.setattr(botmod, "dotenv_values", lambda p: {})
    with pytest.raises(SystemExit):
        botmod._load_token()
