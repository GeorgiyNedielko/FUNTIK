"""Точка входа — генерация речи (cartoon / piper) + постобработка."""

import logging
import sys

import config
from utils.helpers import ensure_dirs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger: logging.Logger = logging.getLogger(__name__)


def main() -> None:
    ensure_dirs(config.VOICES_DIR, config.TEXT_DIR, config.OUTPUT_DIR)

    # --- Текст для озвучки (редактируйте здесь) ---
    text: str = (
        "Приветствую тебя на нашем канале! "
        "Сегодня — весёлая история, с паузами и живой интонацией."
    )

    engine: str = config.ENGINE.strip().lower()
    logger.info("Движок: %s", engine)

    try:
        if engine == "cartoon":
            from utils.cartoon import generate_cartoon
            from utils.helpers import cartoon_style, cheer_up_text

            auto_pitch, auto_rate, auto_volume = cartoon_style(
                config.INTONATION,
                config.CHEERFULNESS,
                pitch_min_hz=config.CARTOON_AUTO_PITCH_MIN_HZ,
                pitch_by_intonation_hz=config.CARTOON_AUTO_PITCH_BY_INTONATION_HZ,
                pitch_by_cheer_hz=config.CARTOON_AUTO_PITCH_BY_CHEER_HZ,
                pitch_max_hz=config.CARTOON_AUTO_PITCH_MAX_HZ,
                rate_by_intonation_pct=config.CARTOON_AUTO_RATE_BY_INTONATION_PCT,
                rate_by_cheer_pct=config.CARTOON_AUTO_RATE_BY_CHEER_PCT,
                rate_max_pct=config.CARTOON_AUTO_RATE_MAX_PCT,
                volume_by_cheer_pct=config.CARTOON_AUTO_VOLUME_BY_CHEER_PCT,
                volume_max_pct=config.CARTOON_AUTO_VOLUME_MAX_PCT,
            )
            pitch: str = config.CARTOON_PITCH or auto_pitch
            rate: str = config.CARTOON_RATE or auto_rate
            volume: str = config.CARTOON_VOLUME or auto_volume
            spoken_text: str = cheer_up_text(
                text,
                config.CHEERFULNESS,
                enabled=config.CHEER_REWRITE_DOTS,
                threshold=config.CHEER_REWRITE_THRESHOLD,
            )

            logger.info(
                "Cartoon: INTONATION=%.2f CHEERFULNESS=%.2f → "
                "pitch=%s rate=%s volume=%s "
                "(ручные: pitch=%s rate=%s volume=%s)",
                config.INTONATION,
                config.CHEERFULNESS,
                pitch,
                rate,
                volume,
                config.CARTOON_PITCH,
                config.CARTOON_RATE,
                config.CARTOON_VOLUME,
            )

            result = generate_cartoon(
                text=spoken_text,
                output_dir=config.OUTPUT_DIR,
                voice=config.CARTOON_VOICE,
                rate=rate,
                pitch=pitch,
                volume=volume,
            )
        elif engine == "piper":
            from utils.download import download_voice
            from utils.synthesize import generate

            voice: str = config.DEFAULT_VOICE
            model_path = config.VOICES_DIR / f"{voice}.onnx"
            if not model_path.exists():
                logger.info("Модель '%s' не найдена, скачиваю...", voice)
                download_voice(voice, config.VOICES_DIR)

            result = generate(
                text=text,
                voice=voice,
                voices_dir=config.VOICES_DIR,
                output_dir=config.OUTPUT_DIR,
                speech_speed=config.SPEECH_SPEED,
                intonation=config.INTONATION,
                noise_scale=config.NOISE_SCALE,
                noise_w_scale=config.NOISE_W_SCALE,
                volume=config.VOLUME,
                normalize_audio=config.NORMALIZE_AUDIO,
                split_sentences=config.SPLIT_SENTENCES,
                pause_sentence=config.PAUSE_AFTER_SENTENCE,
                pause_paragraph=config.PAUSE_AFTER_PARAGRAPH,
            )
        else:
            logger.error(
                "Неизвестный ENGINE='%s'. Допустимо: 'cartoon' или 'piper'.",
                config.ENGINE,
            )
            sys.exit(1)

        if config.POSTPROCESS_ENABLED:
            from utils.postprocess import postprocess_wav

            result = postprocess_wav(
                result,
                enable_compressor=config.POST_COMPRESSOR,
                enable_eq=config.POST_EQ,
                enable_normalize=config.POST_NORMALIZE,
                enable_limiter=config.POST_LIMITER,
                enable_trim_silence=config.POST_TRIM_SILENCE,
                enable_fades=config.POST_FADES,
                enable_pitch_shift=config.POST_PITCH_SHIFT,
                compressor_threshold_db=config.POST_COMPRESSOR_THRESHOLD_DB,
                compressor_ratio=config.POST_COMPRESSOR_RATIO,
                compressor_attack_ms=config.POST_COMPRESSOR_ATTACK_MS,
                compressor_release_ms=config.POST_COMPRESSOR_RELEASE_MS,
                eq_high_shelf_hz=config.POST_EQ_HIGHSHELF_HZ,
                eq_high_shelf_gain_db=config.POST_EQ_HIGHSHELF_GAIN_DB,
                eq_presence_hz=config.POST_EQ_PRESENCE_HZ,
                eq_presence_gain_db=config.POST_EQ_PRESENCE_GAIN_DB,
                eq_presence_q=config.POST_EQ_PRESENCE_Q,
                silence_threshold_db=config.POST_SILENCE_THRESHOLD_DB,
                max_silence_sec=config.POST_MAX_SILENCE_SEC,
                silence_frame_ms=config.POST_SILENCE_FRAME_MS,
                fade_in_sec=config.POST_FADE_IN_SEC,
                fade_out_sec=config.POST_FADE_OUT_SEC,
                pitch_semitones=config.POST_PITCH_SEMITONES,
                normalize_peak_db=config.POST_NORMALIZE_PEAK_DB,
                limiter_threshold_db=config.POST_LIMITER_THRESHOLD_DB,
                limiter_release_ms=config.POST_LIMITER_RELEASE_MS,
            )

        logger.info("Файл создан: %s", result)
    except (FileNotFoundError, ValueError, ConnectionError, RuntimeError) as exc:
        logger.error("%s", exc)
        sys.exit(1)
    except Exception as exc:
        logger.error("Ошибка синтеза: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
