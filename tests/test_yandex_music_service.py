from bs4 import BeautifulSoup

from src.services.yandex_music import (
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
