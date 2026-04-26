from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    bot_token: str
    request_timeout_seconds: int = 10
    webhook_base_url: str = ""
    webhook_path: str = "/tg/webhook"
    port: int = 10000


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

    webhook_base_url = os.getenv("WEBHOOK_BASE_URL", "").strip().rstrip("/")
    if not webhook_base_url:
        raise ValueError("WEBHOOK_BASE_URL is not set.")
    if not webhook_base_url.startswith("https://"):
        raise ValueError("WEBHOOK_BASE_URL must start with https://")

    webhook_path = os.getenv("WEBHOOK_PATH", "/tg/webhook").strip()
    if not webhook_path.startswith("/"):
        raise ValueError("WEBHOOK_PATH must start with '/'.")

    port_raw = os.getenv("PORT", "10000").strip()
    try:
        port = int(port_raw)
    except ValueError as exc:
        raise ValueError("PORT must be an integer.") from exc

    if port <= 0:
        raise ValueError("PORT must be positive.")

    return Settings(
        bot_token=bot_token,
        request_timeout_seconds=timeout,
        webhook_base_url=webhook_base_url,
        webhook_path=webhook_path,
        port=port,
    )
