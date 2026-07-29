"""Конфигурация FUNTIK — ВСЕ параметры редактируются вручную здесь.

Меняете значение → сохраняете → Run generate.py
Текст для озвучки: generate.py → переменная text
"""

from pathlib import Path

# ===========================================================================
# ПУТИ
# ===========================================================================

BASE_DIR: Path = Path(__file__).resolve().parent
VOICES_DIR: Path = BASE_DIR / "voices"
TEXT_DIR: Path = BASE_DIR / "text"
OUTPUT_DIR: Path = BASE_DIR / "output"

# ===========================================================================
# ДВИЖОК
# Диапазон: "cartoon" | "piper"
# cartoon = Edge TTS (интернет), piper = локальный офлайн
# ===========================================================================

ENGINE: str = "cartoon"

# ===========================================================================
# НАСТРОЕНИЕ (удобные ручки 0..1)
# ===========================================================================

# Детскость / высота.
# Диапазон: мин. 0.0 … макс. 1.0
INTONATION: float = 0.80

# Веселье / энергия.
# Диапазон: мин. 0.0 … макс. 1.0
CHEERFULNESS: float = 0.90

# Заменять точки на «!» при высоком веселье.
# Диапазон: True | False
CHEER_REWRITE_DOTS: bool = True
# С какого CHEERFULNESS включать замену.
# Диапазон: мин. 0.0 … макс. 1.0
CHEER_REWRITE_THRESHOLD: float = 0.55

# ===========================================================================
# CARTOON — Edge TTS (нужен интернет)
# API: только voice / pitch / rate / volume
# Если CARTOON_PITCH/RATE/VOLUME = None → считаются автоматически
# из INTONATION + CHEERFULNESS (формула ниже).
# Если задать строку вручную — она ПОЛНОСТЬЮ перебивает авто.
# ===========================================================================

# Голос.
# Диапазон: "ru-RU-SvetlanaNeural" | "ru-RU-DmitryNeural"
CARTOON_VOICE: str = "ru-RU-SvetlanaNeural"

# Ручной pitch. Пример: "+110Hz". None = авто.
# Диапазон: мин. "-50Hz" … макс. "+150Hz"
CARTOON_PITCH: str | None = None

# Ручная скорость. Пример: "+18%". None = авто.
# Диапазон: мин. "-50%" … макс. "+50%"
CARTOON_RATE: str | None = None

# Ручная громкость. Пример: "+10%". None = авто.
# Диапазон: мин. "-50%" … макс. "+50%"
CARTOON_VOLUME: str | None = None

# --- Формула авто (если выше None) ---
# pitch_hz = PITCH_MIN + INTONATION * PITCH_BY_INT + CHEERFULNESS * PITCH_BY_CHEER
# Диапазон Hz: мин. 0 … макс. 150
CARTOON_AUTO_PITCH_MIN_HZ: float = 35.0
CARTOON_AUTO_PITCH_BY_INTONATION_HZ: float = 70.0
CARTOON_AUTO_PITCH_BY_CHEER_HZ: float = 40.0
CARTOON_AUTO_PITCH_MAX_HZ: float = 150.0

# rate% = INTONATION * RATE_BY_INT + CHEERFULNESS * RATE_BY_CHEER
# Диапазон %: мин. 0 … макс. 50
CARTOON_AUTO_RATE_BY_INTONATION_PCT: float = 10.0
CARTOON_AUTO_RATE_BY_CHEER_PCT: float = 20.0
CARTOON_AUTO_RATE_MAX_PCT: float = 40.0

# volume% = CHEERFULNESS * VOLUME_BY_CHEER
# Диапазон %: мин. 0 … макс. 50
CARTOON_AUTO_VOLUME_BY_CHEER_PCT: float = 15.0
CARTOON_AUTO_VOLUME_MAX_PCT: float = 50.0

# ===========================================================================
# PIPER — офлайн (ENGINE = "piper")
# ===========================================================================

# Голос Piper.
# Диапазон: ru_RU-irina-medium | ru_RU-dmitri-medium |
#           ru_RU-denis-medium | ru_RU-ruslan-medium
DEFAULT_VOICE: str = "ru_RU-irina-medium"

# Скорость. Диапазон: мин. 0.50 … макс. 1.50
SPEECH_SPEED: float = 1.0

# Громкость. Диапазон: мин. 0.10 … макс. 2.00
VOLUME: float = 1.0

