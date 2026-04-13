from app.services.telegram import (
    TelegramConfig,
    build_optimization_message,
    send_telegram_message,
)


def test_build_optimization_message() -> None:
    message = build_optimization_message(
        "AI Engineer",
        0.84,
        ["Python", "FastAPI", "LLM"],
        ["Kubernetes"],
    )
    assert "AI Engineer" in message
    assert "0.84" in message
    assert "Python" in message
    assert "Kubernetes" in message


def test_send_telegram_message_without_config() -> None:
    sent = send_telegram_message("hello", config=TelegramConfig(bot_token="", chat_id=""))
    assert sent is False
