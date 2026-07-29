"""Вспомогательные функции: директории, имена файлов, паузы, стиль."""

from __future__ import annotations

import logging
import re
import wave
from pathlib import Path

logger: logging.Logger = logging.getLogger(__name__)

# Только конец предложения — запятые/тире оставляем внутри фразы
_SENTENCE_END: str = ".!?…"


def ensure_dirs(*dirs: Path) -> None:
    """Создаёт директории, если они не существуют."""
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        logger.debug("Директория готова: %s", d)


def sanitize_filename(text: str, max_length: int = 40) -> str:
    """Превращает произвольный текст в безопасное имя файла."""
    name: str = text.strip().lower()
    name = re.sub(r"[^\w\s]", "", name, flags=re.UNICODE)
    name = re.sub(r"\s+", "_", name)
    name = name[:max_length].rstrip("_")
    return name or "output"


def clamp(value: float, low: float, high: float) -> float:
    """Ограничивает число диапазоном [low, high]."""
    return max(low, min(high, value))


def cartoon_style(
    intonation: float,
    cheerfulness: float,
    *,
    pitch_min_hz: float = 35.0,
    pitch_by_intonation_hz: float = 70.0,
    pitch_by_cheer_hz: float = 40.0,
    pitch_max_hz: float = 150.0,
    rate_by_intonation_pct: float = 10.0,
    rate_by_cheer_pct: float = 20.0,
    rate_max_pct: float = 40.0,
    volume_by_cheer_pct: float = 15.0,
    volume_max_pct: float = 50.0,
) -> tuple[str, str, str]:
    """
    INTONATION + CHEERFULNESS → (pitch, rate, volume) для Edge TTS.
    Все коэффициенты задаются из config.py.
    """
    x: float = clamp(intonation, 0.0, 1.0)
    c: float = clamp(cheerfulness, 0.0, 1.0)

    pitch_hz: int = int(
        round(pitch_min_hz + x * pitch_by_intonation_hz + c * pitch_by_cheer_hz)
    )
    pitch_hz = int(clamp(float(pitch_hz), 0.0, pitch_max_hz))

    rate_pct: int = int(round(x * rate_by_intonation_pct + c * rate_by_cheer_pct))
    rate_pct = int(clamp(float(rate_pct), 0.0, rate_max_pct))

    vol_pct: int = int(round(c * volume_by_cheer_pct))
    vol_pct = int(clamp(float(vol_pct), 0.0, volume_max_pct))

    return f"+{pitch_hz}Hz", f"+{rate_pct}%", f"+{vol_pct}%"


def cheer_up_text(
    text: str,
    cheerfulness: float,
    *,
    enabled: bool = True,
    threshold: float = 0.55,
) -> str:
    """При высоком cheerfulness точки в конце предложений → '!'."""
    if not enabled:
        return text
    if clamp(cheerfulness, 0.0, 1.0) < threshold:
        return text
    return re.sub(r"(?<=\w)\.(?=(\s|$))", "!", text.strip())


# Совместимость со старым именем
def cartoon_style_from_intonation(intonation: float) -> tuple[str, str]:
    """Устаревшая обёртка: pitch/rate без cheerfulness."""
    pitch, rate, _volume = cartoon_style(intonation, cheerfulness=0.5)
    return pitch, rate


def resolve_style(
    intonation: float,
    noise_scale: float | None,
    noise_w_scale: float | None,
) -> tuple[float, float]:
    """
    Превращает INTONATION (0..1) в параметры Piper.

    Держимся близко к дефолтам модели (noise≈0.667, noise_w≈0.8),
    иначе появляются «вздохи» и деревянный/хриплый звук.
    """
    x: float = clamp(intonation, 0.0, 1.0)

    # Близко к inference из .onnx.json: 0.667 / 0.8
    auto_noise: float = 0.55 + x * 0.20   # 0.55 .. 0.75
    auto_nw: float = 0.70 + x * 0.15      # 0.70 .. 0.85

    final_noise: float = auto_noise if noise_scale is None else float(noise_scale)
    final_nw: float = auto_nw if noise_w_scale is None else float(noise_w_scale)

    # Жёсткий clamp — защита от вздохов/артефактов
    final_noise = clamp(final_noise, 0.20, 1.00)
    final_nw = clamp(final_nw, 0.30, 1.00)
    return final_noise, final_nw


def format_settings_tag(
    speech_speed: float,
    noise_scale: float,
    noise_w_scale: float,
) -> str:
    """Короткий ярлык настроек для имени файла."""
    return (
        f"spd{speech_speed:.2f}"
        f"_n{noise_scale:.2f}"
        f"_nw{noise_w_scale:.2f}"
    )


def next_versioned_path(
    output_dir: Path,
    base_name: str,
    suffix: str = ".wav",
) -> Path:
    """Путь с новой версией: name_v1.wav, name_v2.wav, ..."""
    output_dir.mkdir(parents=True, exist_ok=True)

    version_re: re.Pattern[str] = re.compile(
        rf"^{re.escape(base_name)}_v(\d+){re.escape(suffix)}$",
        flags=re.IGNORECASE,
    )

    max_version: int = 0
    for path in output_dir.iterdir():
        if not path.is_file():
            continue
        match: re.Match[str] | None = version_re.match(path.name)
        if match:
            max_version = max(max_version, int(match.group(1)))

    return output_dir / f"{base_name}_v{max_version + 1}{suffix}"


def split_for_pauses(
    text: str,
    pause_sentence: float,
    pause_paragraph: float,
) -> list[tuple[str, float]]:
    """
    Делит текст на предложения (не по запятым!).

    Запятые и тире остаются внутри фразы — так Piper говорит естественно,
    без «заикания» на обрывках вроде «Сегодня —».
    """
    segments: list[tuple[str, float]] = []
    paragraphs: list[str] = re.split(r"\n\s*\n", text.strip())

    for p_index, paragraph in enumerate(paragraphs):
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        # Предложения: текст + конечный знак, либо хвост без знака
        parts: list[str] = re.findall(
            rf"[^{re.escape(_SENTENCE_END)}]+[{re.escape(_SENTENCE_END)}]+|"
            rf"[^{re.escape(_SENTENCE_END)}]+$",
            paragraph,
        )
        cleaned: list[str] = [p.strip() for p in parts if p.strip()]

        for i, part in enumerate(cleaned):
            is_last_in_paragraph: bool = i == len(cleaned) - 1
            is_last_paragraph: bool = p_index == len(paragraphs) - 1

            pause: float = 0.0
            if not is_last_in_paragraph:
                pause = pause_sentence
            elif not is_last_paragraph:
                pause = max(pause_sentence, pause_paragraph)

            segments.append((part, pause))

    return segments


def write_silence(
    wav_file: wave.Wave_write,
    duration_sec: float,
    sample_rate: int,
    sample_width: int = 2,
    channels: int = 1,
) -> None:
    """Записывает тишину заданной длительности в открытый wav-файл."""
    if duration_sec <= 0:
        return
    n_frames: int = int(sample_rate * duration_sec)
    wav_file.writeframes(b"\x00" * n_frames * sample_width * channels)
