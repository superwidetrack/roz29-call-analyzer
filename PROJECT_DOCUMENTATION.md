# 29ROZ Call Analyzer - Полная документация проекта

## 🎯 Обзор проекта
**Название:** Автоматический анализатор звонков для цветочного магазина "29ROZ"
**Heroku App:** `roz29-call-analyzer`
**URL:** https://roz29-call-analyzer-4a23b521feb5.herokuapp.com/
**GitHub ветка:** `devin/1753613763-telphin-api-integration`

## 🏗️ Архитектура системы

### Основные компоненты:
1. **Telphin API** - получение списка звонков и загрузка записей
2. **Yandex SpeechKit** - транскрипция коротких записей (≤30 сек)
3. **OpenAI Whisper** - fallback для длинных записей (>30 сек)
4. **GPT-4o** - двухэтапный анализ разговоров
5. **Telegram Bot** - отправка отчетов
6. **Heroku Scheduler** - автоматический запуск каждые 10 минут

### Поток данных:
```
Heroku Scheduler (каждые 10 мин)
    ↓
Telphin API (получение звонков за последний час)
    ↓
Фильтрация (только входящие с записями)
    ↓
Загрузка аудиозаписей
    ↓
Транскрипция (Yandex SpeechKit или OpenAI Whisper)
    ↓
Анализ GPT-4o (классификация + детальный анализ)
    ↓
Отправка отчета в Telegram
    ↓
Сохранение ID обработанного звонка
```

## 📁 Структура проекта

```
call_analyzer/
├── main.py                    # Основная логика системы
├── requirements.txt           # Python зависимости
├── Dockerfile                # Контейнеризация для Heroku
├── Procfile                  # Heroku процессы
├── .env                      # Локальные переменные окружения
├── .env.template             # Шаблон для переменных
├── processed_calls.txt       # Отслеживание обработанных звонков
├── README.md                 # Базовая документация
├── .gitignore               # Git исключения
└── test_*.py                # Тестовые скрипты
```

## 🔑 Переменные окружения

### Локальный .env файл:
```env
# Telphin API credentials
TELFIN_HOSTNAME=apiproxy.telphin.ru
TELFIN_LOGIN=45e44eaf13a6477b97b9b4cbe639b6ec
TELFIN_PASSWORD=53f52703b56743948ed1af0f1ad8a144

# Yandex SpeechKit API
YANDEX_API_KEY=your_yandex_api_key_here

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Telegram Bot
TELEGRAM_BOT_TOKEN=8266652973:AAFqGFfYU33KpMX7O8Bsf7iBBlFwxjJ-Ovs
TELEGRAM_CHAT_ID=6297431944
```

### Heroku Config Vars:
```bash
# Проверить текущие переменные:
heroku config --app roz29-call-analyzer

# Установить переменную:
heroku config:set VARIABLE_NAME="value" --app roz29-call-analyzer
```

## 🚀 Развертывание на Heroku

### Первоначальная настройка:
```bash
# 1. Создание приложения
heroku create roz29-call-analyzer

# 2. Установка переменных окружения
heroku config:set TELFIN_HOSTNAME="apiproxy.telphin.ru" --app roz29-call-analyzer
heroku config:set TELFIN_LOGIN="45e44eaf13a6477b97b9b4cbe639b6ec" --app roz29-call-analyzer
heroku config:set TELFIN_PASSWORD="53f52703b56743948ed1af0f1ad8a144" --app roz29-call-analyzer
heroku config:set YANDEX_API_KEY="your_yandex_api_key" --app roz29-call-analyzer
heroku config:set OPENAI_API_KEY="your_openai_api_key" --app roz29-call-analyzer
heroku config:set TELEGRAM_BOT_TOKEN="8266652973:AAFqGFfYU33KpMX7O8Bsf7iBBlFwxjJ-Ovs" --app roz29-call-analyzer
heroku config:set TELEGRAM_CHAT_ID="6297431944" --app roz29-call-analyzer

# 3. Развертывание через Container Registry
heroku container:push web --app roz29-call-analyzer
heroku container:release web --app roz29-call-analyzer

# 4. Настройка Scheduler
heroku addons:create scheduler:standard --app roz29-call-analyzer
heroku addons:open scheduler --app roz29-call-analyzer
# В веб-интерфейсе добавить задачу: "python main.py scheduler" каждые 10 минут
```

### Обновление кода:
```bash
# Аутентификация
export HEROKU_API_KEY="your_heroku_api_key_here"

# Развертывание изменений
heroku container:push web --app roz29-call-analyzer
heroku container:release web --app roz29-call-analyzer
```

## 📊 Мониторинг и логи

### Просмотр логов:
```bash
# Реальное время
heroku logs --tail --app roz29-call-analyzer

# Последние логи
heroku logs --app roz29-call-analyzer

# Логи Scheduler
heroku logs --source scheduler --app roz29-call-analyzer
```

