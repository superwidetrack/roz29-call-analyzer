#!/usr/bin/env python3
"""
Локальный тестовый скрипт для проверки системы анализа звонков.
"""
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from prompt_loader import prompt_loader
from main import analyze_with_gpt, send_telegram_report

# Загружаем переменные окружения
load_dotenv()

def test_prompt_system():
    """Тестируем систему промптов"""
    print("🧪 Тестирование системы промптов...")
    
    # Тестовая транскрипция
    test_transcript = """
    Менеджер: Алло, салон цветов 29ROZ, слушаю вас.
    Клиент: Здравствуйте, мне нужен букет на день рождения.
    Менеджер: Какой бюджет вы планируете?
    Клиент: До 3000 рублей.
    Менеджер: У нас есть красивые розы, 15 штук за 2800.
    Клиент: А хризантемы есть?
    Менеджер: Хризантем нет в наличии.
    Клиент: Ну тогда спасибо, до свидания.
    """
    
    # Тестовая информация о звонке
    test_call_info = {
        'duration': 45,
        'time': '2024-01-15 14:30',
        'direction': 'входящий'
    }
    
    # Генерируем промпт
    full_prompt = prompt_loader.get_full_analysis_prompt(test_transcript.strip(), test_call_info)
    
    print(f"✅ Промпт сгенерирован, длина: {len(full_prompt)} символов")
    print("📝 Начало промпта:")
    print(full_prompt[:500] + "...")
    return True

async def test_full_analysis(transcript, call_info=None):
    """Тестируем полный анализ звонка"""
    print("\n🤖 Запускаем полный анализ звонка...")
    
    # Анализируем с помощью GPT-4
    analysis = analyze_with_gpt(transcript, call_info)
    
    if not analysis:
        print("❌ Анализ не удался")
        return None
        
    print(f"✅ Анализ завершен ({len(analysis)} символов)")
    print("\n📊 РЕЗУЛЬТАТ АНАЛИЗА:")
    print("-" * 50)
    print(analysis)
    print("-" * 50)
    
    return analysis

async def test_telegram_report(analysis, call_info=None):
    """Тестируем отправку отчета в Telegram"""
    print("\n📱 Тестируем отправку в Telegram...")
    
    # Создаем финальный отчет
    call_type_emoji = "📞"
    if "ПРОДАЖА" in analysis:
        if "ЗАКАЗ ОФОРМЛЕН" in analysis:
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
    
    # Информация о тестовом звонке
    moscow_time_str = datetime.now().strftime("%d.%m.%Y %H:%M MSK")
    
    final_report = f"""{call_type_emoji}

📞 **Звонок:** ТЕСТОВЫЙ ЛОКАЛЬНЫЙ ЗАПУСК
🗓️ **Дата:** {moscow_time_str}
⏱️ **Длительность:** {call_info.get('duration', 'N/A') if call_info else 'N/A'} сек
📊 **Результат:** ТЕСТ

---

{analysis}

---
*🧪 Локальное тестирование системы 29ROZ Call Analyzer*
**ID теста:** `LOCAL_TEST_{int(datetime.now().timestamp())}`"""

    print("📝 ФИНАЛЬНЫЙ ОТЧЕТ:")
    print(final_report)
    
    # Отправляем в Telegram
    telegram_success = await send_telegram_report(final_report)
    
    if telegram_success:
        print("✅ Отчет успешно отправлен в Telegram!")
        return True
    else:
        print("❌ Ошибка отправки в Telegram")
        return False

async def main():
    """Главная функция тестирования"""
    print("=== 🧪 ЛОКАЛЬНОЕ ТЕСТИРОВАНИЕ СИСТЕМЫ АНАЛИЗА ЗВОНКОВ ===")
    
    # Проверяем настройки
    required_env_vars = ["OPENAI_API_KEY", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Отсутствуют переменные окружения: {', '.join(missing_vars)}")
        print("Убедитесь, что .env файл содержит все необходимые ключи")
        return
    
    print("✅ Все необходимые переменные окружения настроены")
    
    # Шаг 1: Тестируем систему промптов
    if not test_prompt_system():
        print("❌ Ошибка в системе промптов")
        return
    
    # Ждем ввода транскрипции от пользователя
    print("\n" + "="*60)
    print("📝 ВВЕДИТЕ ТРАНСКРИПЦИЮ ЗВОНКА ДЛЯ ТЕСТИРОВАНИЯ:")
    print("(Вставьте текст диалога и нажмите Enter дважды для завершения)")
    print("="*60)
    
    transcript_lines = []
    empty_lines = 0
    
    while True:
        try:
            line = input()
            if line.strip():
                transcript_lines.append(line)
                empty_lines = 0
            else:
                empty_lines += 1
                if empty_lines >= 2 or not transcript_lines:  # Две пустые строки или первая пустая
                    break
        except KeyboardInterrupt:
            print("\n❌ Тестирование прервано пользователем")
            return
        except EOFError:
            break
    
    if not transcript_lines:
        print("❌ Транскрипция не введена")
        return
    
    transcript = "\n".join(transcript_lines)
    
    # Информация о тестовом звонке
    test_call_info = {
        'duration': len(transcript) // 10,  # Примерная длительность
        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'direction': 'входящий'
    }
    
    print(f"\n✅ Получена транскрипция ({len(transcript)} символов)")
    
    # Шаг 2: Анализируем звонок
    analysis = await test_full_analysis(transcript, test_call_info)
    
    if not analysis:
        print("❌ Тестирование прервано из-за ошибки анализа")
        return
    
    # Шаг 3: Отправляем в Telegram
    success = await test_telegram_report(analysis, test_call_info)
    
    if success:
        print("\n🎉 ЛОКАЛЬНОЕ ТЕСТИРОВАНИЕ УСПЕШНО ЗАВЕРШЕНО!")
        print("✅ Все компоненты системы работают корректно")
    else:
        print("\n⚠️ Тестирование завершено с предупреждениями")

if __name__ == "__main__":
    asyncio.run(main())