# Нормализация Piper. Диапазон: True | False
NORMALIZE_AUDIO: bool = True

# Резать по предложениям. Диапазон: True | False
SPLIT_SENTENCES: bool = False

# Пауза после предложения (сек). Диапазон: мин. 0.00 … макс. 2.00
PAUSE_AFTER_SENTENCE: float = 0.25

# Пауза между абзацами (сек). Диапазон: мин. 0.00 … макс. 3.00
PAUSE_AFTER_PARAGRAPH: float = 0.70

# Тонкая настройка Piper. None = из INTONATION.
# Диапазон: None или мин. 0.20 … макс. 1.00
NOISE_SCALE: float | None = None
NOISE_W_SCALE: float | None = None

# ===========================================================================
# ПОСТОБРАБОТКА WAV (детский канал) — после cartoon и piper
# ===========================================================================

# Включить всю постобработку. Диапазон: True | False
POSTPROCESS_ENABLED: bool = True

# --- Компрессор ---
# Диапазон: True | False
POST_COMPRESSOR: bool = True
# Порог дБ. Диапазон: мин. -40.0 … макс. -6.0
POST_COMPRESSOR_THRESHOLD_DB: float = -18.0
# Степень сжатия. Диапазон: мин. 1.5 … макс. 6.0
POST_COMPRESSOR_RATIO: float = 3.0
# Атака мс. Диапазон: мин. 1.0 … макс. 50.0
POST_COMPRESSOR_ATTACK_MS: float = 8.0
# Релиз мс. Диапазон: мин. 20.0 … макс. 300.0
POST_COMPRESSOR_RELEASE_MS: float = 80.0

# --- EQ ---
# Диапазон: True | False
POST_EQ: bool = True
# High-shelf частота Гц. Диапазон: мин. 2000 … макс. 8000
POST_EQ_HIGHSHELF_HZ: float = 4200.0
# High-shelf усиление дБ. Диапазон: мин. 0.0 … макс. 8.0
POST_EQ_HIGHSHELF_GAIN_DB: float = 3.5
# Presence частота Гц. Диапазон: мин. 1500 … макс. 5000
POST_EQ_PRESENCE_HZ: float = 3000.0
# Presence усиление дБ. Диапазон: мин. 0.0 … макс. 6.0
POST_EQ_PRESENCE_GAIN_DB: float = 2.0
# Presence Q. Диапазон: мин. 0.3 … макс. 5.0
POST_EQ_PRESENCE_Q: float = 1.0

# --- Нормализация ---
# Диапазон: True | False
POST_NORMALIZE: bool = True
# Целевой пик дБ. Диапазон: мин. -6.0 … макс. -0.1
POST_NORMALIZE_PEAK_DB: float = -1.0

# --- Лимитер ---
# Диапазон: True | False
POST_LIMITER: bool = True
# Порог дБ. Диапазон: мин. -6.0 … макс. -0.1
POST_LIMITER_THRESHOLD_DB: float = -1.0
# Релиз мс. Диапазон: мин. 10.0 … макс. 200.0
POST_LIMITER_RELEASE_MS: float = 50.0

# --- Паузы ---
# Диапазон: True | False
POST_TRIM_SILENCE: bool = True
# Порог тишины дБ. Диапазон: мин. -60.0 … макс. -20.0
POST_SILENCE_THRESHOLD_DB: float = -40.0
# Макс. пауза сек. Диапазон: мин. 0.05 … макс. 1.00
POST_MAX_SILENCE_SEC: float = 0.28
# Размер кадра анализа мс. Диапазон: мин. 5.0 … макс. 50.0
POST_SILENCE_FRAME_MS: float = 20.0

# --- Fade ---
# Диапазон: True | False
POST_FADES: bool = True
# Fade-in сек. Диапазон: мин. 0.0 … макс. 0.20
POST_FADE_IN_SEC: float = 0.025
# Fade-out сек. Диапазон: мин. 0.0 … макс. 0.20
POST_FADE_OUT_SEC: float = 0.040

# --- Pitch shift (полутона) ---
# Диапазон: True | False
POST_PITCH_SHIFT: bool = True
# Сдвиг. Диапазон: мин. -6.0 … макс. 6.0
# cartoon: обычно 0.5–1.2; piper: 1.5–2.5
POST_PITCH_SEMITONES: float = 1.2
