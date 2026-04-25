from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Optional
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from src.models import TrackInfo


class TrackError(Exception):
    pass


@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    error: Optional[str] = None


def validate_track_url(url: str) -> ValidationResult:
    try:
        parsed = urlparse(url)
    except ValueError:
        return ValidationResult(False, "Некорректная ссылка.")

    if parsed.scheme not in {"http", "https"}:
        return ValidationResult(False, "Ссылка должна начинаться с http:// или https://")

    host = parsed.netloc.lower()
    if not host.endswith("music.yandex.ru") and not host.endswith("music.yandex.com"):
        return ValidationResult(False, "Поддерживаются только ссылки Яндекс.Музыки.")

    # Expected format: /album/<id>/track/<id>
    path = parsed.path.strip("/")
    parts = path.split("/")
    if len(parts) < 4 or parts[0] != "album" or parts[2] != "track":
        return ValidationResult(False, "Поддерживаются только ссылки на трек (album/.../track/...).")

    return ValidationResult(True)


def _parse_duration_seconds(raw: str) -> int:
    raw = raw.strip()
    if raw.isdigit():
        value = int(raw)
        # Some sources expose milliseconds.
        if value > 10_000:
            return value // 1000
        return value
    return 0


def _extract_from_ld_json(soup: BeautifulSoup) -> Optional[TrackInfo]:
    scripts = soup.select('script[type="application/ld+json"]')
    for script in scripts:
        if not script.string:
            continue
        try:
            payload = json.loads(script.string)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, list):
            candidates = payload
        else:
            candidates = [payload]
        for item in candidates:
            if not isinstance(item, dict):
                continue
            if item.get("@type") not in {"MusicRecording", "AudioObject"}:
                continue
            title = (item.get("name") or "").strip()
            by_artist = item.get("byArtist")
            artist = ""
            if isinstance(by_artist, dict):
                artist = (by_artist.get("name") or "").strip()
            elif isinstance(by_artist, list) and by_artist:
                first = by_artist[0]
                if isinstance(first, dict):
                    artist = (first.get("name") or "").strip()
            duration = item.get("duration", "")
            duration_seconds = 0
            if isinstance(duration, str) and duration.startswith("PT"):
                # Very small parser for strings like PT3M25S
                mins = 0
                secs = 0
                if "M" in duration:
                    mins_part = duration.split("PT", 1)[1].split("M", 1)[0]
                    if mins_part.isdigit():
                        mins = int(mins_part)
                if "S" in duration:
                    secs_part = duration.split("M")[-1].split("S", 1)[0].replace("PT", "")
                    if secs_part.isdigit():
                        secs = int(secs_part)
                duration_seconds = mins * 60 + secs
            if title and artist and duration_seconds > 0:
                return TrackInfo(title=title, artist=artist, duration_seconds=duration_seconds)
    return None


def _extract_from_meta_tags(soup: BeautifulSoup) -> Optional[TrackInfo]:
    title = ""
    artist = ""
    duration_seconds = 0

    og_title = soup.find("meta", attrs={"property": "og:title"})
    if og_title and og_title.get("content"):
        title = og_title["content"].strip()

    music_artist = soup.find("meta", attrs={"property": "music:musician"})
    if music_artist and music_artist.get("content"):
        artist = music_artist["content"].strip().split("/")[-1].replace("-", " ")

    music_duration = soup.find("meta", attrs={"property": "music:duration"})
    if music_duration and music_duration.get("content"):
        duration_seconds = _parse_duration_seconds(music_duration["content"])

    if title and artist and duration_seconds > 0:
        return TrackInfo(title=title, artist=artist, duration_seconds=duration_seconds)
    return None


async def fetch_track_info(url: str, timeout_seconds: int = 10) -> TrackInfo:
    validation = validate_track_url(url)
    if not validation.is_valid:
        raise TrackError(validation.error or "Некорректная ссылка.")

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; UpSoundTestBot/1.0)",
        "Accept-Language": "ru,en;q=0.9",
    }
    try:
        async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
    except httpx.TimeoutException as exc:
        raise TrackError("Таймаут при обращении к Яндекс.Музыке. Повторите позже.") from exc
    except httpx.HTTPError as exc:
        raise TrackError("Сетевая ошибка при получении данных трека.") from exc

    if response.status_code >= 400:
        raise TrackError("Трек недоступен или ссылка не открывается.")

    soup = BeautifulSoup(response.text, "html.parser")
    parsed = _extract_from_ld_json(soup) or _extract_from_meta_tags(soup)
    if not parsed:
        raise TrackError("Не удалось извлечь данные трека. Проверьте ссылку.")

    return parsed
