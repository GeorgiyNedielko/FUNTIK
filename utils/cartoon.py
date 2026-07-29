"""Мультяшный / полудетский голос через Microsoft Edge TTS (online)."""

from __future__ import annotations

import asyncio
import logging
import subprocess
import tempfile
from pathlib import Path

import edge_tts
import imageio_ffmpeg

from .helpers import next_versioned_path, sanitize_filename

logger: logging.Logger = logging.getLogger(__name__)


def _mp3_to_wav(mp3_path: Path, wav_path: Path) -> None:
    """Конвертирует mp3 → wav через встроенный ffmpeg."""
    ffmpeg: str = imageio_ffmpeg.get_ffmpeg_exe()
    cmd: list[str] = [
        ffmpeg,
        "-y",
        "-i",
        str(mp3_path),
        "-acodec",
        "pcm_s16le",
        "-ar",
        "22050",
        "-ac",
        "1",
        str(wav_path),
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Не удалось конвертировать mp3→wav:\n{result.stderr[-500:]}"
        )


async def _synthesize_async(
    text: str,
    voice: str,
    rate: str,
    pitch: str,
    volume: str,
    mp3_path: Path,
) -> None:
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        pitch=pitch,
        volume=volume,
    )
    await communicate.save(str(mp3_path))


def generate_cartoon(
    text: str,
    output_dir: Path,
    *,
    voice: str = "ru-RU-SvetlanaNeural",
    rate: str = "+10%",
    pitch: str = "+90Hz",
    volume: str = "+0%",
) -> Path:
    """
    Генерирует полудетский мультяшный голос (Edge TTS).

    Нужен интернет. Pitch выше обычного → «детский/мультяшный» тембр.
    """
    if not text.strip():
        raise ValueError("Текст для озвучки пустой.")

    output_dir.mkdir(parents=True, exist_ok=True)

    # Ярлык в имени файла (spd/n/nw формат сохраняем для единообразия версий)
    # pitch +90Hz → помечаем как cartoon
    tag: str = f"cartoon_{sanitize_filename(voice)}_{sanitize_filename(pitch)}"
    base_name: str = f"{sanitize_filename(text)}_{tag}"
    output_path: Path = next_versioned_path(output_dir, base_name)

    logger.info(
        "Cartoon TTS: voice=%s rate=%s pitch=%s volume=%s",
        voice,
        rate,
        pitch,
        volume,
    )

    with tempfile.TemporaryDirectory() as tmp:
        mp3_path: Path = Path(tmp) / "speech.mp3"
        try:
            asyncio.run(
                _synthesize_async(text, voice, rate, pitch, volume, mp3_path)
            )
        except Exception as exc:
            raise ConnectionError(
                f"Не удалось синтезировать через Edge TTS (нужен интернет): {exc}"
            ) from exc

        _mp3_to_wav(mp3_path, output_path)

    logger.info("Готово: %s", output_path)
    return output_path
