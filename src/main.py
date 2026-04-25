import asyncio
import logging

from aiogram import Bot

from src.bot import build_dispatcher
from src.config import load_settings


async def _run() -> None:
    settings = load_settings()
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=settings.bot_token)
    dispatcher = build_dispatcher(settings)
    await dispatcher.start_polling(bot)


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
