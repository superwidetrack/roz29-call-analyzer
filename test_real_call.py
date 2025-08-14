#!/usr/bin/env python3
"""
Тестирование с реальной расшифровкой звонка
"""
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from prompt_loader import prompt_loader
from main import analyze_with_gpt, send_telegram_report

# Загружаем переменные окружения
load_dotenv()

async def test_real_call():
    """Тестируем с реальной расшифровкой"""
    print("=== 🧪 ТЕСТИРОВАНИЕ С РЕАЛЬНОЙ РАСШИФРОВКОЙ ===")
    
    # Проверяем настройки
    required_env_vars = ["OPENAI_API_KEY", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Отсутствуют переменные окружения: {', '.join(missing_vars)}")
        return
    
    print("✅ Все необходимые переменные окружения настроены")
    
    # Читаем реальную транскрипцию
    try:
        with open('test_transcript.txt', 'r', encoding='utf-8') as f:
            transcript = f.read().strip()
    except FileNotFoundError:
        print("❌ Файл test_transcript.txt не найден")
        return
    
    print(f"📝 Загружена расшифровка ({len(transcript)} символов)")
    
    # Информация о звонке
    call_info = {
        'duration': 180,  # примерно 3 минуты
        'time': '2024-01-15 19:37:56',
        'direction': 'исходящий'
    }
    
    print("\n🤖 Запускаем анализ с помощью GPT-4...")
    
    # Анализируем звонок
    analysis = analyze_with_gpt(transcript, call_info)
    
    if not analysis:
        print("❌ Анализ не удался")
        return
        
    print(f"✅ Анализ завершен ({len(analysis)} символов)")
    print("\n📊 РЕЗУЛЬТАТ АНАЛИЗА:")
    print("=" * 60)
    print(analysis)
    print("=" * 60)
    
    # Определяем тип звонка для эмодзи
    call_type_emoji = "📞"
    if "ПРОДАЖА" in analysis:
        if "ЗАКАЗ ОФОРМЛЕН" in analysis or "СОСТОЯЛАСЬ" in analysis:
            call_type_emoji = "🟢 УСПЕШНАЯ ПРОДАЖА"
        else:
            call_type_emoji = "🔴 НЕУДАЧНАЯ ПРОДАЖА"
    elif "ЛОГИСТИКА" in analysis:
        call_type_emoji = "🚚 ЛОГИСТИКА"
    elif "ПОДДЕРЖКА" in analysis:
        call_type_emoji = "🛠️ ПОДДЕРЖКА"
    elif "НЕДОЗВОН" in analysis or "ОШИБКА" in analysis:
        call_type_emoji = "❌ НЕДОЗВОН/ОШИБКА"
    elif "ДРУГОЕ" in analysis:
        call_type_emoji = "📋 ДРУГОЕ"
    
    # Создаем финальный отчет
    moscow_time_str = datetime.now().strftime("%d.%m.%Y %H:%M MSK")
    
    final_report = f"""{call_type_emoji}

📞 **Звонок:** Татьяна (29ROZ) → отель Рум
🗓️ **Дата:** {moscow_time_str}
⏱️ **Длительность:** {call_info['duration']} сек
📊 **Результат:** ТЕСТ РЕАЛЬНОЙ РАСШИФРОВКИ

---

{analysis}

📝 **Фрагмент транскрипции:**
```
29 Рот, здравствуйте, меня зовут Татьяна...
Доставка в руме завтра к 7:30...
Спасибо вам за заказ, до свидания...
```

---
*🧪 Локальное тестирование системы 29ROZ Call Analyzer*
**ID теста:** `REAL_CALL_TEST_{int(datetime.now().timestamp())}`"""

    print("\n📱 Отправляем отчет в Telegram...")
    
    # Отправляем в Telegram
    telegram_success = await send_telegram_report(final_report)
    
    if telegram_success:
        print("✅ Отчет успешно отправлен в Telegram!")
        print("\n🎉 ТЕСТИРОВАНИЕ УСПЕШНО ЗАВЕРШЕНО!")
        print("✅ Система анализа работает корректно с реальными данными")
    else:
        print("❌ Ошибка отправки в Telegram")
        print("📝 Отчет был сформирован, но не отправлен")

if __name__ == "__main__":
    asyncio.run(test_real_call())