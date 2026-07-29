# FUNTIK — Генерация речи

Два движка:
- **cartoon** — полудетский мультяшный голос (Edge TTS, нужен интернет)
- **piper** — локальный офлайн TTS

## Установка

```bash
pip install -r requirements.txt
```

## Запуск

1. Текст — в `generate.py`
2. Движок и голос — в `config.py` (`ENGINE = "cartoon"`)
3. Запуск:

```bash
python generate.py
```

Результат в `output/` (каждый раз новый файл с версией).

## Мультяшный голос (по умолчанию)

В `config.py`:

```python
ENGINE = "cartoon"
CARTOON_VOICE = "ru-RU-SvetlanaNeural"
CARTOON_PITCH = "+90Hz"   # выше = более детский
CARTOON_RATE = "+8%"
```

Подробности — в `ИНСТРУКЦИЯ.txt`.
