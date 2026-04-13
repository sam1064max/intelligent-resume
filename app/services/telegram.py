from __future__ import annotations

import os
from dataclasses import dataclass

import httpx


@dataclass
class TelegramConfig:
    bot_token: str
    chat_id: str

    @property
    def enabled(self) -> bool:
        return bool(self.bot_token and self.chat_id)


def get_telegram_config() -> TelegramConfig:
    return TelegramConfig(
        bot_token=os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),
        chat_id=os.getenv("TELEGRAM_CHAT_ID", "").strip(),
    )


def send_telegram_message(message: str, config: TelegramConfig | None = None, timeout: float = 15.0) -> bool:
    current = config or get_telegram_config()
    if not current.enabled:
        return False

    response = httpx.post(
        f"https://api.telegram.org/bot{current.bot_token}/sendMessage",
        json={
            "chat_id": current.chat_id,
            "text": message,
        },
        timeout=timeout,
    )
    response.raise_for_status()
    return True


def build_optimization_message(target_role: str | None, ats_score: float, matched_skills: list[str], missing_skills: list[str]) -> str:
    role = target_role or "Resume optimization"
    matched = ", ".join(matched_skills[:8]) if matched_skills else "No exact matches detected"
    missing = ", ".join(missing_skills[:8]) if missing_skills else "No major skill gaps detected"
    return (
        f"JD-Aware Resume Optimizer update\n"
        f"Role: {role}\n"
        f"ATS score: {ats_score:.2f}\n"
        f"Matched skills: {matched}\n"
        f"Missing skills: {missing}"
    )
