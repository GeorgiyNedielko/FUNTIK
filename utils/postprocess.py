"""Постобработка wav для детского канала (pedalboard + numpy)."""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import soundfile as sf
from pedalboard import (
    Compressor,
    HighShelfFilter,
    Limiter,
    PeakFilter,
    Pedalboard,
    PitchShift,
)

logger: logging.Logger = logging.getLogger(__name__)


def _to_mono(audio: np.ndarray) -> np.ndarray:
    """Приводит аудио к моно float32 shape (n_samples,)."""
    if audio.ndim == 1:
        return audio.astype(np.float32, copy=False)
    return np.mean(audio, axis=1).astype(np.float32)


def _trim_long_silences(
    audio: np.ndarray,
    sample_rate: int,
    *,
    threshold_db: float,
    max_silence_sec: float,
    frame_ms: float,
) -> np.ndarray:
    """Сжимает длинные паузы до max_silence_sec."""
    if audio.size == 0:
        return audio

    frame: int = max(1, int(sample_rate * frame_ms / 1000.0))
    max_silent_frames: int = max(1, int(max_silence_sec * 1000.0 / frame_ms))
    threshold: float = 10 ** (threshold_db / 20.0)

    kept: list[np.ndarray] = []
    silent_run: int = 0

    for start in range(0, len(audio), frame):
        chunk: np.ndarray = audio[start : start + frame]
        rms: float = float(np.sqrt(np.mean(np.square(chunk)) + 1e-12))
        if rms < threshold:
            silent_run += 1
            if silent_run <= max_silent_frames:
                kept.append(chunk)
        else:
            silent_run = 0
            kept.append(chunk)

    if not kept:
        return audio
    return np.concatenate(kept)


def _apply_fades(
    audio: np.ndarray,
    sample_rate: int,
    fade_in_sec: float,
    fade_out_sec: float,
) -> np.ndarray:
    """Плавный fade-in / fade-out."""
    out: np.ndarray = audio.copy()
    n_in: int = int(sample_rate * fade_in_sec)
    n_out: int = int(sample_rate * fade_out_sec)

    if n_in > 0 and len(out) > n_in:
        out[:n_in] *= np.linspace(0.0, 1.0, n_in, dtype=np.float32)
    if n_out > 0 and len(out) > n_out:
        out[-n_out:] *= np.linspace(1.0, 0.0, n_out, dtype=np.float32)
    return out


def _peak_normalize(audio: np.ndarray, peak_db: float) -> np.ndarray:
    """Нормализация по пику до peak_db."""
    peak: float = float(np.max(np.abs(audio)) + 1e-12)
    target: float = 10 ** (peak_db / 20.0)
    return (audio * (target / peak)).astype(np.float32)


def postprocess_wav(
    wav_path: Path,
    *,
    enable_compressor: bool = True,
    enable_eq: bool = True,
    enable_normalize: bool = True,
    enable_limiter: bool = True,
    enable_trim_silence: bool = True,
    enable_fades: bool = True,
    enable_pitch_shift: bool = True,
    compressor_threshold_db: float = -18.0,
    compressor_ratio: float = 3.0,
    compressor_attack_ms: float = 8.0,
    compressor_release_ms: float = 80.0,
    eq_high_shelf_hz: float = 4200.0,
    eq_high_shelf_gain_db: float = 3.5,
    eq_presence_hz: float = 3000.0,
    eq_presence_gain_db: float = 2.0,
    eq_presence_q: float = 1.0,
    silence_threshold_db: float = -40.0,
    max_silence_sec: float = 0.28,
    silence_frame_ms: float = 20.0,
    fade_in_sec: float = 0.025,
    fade_out_sec: float = 0.040,
    pitch_semitones: float = 1.2,
    normalize_peak_db: float = -1.0,
    limiter_threshold_db: float = -1.0,
    limiter_release_ms: float = 50.0,
) -> Path:
    """Улучшает wav и перезаписывает файл на месте."""
    audio, sample_rate = sf.read(str(wav_path), always_2d=False)
    mono: np.ndarray = _to_mono(np.asarray(audio))
    sr: int = int(sample_rate)

    logger.info("Постобработка: %s (%d Hz, %d сэмплов)", wav_path.name, sr, len(mono))

    if enable_trim_silence:
        before: int = len(mono)
        mono = _trim_long_silences(
            mono,
            sr,
            threshold_db=silence_threshold_db,
            max_silence_sec=max_silence_sec,
            frame_ms=silence_frame_ms,
        )
        logger.info(
            "Паузы: %d → %d сэмплов (max silence=%.2fs)",
            before,
            len(mono),
            max_silence_sec,
        )

    if enable_fades:
        mono = _apply_fades(mono, sr, fade_in_sec, fade_out_sec)

    plugins: list[object] = []

    if enable_pitch_shift and abs(pitch_semitones) > 0.01:
        plugins.append(PitchShift(semitones=float(pitch_semitones)))

    if enable_eq:
        plugins.append(
            HighShelfFilter(
                cutoff_frequency_hz=float(eq_high_shelf_hz),
                gain_db=float(eq_high_shelf_gain_db),
            )
        )
        plugins.append(
            PeakFilter(
                cutoff_frequency_hz=float(eq_presence_hz),
                gain_db=float(eq_presence_gain_db),
                q=float(eq_presence_q),
            )
        )

    if enable_compressor:
        plugins.append(
            Compressor(
                threshold_db=float(compressor_threshold_db),
                ratio=float(compressor_ratio),
                attack_ms=float(compressor_attack_ms),
                release_ms=float(compressor_release_ms),
            )
        )

    if enable_limiter:
        plugins.append(
            Limiter(
                threshold_db=float(limiter_threshold_db),
                release_ms=float(limiter_release_ms),
            )
        )

    if plugins:
        board: Pedalboard = Pedalboard(plugins)
        processed: np.ndarray = board(mono, sr)
        processed = _to_mono(np.asarray(processed))
    else:
        processed = mono

    if enable_normalize:
        processed = _peak_normalize(processed, peak_db=normalize_peak_db)

    processed = np.clip(processed, -1.0, 1.0).astype(np.float32)
    sf.write(str(wav_path), processed, sr, subtype="PCM_16")
    logger.info("Постобработка готова: %s", wav_path)
    return wav_path
