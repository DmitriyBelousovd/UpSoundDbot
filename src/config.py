from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    bot_token: str
    request_timeout_seconds: int = 10


def load_settings() -> Settings:
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    if not bot_token:
        raise ValueError("BOT_TOKEN is not set. Put it in .env file.")

    timeout_raw = os.getenv("REQUEST_TIMEOUT_SECONDS", "10").strip()
    try:
        timeout = int(timeout_raw)
    except ValueError as exc:
        raise ValueError("REQUEST_TIMEOUT_SECONDS must be an integer.") from exc

    if timeout <= 0:
        raise ValueError("REQUEST_TIMEOUT_SECONDS must be positive.")

    return Settings(bot_token=bot_token, request_timeout_seconds=timeout)
