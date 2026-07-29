"""Точка входа — скачивание модели и генерация речи."""

import logging
import sys

import config
from utils.download import download_voice
from utils.helpers import ensure_dirs
from utils.synthesize import generate

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
    voice: str = config.DEFAULT_VOICE

    model_path = config.VOICES_DIR / f"{voice}.onnx"
    if not model_path.exists():
        logger.info("Модель '%s' не найдена, скачиваю...", voice)
        try:
            download_voice(voice, config.VOICES_DIR)
        except (ConnectionError, ValueError) as exc:
            logger.error("Ошибка загрузки: %s", exc)
            sys.exit(1)

    try:
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
            pause_sentence=config.PAUSE_AFTER_SENTENCE,
            pause_paragraph=config.PAUSE_AFTER_PARAGRAPH,
        )
        logger.info("Файл создан: %s", result)
    except (FileNotFoundError, ValueError) as exc:
        logger.error("%s", exc)
        sys.exit(1)
    except Exception as exc:
        logger.error("Ошибка синтеза: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
