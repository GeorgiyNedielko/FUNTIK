"""Конфигурация проекта FUNTIK — пути и настройки по умолчанию."""

from pathlib import Path

# Корневая директория проекта
BASE_DIR: Path = Path(__file__).resolve().parent

# Папка для голосовых моделей (.onnx + .onnx.json)
VOICES_DIR: Path = BASE_DIR / "voices"

# Папка для входных текстов (опционально)
TEXT_DIR: Path = BASE_DIR / "text"

# Папка для сгенерированных wav-файлов
OUTPUT_DIR: Path = BASE_DIR / "output"

# Голос по умолчанию
DEFAULT_VOICE: str = "de_DE-thorsten-medium"
