"""Скачивание голосовых моделей Piper с Hugging Face."""

import json
import logging
import shutil
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

logger: logging.Logger = logging.getLogger(__name__)

# Шаблон URL для загрузки моделей с Hugging Face
_URL_FORMAT: str = (
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
    "{lang_family}/{lang_code}/{voice_name}/{voice_quality}/"
    "{lang_code}-{voice_name}-{voice_quality}{extension}?download=true"
)

_VOICES_JSON_URL: str = (
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/voices.json?download=true"
)


def _parse_voice_name(voice: str) -> dict[str, str]:
    """Разбирает имя голоса вида 'de_DE-thorsten-medium' на компоненты."""
    parts: list[str] = voice.split("-")
    if len(parts) < 3:
        raise ValueError(
            f"Неверный формат голоса: '{voice}'. "
            "Ожидается: <lang_REGION>-<name>-<quality>, например 'de_DE-thorsten-medium'"
        )
    lang_code: str = parts[0]          # de_DE
    voice_name: str = parts[1]         # thorsten
    voice_quality: str = parts[2]      # medium
    lang_family: str = lang_code.split("_")[0]  # de

    return {
        "lang_family": lang_family,
        "lang_code": lang_code,
        "voice_name": voice_name,
        "voice_quality": voice_quality,
    }


def _needs_download(path: Path) -> bool:
    """Проверяет, нужно ли скачивать файл."""
    return not path.exists() or path.stat().st_size == 0


def download_voice(voice: str, download_dir: Path) -> Path:
    """
    Скачивает модель (.onnx) и конфиг (.onnx.json) в download_dir.

    :param voice: Имя голоса, например 'de_DE-thorsten-medium'.
    :param download_dir: Папка для сохранения файлов.
    :return: Путь к файлу модели (.onnx).
    :raises ValueError: Если формат имени голоса некорректен.
    :raises ConnectionError: Если не удалось скачать файлы.
    """
    params: dict[str, str] = _parse_voice_name(voice)
    download_dir.mkdir(parents=True, exist_ok=True)

    model_path: Path = download_dir / f"{voice}.onnx"
    config_path: Path = download_dir / f"{voice}.onnx.json"

    for extension, target in [(".onnx", model_path), (".onnx.json", config_path)]:
        if not _needs_download(target):
            logger.info("Файл уже существует: %s", target)
            continue

        url: str = _URL_FORMAT.format(extension=extension, **params)
        logger.info("Скачивание %s ...", url)

        try:
            with urlopen(url) as response, open(target, "wb") as out_file:
                shutil.copyfileobj(response, out_file)
        except URLError as exc:
            # Удаляем частично скачанный файл
            target.unlink(missing_ok=True)
            raise ConnectionError(
                f"Не удалось скачать '{voice}': {exc}"
            ) from exc

        logger.info("Сохранено: %s", target)

    return model_path


def list_voices() -> list[str]:
    """
    Загружает список всех доступных голосов из Hugging Face.

    :return: Отсортированный список имён голосов.
    :raises ConnectionError: Если не удалось получить список.
    """
    try:
        with urlopen(_VOICES_JSON_URL) as response:
            voices_dict: dict[str, object] = json.load(response)
    except URLError as exc:
        raise ConnectionError(
            f"Не удалось получить список голосов: {exc}"
        ) from exc

    return sorted(voices_dict.keys())
