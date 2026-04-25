from src.utils.link_parser import extract_first_url


def test_extract_first_url_from_plain_message() -> None:
    text = "Проверь пожалуйста https://music.yandex.ru/album/1/track/2 спасибо"
    assert extract_first_url(text) == "https://music.yandex.ru/album/1/track/2"


def test_extract_first_url_returns_none_without_url() -> None:
    assert extract_first_url("без ссылки") is None


def test_extract_first_url_trims_trailing_punctuation() -> None:
    text = "Ссылка: https://music.yandex.ru/album/1/track/2)."
    assert extract_first_url(text) == "https://music.yandex.ru/album/1/track/2"
