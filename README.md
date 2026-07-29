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

download_voice("de_DE-thorsten-medium", VOICES_DIR)
```

## Запуск

```bash
python generate.py
```

Результат сохраняется в папку `output/` (например, `output/hallo_kinder.wav`).

## Список доступных голосов

```python
from utils.download import list_voices

for v in list_voices():
    print(v)
```

## Структура проекта

```
FUNTIK/
├── generate.py          # Точка входа
├── config.py            # Пути и настройки
├── requirements.txt
├── README.md
├── voices/              # Голосовые модели
├── text/                # Входные тексты
├── output/              # Результаты (wav)
└── utils/
    ├── download.py      # Скачивание моделей
    ├── synthesize.py    # Синтез речи
    └── helpers.py       # Вспомогательные функции
```
