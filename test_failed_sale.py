#!/usr/bin/env python3
"""
Тестирование с реальной расшифровкой неудачной продажи
"""
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from prompt_loader import prompt_loader
from main import analyze_with_gpt, send_telegram_report

# Загружаем переменные окружения
load_dotenv()

async def test_failed_sale():
    """Тестируем с реальной расшифровкой неудачной продажи"""
    print("=== 🔴 ТЕСТИРОВАНИЕ НЕУДАЧНОЙ ПРОДАЖИ ===")
    
    # Проверяем настройки
    required_env_vars = ["OPENAI_API_KEY", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Отсутствуют переменные окружения: {', '.join(missing_vars)}")
        return
    
    print("✅ Все необходимые переменные окружения настроены")
    
    # Читаем реальную транскрипцию неудачной продажи
    try:
        with open('test_transcript3.txt', 'r', encoding='utf-8') as f:
            transcript = f.read().strip()
    except FileNotFoundError:
        print("❌ Файл test_transcript3.txt не найден")
        return
    
    print(f"📝 Загружена расшифровка неудачной продажи ({len(transcript)} символов)")
    print("👀 Ожидаем выявление ошибки M1 - не предложил альтернативу")
    
    # Информация о звонке
    call_info = {
        'duration': 60,  # примерно 1 минута - короткий звонок
        'time': '2024-01-15 20:36:05',
        'direction': 'исходящий'
    }
    
    print("\n🤖 Запускаем анализ неудачной продажи...")
    
    # Анализируем звонок
    analysis = analyze_with_gpt(transcript, call_info)
    
    if not analysis:
        print("❌ Анализ не удался")
        return
        
    print(f"✅ Анализ завершен ({len(analysis)} символов)")
    print("\n📊 РЕЗУЛЬТАТ АНАЛИЗА:")
    print("=" * 80)
    print(analysis)
    print("=" * 80)
    
    # Проверяем, выявил ли анализ ошибку M1
    if "M1" in analysis:
        print("\n🎯 ✅ ОТЛИЧНО! Система правильно выявила ошибку M1!")
    elif "MANAGER_FAULT" in analysis:
        print("\n🎯 ✅ Система выявила ошибку менеджера!")
    else:
        print("\n⚠️ Возможно, система не выявила ошибку менеджера")
    
    # Определяем тип звонка для эмодзи
    call_type_emoji = "🔴 НЕУДАЧНАЯ ПРОДАЖА"
    
    # Создаем финальный отчет
    moscow_time_str = datetime.now().strftime("%d.%m.%Y %H:%M MSK")
    
    final_report = f"""{call_type_emoji}

📞 **Звонок:** 29ROZ → клиент (повторный)
🗓️ **Дата:** {moscow_time_str}  
⏱️ **Длительность:** {call_info['duration']} сек
📊 **Результат:** ПОТЕРЯННАЯ ПРОДАЖА

---

{analysis}

📝 **Контекст звонка:**
• Повторный звонок по поводу букета
• Клиент хотел что-то кроме розовых роз
• Менеджер: "к сожалению, в наличии рос нету"
• Результат: клиент отказался и ушел

---
*🧪 Локальное тестирование системы 29ROZ Call Analyzer*
**ID теста:** `FAILED_SALE_TEST_{int(datetime.now().timestamp())}`"""

    print("\n📱 Отправляем отчет в Telegram...")
    
    # Отправляем в Telegram
    telegram_success = await send_telegram_report(final_report)
    
    if telegram_success:
        print("✅ Отчет успешно отправлен в Telegram!")
        print("\n🎉 ТЕСТИРОВАНИЕ НЕУДАЧНОЙ ПРОДАЖИ ЗАВЕРШЕНО!")
        
        # Проверяем качество анализа
        if "M1" in analysis:
            print("🎯 ✅ СИСТЕМА РАБОТАЕТ ИДЕАЛЬНО!")
            print("   → Правильно выявила ошибку M1: не предложил альтернативу")
        print("✅ Система готова выявлять ошибки менеджеров в реальных звонках")
    else:
        print("❌ Ошибка отправки в Telegram")
        print("📝 Отчет был сформирован, но не отправлен")

if __name__ == "__main__":
    asyncio.run(test_failed_sale())