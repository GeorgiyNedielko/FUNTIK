"""Точка входа — скачивание модели и генерация речи."""

import logging
import sys

from config import DEFAULT_VOICE, OUTPUT_DIR, VOICES_DIR, TEXT_DIR
from utils.helpers import ensure_dirs
from utils.download import download_voice, list_voices
from utils.synthesize import generate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger: logging.Logger = logging.getLogger(__name__)


def main() -> None:
    # Создаём рабочие директории
    ensure_dirs(VOICES_DIR, TEXT_DIR, OUTPUT_DIR)

    voice: str = DEFAULT_VOICE
    text: str = "Hallo Kinder!"

    # Скачиваем модель, если её ещё нет
    model_path = VOICES_DIR / f"{voice}.onnx"
    if not model_path.exists():
        logger.info("Модель '%s' не найдена, скачиваю...", voice)
        try:
            download_voice(voice, VOICES_DIR)
        except (ConnectionError, ValueError) as exc:
            logger.error("Ошибка загрузки: %s", exc)
            sys.exit(1)

    # Генерируем речь
    try:
        result = generate(text=text, voice=voice, voices_dir=VOICES_DIR, output_dir=OUTPUT_DIR)
        logger.info("Файл создан: %s", result)
    except FileNotFoundError as exc:
        logger.error("%s", exc)
        sys.exit(1)
    except Exception as exc:
        logger.error("Ошибка синтеза: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
