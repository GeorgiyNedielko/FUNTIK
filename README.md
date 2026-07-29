# FUNTIK — Генерация речи на базе Piper TTS

Локальный проект синтеза речи. Работает полностью офлайн (после скачивания модели).

## Установка

```bash
pip install -r requirements.txt
```

## Скачивание голосовой модели

Модель скачивается автоматически при первом запуске. Можно скачать вручную:

```python
from utils.download import download_voice
from config import VOICES_DIR

download_voice("ru_RU-irina-medium", VOICES_DIR)
```

## Запуск

1. Текст — в `generate.py` (переменная `text`)
2. Голос, скорость, выразительность, паузы — в `config.py`
3. Запуск:

```bash
python generate.py
```

Результат сохраняется в папку `output/`.

## Параметры озвучки (`config.py`)

| Параметр | Что делает |
|---|---|
| `DEFAULT_VOICE` | Голос (язык = язык текста) |
| `SPEECH_SPEED` | Скорость (`1.0` норма, `>1` быстрее) |
| `INTONATION` | Интонация / живость (`0.0`…`1.0`) |
| `VOLUME` | Громкость |
| `PAUSE_AFTER_SENTENCE` | Пауза после `. ! ?` (сек) |
| `PAUSE_AFTER_PARAGRAPH` | Пауза между абзацами (сек) |

Подробности — в файле `ИНСТРУКЦИЯ.txt`.

## Список всех голосов

```python
from utils.download import list_voices

for v in list_voices():
    print(v)
```

## Структура проекта

```
FUNTIK/
├── generate.py          # Текст + запуск
├── config.py            # Голос и параметры озвучки
├── requirements.txt
├── README.md
├── voices/              # Голосовые модели
├── text/
├── output/              # Результаты (wav)
└── utils/
    ├── download.py
    ├── synthesize.py
    └── helpers.py
```
