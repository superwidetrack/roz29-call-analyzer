#!/usr/bin/env python3
"""
Тест новой системы анализа с фокусом на критических ошибках
"""
import os
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv
from prompt_loader import prompt_loader
from main import analyze_with_gpt_new, send_telegram_report

# Загружаем переменные окружения
load_dotenv()

async def test_new_critical_system():
    """Тестируем новую систему с разными типами звонков"""
    print("=== 🚨 ТЕСТИРОВАНИЕ НОВОЙ СИСТЕМЫ КРИТИЧЕСКИХ ОШИБОК ===")
    
    # Проверяем настройки
    required_env_vars = ["OPENAI_API_KEY", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Отсутствуют переменные окружения: {', '.join(missing_vars)}")
        return
    
    print("✅ Все необходимые переменные окружения настроены")
    
    # Перезагружаем промпты для актуальности
    print("🔄 Перезагружаем промпты...")
    prompt_loader.reload_prompts()
    
    # Тестовые звонки разных типов
    test_calls = [
        {
            "name": "❌ КРИТИЧЕСКАЯ ОШИБКА M1",
            "transcript": """
            Клиент: Здравствуйте, мне нужен букет хризантем для мамы.
            Менеджер: Здравствуйте! К сожалению, хризантем у нас сейчас нет.
            Клиент: А что у вас есть?
            Менеджер: Розы есть красивые.
            Клиент: Не, мне именно хризантемы нужны. До свидания.
            Менеджер: До свидания.
            """,
            "expected": "alert",
            "description": "Менеджер не предложил альтернативу при отсутствии товара"
        },
        {
            "name": "✅ УСПЕШНАЯ ПРОДАЖА",  
            "transcript": """
            Менеджер: 29ROZ, здравствуйте!
            Клиент: Нужен букет роз на день рождения.
            Менеджер: Конечно, сколько роз и какой бюджет?
            Клиент: 21 роза, до 4000 рублей.
            Менеджер: Отлично, у нас есть букет 21 роза за 3800. Оформляем?
            Клиент: Да, оформляем. Когда доставка?
            Менеджер: Завтра к 18:00. Ваш телефон для курьера?
            Клиент: 89991234567
            Менеджер: Принято! Спасибо за заказ!
            """,
            "expected": "ignore",
            "description": "Успешная продажа - не требует вмешательства"
        },
        {
            "name": "🚚 ЛОГИСТИКА",
            "transcript": """
            Менеджер: Добрый день! Это 29ROZ, звоним уточнить время доставки.
            Клиент: Да, привет!
            Менеджер: Ваш заказ готов, удобно ли к 17:00?
            Клиент: Да, удобно. Спасибо!
            Менеджер: Отлично, курьер будет к 17:00. Хорошего дня!
            """,
            "expected": "ignore", 
            "description": "Логистический звонок - не требует анализа"
        },
        {
            "name": "❌ КРИТИЧЕСКАЯ ОШИБКА M3",
            "transcript": """
            Клиент: Здравствуйте, хочу заказать букет.
            Менеджер: Здравствуйте! Какой букет вас интересует?
            Клиент: 25 роз, красные.
            Менеджер: Есть, 4500 рублей. Подходит?
            Клиент: Да, подходит. А доставка?
            Менеджер: 500 рублей, завтра доставим.
            Клиент: Хорошо, мне подходит.
            Менеджер: Отлично! Я вам перезвоню завтра утром, уточню детали.
            Клиент: Хорошо, жду звонка.
            """,
            "expected": "alert",
            "description": "Менеджер не закрыл сделку в один контакт"
        }
    ]
    
    print(f"\n🧪 Запускаем тестирование {len(test_calls)} сценариев...")
    
    results = []
    critical_count = 0
    
    for i, test_call in enumerate(test_calls, 1):
        print(f"\n{'='*60}")
        print(f"ТЕСТ {i}/4: {test_call['name']}")
        print(f"ОПИСАНИЕ: {test_call['description']}")
        print("="*60)
        
        # Анализируем звонок
        call_info = {
            'duration': 120,
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'direction': 'incoming'
        }
        
        result = analyze_with_gpt_new(test_call['transcript'].strip(), call_info)
        
        if result:
            status = result.get('status', 'unknown')
            print(f"📋 РЕЗУЛЬТАТ АНАЛИЗА: status = '{status}'")
            
            if status == 'alert':
                print(f"🚨 КРИТИЧЕСКАЯ ОШИБКА ОБНАРУЖЕНА!")
                print(f"   Код: {result.get('error_code', 'N/A')}")
                print(f"   Описание: {result.get('error_description', 'N/A')}")
                print(f"   Контекст: {result.get('context', 'N/A')}")
                print(f"   Решение: {result.get('solution', 'N/A')}")
                
                # Создаём тестовый отчёт
                alert_template = prompt_loader.get_alert_template()
                test_report = alert_template.format(
                    error_code=result.get('error_code', 'TEST'),
                    error_description=result.get('error_description', 'Test error'),
                    client_phone='TEST_PHONE',
                    context=result.get('context', 'Test context'),
                    solution=result.get('solution', 'Test solution')
                )
                
                print(f"\n📱 ОТПРАВЛЯЕМ ТЕСТОВЫЙ ОТЧЁТ В TELEGRAM...")
                telegram_success = await send_telegram_report(test_report)
                
                if telegram_success:
                    print("✅ Отчёт отправлен в Telegram!")
                    critical_count += 1
                else:
                    print("❌ Ошибка отправки отчёта")
                    
            elif status == 'ignore':
                print(f"✅ Звонок не требует вмешательства")
            else:
                print(f"⚠️ Неожиданный статус: {status}")
            
            # Проверяем ожидаемый результат
            if status == test_call['expected']:
                print(f"✅ ТЕСТ ПРОЙДЕН: ожидался '{test_call['expected']}', получен '{status}'")
                results.append({"test": test_call['name'], "status": "PASS", "result": status})
            else:
                print(f"❌ ТЕСТ НЕ ПРОЙДЕН: ожидался '{test_call['expected']}', получен '{status}'")
                results.append({"test": test_call['name'], "status": "FAIL", "result": status})
        else:
            print("❌ Ошибка анализа")
            results.append({"test": test_call['name'], "status": "ERROR", "result": "no_result"})
    
    # Итоги тестирования
    print(f"\n{'='*80}")
    print("🏁 ИТОГИ ТЕСТИРОВАНИЯ НОВОЙ СИСТЕМЫ")
    print("="*80)
    
    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = sum(1 for r in results if r['status'] == 'FAIL')
    errors = sum(1 for r in results if r['status'] == 'ERROR')
    
    print(f"✅ ПРОЙДЕНО: {passed}/{len(results)} тестов")
    print(f"❌ НЕ ПРОЙДЕНО: {failed}/{len(results)} тестов")
    print(f"💥 ОШИБОК: {errors}/{len(results)} тестов")
    print(f"🚨 КРИТИЧЕСКИХ ОТЧЁТОВ ОТПРАВЛЕНО: {critical_count}")
    
    print("\nДЕТАЛИ:")
    for result in results:
        status_emoji = "✅" if result['status'] == 'PASS' else "❌" if result['status'] == 'FAIL' else "💥"
        print(f"{status_emoji} {result['test']} -> {result['result']}")
    
    if passed == len(results):
        print(f"\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! СИСТЕМА ГОТОВА К ПРОДАКШЕНУ!")
        print("🎯 Система корректно выявляет только критические ошибки менеджеров")
    else:
        print(f"\n⚠️ ЕСТЬ ПРОБЛЕМЫ В ТЕСТАХ - НУЖНА ДОРАБОТКА")

if __name__ == "__main__":
    asyncio.run(test_new_critical_system())