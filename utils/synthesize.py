"""Синтез речи с помощью Piper TTS."""

import logging
import wave
from pathlib import Path

from piper import PiperVoice

logger: logging.Logger = logging.getLogger(__name__)


def generate(text: str, voice: str, voices_dir: Path, output_dir: Path) -> Path:
    """
    Синтезирует речь и сохраняет результат в wav-файл.

    :param text: Текст для озвучки.
    :param voice: Имя голоса, например 'de_DE-thorsten-medium'.
    :param voices_dir: Папка с моделями.
    :param output_dir: Папка для результата.
    :return: Путь к созданному wav-файлу.
    :raises FileNotFoundError: Если модель не найдена.
    """
    from .helpers import sanitize_filename

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

    output_dir.mkdir(parents=True, exist_ok=True)

    filename: str = sanitize_filename(text) + ".wav"
    output_path: Path = output_dir / filename

    logger.info("Загрузка модели: %s", model_path)
    piper_voice: PiperVoice = PiperVoice.load(
        model_path=str(model_path),
        config_path=str(config_path),
    )

    logger.info("Синтез: '%s' → %s", text, output_path)
    with wave.open(str(output_path), "wb") as wav_file:
        piper_voice.synthesize_wav(text, wav_file)

    logger.info("Готово: %s", output_path)
    return output_path
