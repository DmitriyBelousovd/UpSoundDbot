from aiogram import Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.config import Settings
from src.services.yandex_music import TrackError, fetch_track_info
from src.utils.link_parser import extract_first_url


def build_dispatcher(settings: Settings) -> Dispatcher:
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def handle_start(message: Message) -> None:
        await message.answer(
            "Привет! Отправьте ссылку на трек из Яндекс.Музыки.\n"
            "Поддерживаемый формат: https://music.yandex.ru/album/<id>/track/<id>"
        )

    @dp.message(Command("reset"))
    async def handle_reset(message: Message, state: FSMContext) -> None:
        await state.clear()
        await message.answer(
            "Состояние сброшено. Отправьте ссылку на трек из Яндекс.Музыки.\n"
            "Поддерживаемый формат: https://music.yandex.ru/album/<id>/track/<id>"
        )

    @dp.message(F.text)
    async def handle_text(message: Message) -> None:
        text = message.text or ""
        url = extract_first_url(text)
        if not url:
            await message.answer("Не нашел ссылку в сообщении. Пришлите ссылку на трек Яндекс.Музыки.")
            return

        try:
            track = await fetch_track_info(url, timeout_seconds=settings.request_timeout_seconds)
        except TrackError as exc:
            await message.answer(f"Ошибка: {exc}")
            return

        await message.answer(
            "Трек найден:\n"
            f"Название: {track.title}\n"
            f"Артист: {track.artist}\n"
            f"Длительность: {track.duration_mm_ss}"
        )

    return dp
