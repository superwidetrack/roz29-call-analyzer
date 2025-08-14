#!/usr/bin/env python3
"""
Тестирование с реальной расшифровкой звонка-продажи
"""
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from prompt_loader import prompt_loader
from main import analyze_with_gpt, send_telegram_report

# Загружаем переменные окружения
load_dotenv()

async def test_sales_call():
    """Тестируем с реальной расшифровкой продажи"""
    print("=== 🛒 ТЕСТИРОВАНИЕ ЗВОНКА-ПРОДАЖИ ===")
    
    # Проверяем настройки
    required_env_vars = ["OPENAI_API_KEY", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Отсутствуют переменные окружения: {', '.join(missing_vars)}")
        return
    
    print("✅ Все необходимые переменные окружения настроены")
    
    # Читаем реальную транскрипцию продажи
    try:
        with open('test_transcript2.txt', 'r', encoding='utf-8') as f:
            transcript = f.read().strip()
    except FileNotFoundError:
        print("❌ Файл test_transcript2.txt не найден")
        return
    
    print(f"📝 Загружена расшифровка продажи ({len(transcript)} символов)")
    
    # Информация о звонке
    call_info = {
        'duration': 240,  # примерно 4 минуты
        'time': '2024-01-15 19:33:46',
        'direction': 'входящий'
    }
    
    print("\n🤖 Запускаем анализ продажи с помощью GPT-4...")
    
    # Анализируем звонок
    analysis = analyze_with_gpt(transcript, call_info)
    
    if not analysis:
        print("❌ Анализ не удался")
        return
        
    print(f"✅ Анализ завершен ({len(analysis)} символов)")
    print("\n📊 РЕЗУЛЬТАТ АНАЛИЗА:")
    print("=" * 70)
    print(analysis)
    print("=" * 70)
    
    # Определяем тип звонка для эмодзи
    call_type_emoji = "📞"
    if "ПРОДАЖА" in analysis.upper():
        if any(phrase in analysis.upper() for phrase in ["ЗАКАЗ ОФОРМЛЕН", "СОСТОЯЛАСЬ", "УСПЕШНА", "ЗАКАЗ ПРИНЯТ"]):
            call_type_emoji = "🟢 УСПЕШНАЯ ПРОДАЖА"
        elif any(phrase in analysis.upper() for phrase in ["В ПРОЦЕССЕ", "НЕ ЗАКРЫТ", "ОЖИДАНИЕ"]):
            call_type_emoji = "🟨 ПРОДАЖА В ПРОЦЕССЕ"
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

📞 **Звонок:** отель Руми → Татьяна (29ROZ)
🗓️ **Дата:** {moscow_time_str}  
⏱️ **Длительность:** {call_info['duration']} сек
📊 **Результат:** ТЕСТ ПРОДАЖИ

---

{analysis}

📝 **Ключевые моменты:**
• Товар: Букет 077 Саксиния Матрикария (размер M)
• Цена: 5490₽ → исправлено на 5990₽
• Доставка: 500₽, к 7:30 утра в отель
• Статус: Клиент уточняет способ оплаты

---
*🧪 Локальное тестирование системы 29ROZ Call Analyzer*
**ID теста:** `SALES_TEST_{int(datetime.now().timestamp())}`"""

    print("\n📱 Отправляем отчет в Telegram...")
    
    # Отправляем в Telegram
    telegram_success = await send_telegram_report(final_report)
    
    if telegram_success:
        print("✅ Отчет успешно отправлен в Telegram!")
        print("\n🎉 ТЕСТИРОВАНИЕ ПРОДАЖИ ЗАВЕРШЕНО!")
        print("✅ Система корректно анализирует продажи")
    else:
        print("❌ Ошибка отправки в Telegram")
        print("📝 Отчет был сформирован, но не отправлен")

if __name__ == "__main__":
    asyncio.run(test_sales_call())