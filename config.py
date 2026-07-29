"""Конфигурация проекта FUNTIK — пути и параметры озвучки.

Все настройки редактируются здесь.

================================================================================
ПОЛНЫЙ СПИСОК НАСТРОЕК ГОЛОСА
================================================================================

1) ENGINE
   "cartoon" | "piper"

2) CARTOON (Edge TTS) — реально доступны ТОЛЬКО 4 параметра API:
   • voice   — какой голос
   • pitch   — высота тона (+NHz / -NHz)
   • rate    — скорость (+N% / -N%)
   • volume  — громкость (+N% / -N%)
   Стилей эмоций (happy/sad/excited) в Edge TTS НЕТ.

   Удобные ручки поверх API:
   • INTONATION    — детскость / высота
   • CHEERFULNESS  — веселье / энергия
   • CARTOON_VOICE / CARTOON_PITCH / CARTOON_RATE / CARTOON_VOLUME

3) PIPER (локально):
   • DEFAULT_VOICE, SPEECH_SPEED, INTONATION, VOLUME
   • SPLIT_SENTENCES, PAUSE_*, NOISE_SCALE, NOISE_W_SCALE
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Пути
# ---------------------------------------------------------------------------

BASE_DIR: Path = Path(__file__).resolve().parent
VOICES_DIR: Path = BASE_DIR / "voices"
TEXT_DIR: Path = BASE_DIR / "text"
OUTPUT_DIR: Path = BASE_DIR / "output"

# ---------------------------------------------------------------------------
# Движок
# Диапазон: "cartoon" | "piper"
# ---------------------------------------------------------------------------

ENGINE: str = "cartoon"

# ---------------------------------------------------------------------------
# Общие ручки настроения (для cartoon влияют сразу и слышно)
# ---------------------------------------------------------------------------

# Детскость / высота.
# Диапазон: мин. 0.0 … макс. 1.0
# Рекомендуется: 0.55–0.85
INTONATION: float = 0.80

# Веселье / энергия ★
# Диапазон: мин. 0.0 … макс. 1.0
# Рекомендуется: 0.70–0.95
# Выше → быстрее, звонче, чуть громче; точки в тексте → «!»
CHEERFULNESS: float = 0.90

# ===========================================================================
# CARTOON — Edge TTS (нужен интернет)
# API умеет только: voice, pitch, rate, volume
# ===========================================================================

# Голос.
# Диапазон:
#   "ru-RU-SvetlanaNeural" — женский, Friendly/Positive
#   "ru-RU-DmitryNeural"   — мужской, Friendly/Positive
# Других русских голосов в Edge TTS нет.
CARTOON_VOICE: str = "ru-RU-SvetlanaNeural"

# Ручной pitch. None = из INTONATION + CHEERFULNESS.
# Формат: "+110Hz"
# Диапазон: мин. "-50Hz" … макс. "+150Hz"
CARTOON_PITCH: str | None = None

# Ручная скорость. None = из INTONATION + CHEERFULNESS.
# Формат: "+18%"
# Диапазон: мин. "-50%" … макс. "+50%"
CARTOON_RATE: str | None = None

# Ручная громкость. None = из CHEERFULNESS.
# Формат: "+10%"
# Диапазон: мин. "-50%" … макс. "+50%"
CARTOON_VOLUME: str | None = None

# ===========================================================================
# PIPER — офлайн (ENGINE = "piper")
# ===========================================================================

DEFAULT_VOICE: str = "ru_RU-irina-medium"

# Скорость. Диапазон: мин. 0.50 … макс. 1.50
SPEECH_SPEED: float = 1.0

# Громкость. Диапазон: мин. 0.10 … макс. 2.00
VOLUME: float = 1.0

NORMALIZE_AUDIO: bool = True

SPLIT_SENTENCES: bool = False

# Паузы (сек). Диапазон: мин. 0.00 … макс. 2.00 / 3.00
PAUSE_AFTER_SENTENCE: float = 0.25
PAUSE_AFTER_PARAGRAPH: float = 0.70

# Тонкая настройка. None = из INTONATION.
# Диапазон: None или мин. 0.20 … макс. 1.00
NOISE_SCALE: float | None = None
NOISE_W_SCALE: float | None = None
