"""Точка входа — генерация речи (cartoon / piper)."""

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
            )
            pitch: str = config.CARTOON_PITCH or auto_pitch
            rate: str = config.CARTOON_RATE or auto_rate
            volume: str = config.CARTOON_VOLUME or auto_volume
            spoken_text: str = cheer_up_text(text, config.CHEERFULNESS)

            logger.info(
                "Cartoon: INTONATION=%.2f CHEERFULNESS=%.2f → "
                "pitch=%s rate=%s volume=%s",
                config.INTONATION,
                config.CHEERFULNESS,
                pitch,
                rate,
                volume,
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

        logger.info("Файл создан: %s", result)
    except (FileNotFoundError, ValueError, ConnectionError, RuntimeError) as exc:
        logger.error("%s", exc)
        sys.exit(1)
    except Exception as exc:
        logger.error("Ошибка синтеза: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
