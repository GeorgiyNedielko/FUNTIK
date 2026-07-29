"""Синтез речи с помощью Piper TTS."""

from __future__ import annotations

import logging
import wave
from pathlib import Path

from piper import PiperVoice
from piper.config import SynthesisConfig

from .helpers import (
    format_settings_tag,
    next_versioned_path,
    resolve_style,
    sanitize_filename,
    split_for_pauses,
    write_silence,
)

logger: logging.Logger = logging.getLogger(__name__)


def generate(
    text: str,
    voice: str,
    voices_dir: Path,
    output_dir: Path,
    *,
    speech_speed: float = 1.0,
    intonation: float = 0.35,
    noise_scale: float | None = None,
    noise_w_scale: float | None = None,
    volume: float = 1.0,
    normalize_audio: bool = True,
    split_sentences: bool = False,
    pause_sentence: float = 0.25,
    pause_paragraph: float = 0.70,
) -> Path:
    """
    Синтезирует речь и сохраняет wav.

    По умолчанию текст озвучивается целиком — так меньше
    «вздохов» и стыков, чем при нарезке по предложениям.
    """
    model_path: Path = voices_dir / f"{voice}.onnx"
    config_path: Path = voices_dir / f"{voice}.onnx.json"

    if not model_path.exists():
        raise FileNotFoundError(
            f"Модель не найдена: {model_path}\n"
            f"Скачайте её командой: download_voice('{voice}', ...)"
        )
    if not config_path.exists():
        raise FileNotFoundError(
            f"Конфиг модели не найден: {config_path}\n"
            f"Скачайте модель заново: download_voice('{voice}', ...)"
        )
    if not text.strip():
        raise ValueError("Текст для озвучки пустой.")
    if speech_speed <= 0:
        raise ValueError(f"SPEECH_SPEED должен быть > 0 (сейчас: {speech_speed})")

    output_dir.mkdir(parents=True, exist_ok=True)

    length_scale: float = 1.0 / speech_speed
    final_noise, final_nw = resolve_style(intonation, noise_scale, noise_w_scale)

    settings_tag: str = format_settings_tag(speech_speed, final_noise, final_nw)
    base_name: str = f"{sanitize_filename(text)}_{settings_tag}"
    output_path: Path = next_versioned_path(output_dir, base_name)

    syn_config: SynthesisConfig = SynthesisConfig(
        length_scale=length_scale,
        noise_scale=final_noise,
        noise_w_scale=final_nw,
        volume=volume,
        normalize_audio=normalize_audio,
    )

    logger.info("Загрузка модели: %s", model_path)
    logger.info(
        "Стиль: speed=%.2f | intonation=%.2f → length=%.3f noise=%.3f noise_w=%.3f | "
        "split=%s | volume=%.2f",
        speech_speed,
        intonation,
        length_scale,
        final_noise,
        final_nw,
        split_sentences,
        volume,
    )

    piper_voice: PiperVoice = PiperVoice.load(
        model_path=str(model_path),
        config_path=str(config_path),
    )

    if split_sentences:
        segments: list[tuple[str, float]] = split_for_pauses(
            text,
            pause_sentence=pause_sentence,
            pause_paragraph=pause_paragraph,
        )
    else:
        # Один проход — самый ровный звук без стыков/вздохов
        segments = [(text.strip(), 0.0)]

    logger.info(
        "Фразы (%d): %s → %s",
        len(segments),
        [s[:40] for s, _ in segments],
        output_path.name,
    )

    sample_rate: int = piper_voice.config.sample_rate

    with wave.open(str(output_path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        for phrase, pause_sec in segments:
            piper_voice.synthesize_wav(
                phrase,
                wav_file,
                syn_config=syn_config,
                set_wav_format=False,
            )
            write_silence(wav_file, pause_sec, sample_rate)

    logger.info("Готово: %s", output_path)
    return output_path
