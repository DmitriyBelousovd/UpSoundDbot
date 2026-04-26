import asyncio
import logging

from aiogram import Bot

from src.bot import build_dispatcher
from src.config import Settings
from dotenv import load_dotenv
import os


def _load_local_settings() -> Settings:
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


async def _run() -> None:
    settings = _load_local_settings()
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=settings.bot_token)
    dispatcher = build_dispatcher(settings)
    # If webhook was previously configured (e.g. Render), polling won't receive updates.
    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot)


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
