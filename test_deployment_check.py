#!/usr/bin/env python3
"""
Тест режима проверки развертывания
"""
import os
import sys
from dotenv import load_dotenv

# Добавляем текущую директорию в PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Загружаем переменные окружения
load_dotenv()

def test_deployment_check():
    """Тестируем режим проверки развертывания"""
    print("=== 🧪 ТЕСТИРОВАНИЕ РЕЖИМА ПРОВЕРКИ РАЗВЕРТЫВАНИЯ ===")
    
    # Проверяем настройки
    required_env_vars = ["TELFIN_HOSTNAME", "TELFIN_LOGIN", "TELFIN_PASSWORD", "YANDEX_API_KEY", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Отсутствуют переменные окружения: {', '.join(missing_vars)}")
        return False
    
    print("✅ Все переменные окружения настроены")
    
    try:
        # Импортируем и запускаем режим проверки развертывания
        from main import main_new
        
        print("\n🚀 Запускаем режим проверки развертывания...")
        print("📞 Будут обработаны последние 2 звонка (игнорируя историю)")
        
        main_new(deployment_check=True)
        
        print("\n✅ ТЕСТ РЕЖИМА ПРОВЕРКИ РАЗВЕРТЫВАНИЯ ЗАВЕРШЕН")
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА В ТЕСТЕ ПРОВЕРКИ РАЗВЕРТЫВАНИЯ: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_deployment_check()
    if success:
        print("\n🎉 Режим проверки развертывания работает корректно!")
        print("🚀 Готов к использованию после развертывания на Heroku")
    else:
        print("\n⚠️ Есть проблемы с режимом проверки развертывания")