### Ключевые метрики:
- **Частота запуска:** каждые 10 минут
- **Временное окно:** 1 час (TIME_WINDOW_HOURS=1)
- **Часовой пояс:** Московское время (UTC+3) для отчетов, UTC для API
- **Фильтрация:** только входящие звонки с duration > 0

## 🔧 Основные функции (main.py)

### Аутентификация:
```python
def authenticate_telfin(hostname, login, password)
```

### Получение звонков:
```python
def get_recent_calls(hostname, token)
def get_call_cdr(hostname, token, call_uuid)
```

### Обработка аудио:
```python
def download_recording(hostname, token, call_uuid, cdr_data)
def transcribe_with_yandex(audio_data)
def transcribe_with_openai_whisper(audio_data)
```

### Анализ:
```python
def analyze_with_gpt(transcript, call_info)
```

### Отчеты:
```python
def send_telegram_report(bot_token, chat_id, report, call_info)
```

### Отслеживание:
```python
def load_processed_calls()
def save_processed_call(call_id, status)
```

## 🎯 Логика фильтрации звонков

Система обрабатывает только звонки, которые соответствуют всем критериям:
1. **Входящие звонки:** `flow == 'in'`
2. **С аудиозаписью:** `duration > 0 or bridged_duration > 0`
3. **В временном окне:** последний час от текущего времени
4. **Не обработанные ранее:** ID отсутствует в processed_calls.txt

## 📋 Двухэтапный анализ GPT-4o

### Этап 1 - Классификация:
- **ПРОДАЖА** - заказ цветов/букетов
- **ЛОГИСТИКА** - вопросы доставки
- **ПОДДЕРЖКА** - жалобы/возвраты
- **НЕДОЗВОН** - сброшенный звонок

### Этап 2 - Детальный анализ:
- Качество обслуживания (1-10)
- Ключевые моменты разговора
- Рекомендации по улучшению
- Извлечение номеров телефонов

## 🔍 Диагностика проблем

### Проверка API ключей:
```bash
python test_openai_key.py
python test_telegram_bot.py
```

### Анализ звонков:
```bash
python diagnose_calls.py
python debug_1hour_filtering.py
```

### Тестирование фильтрации:
```bash
python test_filtering.py
```

## 📱 Telegram Bot

**Имя бота:** Анализатор звонков 29ROZ (@call_analyzer_29roz_bot)
**Token:** 8266652973:AAFqGFfYU33KpMX7O8Bsf7iBBlFwxjJ-Ovs
**Chat ID:** 6297431944

### Формат отчета:
```
🌹 АНАЛИЗ ЗВОНКА 29ROZ

📞 Информация о звонке:
• Дата: 14.08.2025 19:33 MSK
• Длительность: 2:27
• Тип: Входящий
• Номер: +7XXXXXXXXXX

📊 Классификация: ПРОДАЖА

🎯 Анализ качества: 8/10

📝 Ключевые моменты:
[Детальный анализ разговора]

💡 Рекомендации:
[Рекомендации по улучшению]
```

## 🛠️ Техническая информация

### Зависимости (requirements.txt):
```
requests==2.31.0
python-dotenv==1.0.0
openai==1.35.15
pytz==2023.3
pydub==0.25.1
```

### Dockerfile:
- Базовый образ: python:3.11-slim
- Установка ffmpeg для обработки аудио
- Копирование кода и установка зависимостей
- Команда по умолчанию: python app.py

### Heroku Scheduler:
- **Команда:** `python main.py scheduler`
- **Частота:** каждые 10 минут
- **Часовой пояс:** UTC

## 🔄 Жизненный цикл обработки

1. **Scheduler запуск** (каждые 10 мин)
2. **Аутентификация** в Telphin API
3. **Получение звонков** за последний час
4. **Фильтрация** входящих с записями
5. **Проверка** на дублирование (processed_calls.txt)
6. **Загрузка** аудиозаписи
7. **Транскрипция** (Yandex/OpenAI)
8. **Анализ** GPT-4o (2 этапа)
9. **Отправка** отчета в Telegram
10. **Сохранение** ID как обработанного

## 🚨 Критические исправления

### История багов:
1. **Бесконечный цикл GPT-4** (224 запроса) - исправлен отслеживанием ID
2. **Неправильный часовой пояс** - исправлен конвертацией в UTC для API
3. **Недействительный OpenAI ключ** - исправлен обновлением Heroku config

### Текущий статус:
✅ Все критические баги исправлены
✅ Система работает стабильно в продакшене
✅ Telegram сообщения доставляются корректно

## 📞 Контакты и доступы

**Heroku API Key:** [Contact admin for access]
**GitHub:** superwidetrack/telfin-call-analyzer
**Пользователь:** Alexander Voronin (@superwidetrack)

---

*Документация создана: 14 августа 2025*
*Версия системы: Release v19*
*Статус: Полностью функциональна*
