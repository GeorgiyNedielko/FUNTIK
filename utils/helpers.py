"""Вспомогательные функции: создание директорий, санитизация имён файлов."""

import logging
import re
from pathlib import Path

logger: logging.Logger = logging.getLogger(__name__)


def ensure_dirs(*dirs: Path) -> None:
    """Создаёт директории, если они не существуют."""
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        logger.debug("Директория готова: %s", d)


def sanitize_filename(text: str, max_length: int = 40) -> str:
    """Превращает произвольный текст в безопасное имя файла (латиница + цифры)."""
    name: str = text.strip().lower()
    # Оставляем только буквы, цифры, пробелы
    name = re.sub(r"[^\w\s]", "", name, flags=re.UNICODE)
    # Пробелы → подчёркивания
    name = re.sub(r"\s+", "_", name)
    # Обрезаем
    name = name[:max_length].rstrip("_")
    return name or "output"
