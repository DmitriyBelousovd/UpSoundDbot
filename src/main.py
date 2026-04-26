import asyncio
import logging

from aiogram import Bot
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from src.bot import build_dispatcher
from src.config import load_settings


async def _run() -> None:
    settings = load_settings()
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=settings.bot_token)
    dispatcher = build_dispatcher(settings)
    webhook_url = f"{settings.webhook_base_url}{settings.webhook_path}"
    app = web.Application()

    SimpleRequestHandler(dispatcher=dispatcher, bot=bot).register(app, path=settings.webhook_path)
    setup_application(app, dispatcher, bot=bot)

    async def _on_startup(_: web.Application) -> None:
        await bot.set_webhook(url=webhook_url)
        logging.info("Webhook set to %s", webhook_url)

    async def _on_shutdown(_: web.Application) -> None:
        await bot.delete_webhook(drop_pending_updates=False)
        await bot.session.close()

    app.on_startup.append(_on_startup)
    app.on_shutdown.append(_on_shutdown)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=settings.port)
    await site.start()
    logging.info("Web server started on port %s", settings.port)

    try:
        await asyncio.Event().wait()
    finally:
        await runner.cleanup()


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
