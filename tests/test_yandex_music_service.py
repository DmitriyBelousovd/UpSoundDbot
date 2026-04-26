from bs4 import BeautifulSoup

from src.services.yandex_music import (
    _detect_block_reason,
    _extract_from_ld_json,
    _parse_duration_seconds,
    validate_track_url,
)


def test_validate_track_url_accepts_track_links() -> None:
    result = validate_track_url("https://music.yandex.ru/album/10/track/99")
    assert result.is_valid is True


def test_validate_track_url_rejects_non_track_links() -> None:
    result = validate_track_url("https://music.yandex.ru/artist/123")
    assert result.is_valid is False


def test_parse_duration_seconds_supports_seconds_and_millis() -> None:
    assert _parse_duration_seconds("245") == 245
    assert _parse_duration_seconds("245000") == 245


def test_extract_from_ld_json_parses_music_recording() -> None:
    html = """
    <html><head>
    <script type="application/ld+json">
      {
        "@context": "https://schema.org",
        "@type": "MusicRecording",
        "name": "My Song",
        "byArtist": {"@type":"MusicGroup","name":"My Artist"},
        "duration": "PT3M25S"
      }
    </script>
    </head><body></body></html>
    """
    soup = BeautifulSoup(html, "html.parser")
    track = _extract_from_ld_json(soup)
    assert track is not None
    assert track.title == "My Song"
    assert track.artist == "My Artist"
    assert track.duration_seconds == 205


def test_detect_block_reason_for_region_restriction() -> None:
    html = "<html><body>Яндекс Музыка недоступна в вашем регионе</body></html>"
    reason = _detect_block_reason(html, "https://music.yandex.ru/album/1/track/2")
    assert reason is not None
    assert "региона" in reason


def test_detect_block_reason_for_captcha_page() -> None:
    html = "<script>window.__SSR_DATA__={url:'/ru/checkbox'}</script>"
    reason = _detect_block_reason(html, "https://music.yandex.ru/ru/checkbox?k=abc")
    assert reason is not None
    assert "captcha" in reason.lower()
