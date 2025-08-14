"""
Модуль для загрузки и управления промптами системы анализа звонков.
"""
import os
from pathlib import Path

class PromptLoader:
    """Класс для загрузки промптов из файлов"""
    
    def __init__(self, prompts_dir="prompts"):
        self.prompts_dir = Path(prompts_dir)
        self.prompts = {}
        self._load_all_prompts()
    
    def _load_all_prompts(self):
        """Загружает все промпты при инициализации"""
        prompt_files = {
            'system_context': 'system_context.txt',
            'classification': 'step1_classification.txt', 
            'manager_codes': 'manager_fault_codes.txt',
            'detailed_analysis': 'step2_detailed_analysis.txt',
            'final_instructions': 'final_instructions.txt'
        }
        
        for key, filename in prompt_files.items():
            self.prompts[key] = self._load_prompt(filename)
    
    def _load_prompt(self, filename):
        """Загружает отдельный промпт из файла"""
        try:
            filepath = self.prompts_dir / filename
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                print(f"✅ Loaded prompt: {filename}")
                return content
            else:
                print(f"⚠️ Prompt file not found: {filename}")
                return ""
        except Exception as e:
            print(f"❌ Error loading prompt {filename}: {e}")
            return ""
    
    def get_full_analysis_prompt(self, transcript, call_info):
        """
        Собирает полный промпт для анализа звонка
        
        Args:
            transcript (str): Транскрипция звонка
            call_info (dict): Информация о звонке (время, длительность и т.д.)
            
        Returns:
            str: Готовый промпт для GPT
        """
        # Форматируем информацию о звонке
        call_details = self._format_call_info(call_info)
        
        # Собираем промпт для новой логики
        full_prompt = f"""{self.prompts['system_context']}

{call_details}

**Транскрипция разговора:**
---
{transcript}
---

{self.prompts['classification']}

{self.prompts['manager_codes']}

{self.prompts['detailed_analysis']}

{self.prompts['final_instructions']}
"""
        return full_prompt
    
    def _format_call_info(self, call_info):
        """Форматирует информацию о звонке для промпта"""
        if not call_info:
            return ""
            
        details = []
        if call_info.get('duration'):
            details.append(f"Длительность: {call_info['duration']} сек")
        if call_info.get('time'):
            details.append(f"Время: {call_info['time']}")
        if call_info.get('direction'):
            details.append(f"Направление: {call_info['direction']}")
            
        if details:
            return f"**Информация о звонке:**\n" + " | ".join(details) + "\n"
        return ""
    
    def get_alert_template(self):
        """Возвращает шаблон для аварийного отчета"""
        return """🟥 **ПРОДАЖА УПУЩЕНА (ВИНА МЕНЕДЖЕРА)**

⚙️ **Ошибка:** {error_code} - {error_description}
📞 **Клиент:** {client_phone}
📋 **Контекст:** {context}

➡️ **Как можно было спасти:** {solution}

---
*Система контроля качества 29ROZ*"""
    
    def reload_prompts(self):
        """Перезагружает все промпты из файлов"""
        print("🔄 Reloading prompts...")
        self.prompts.clear()
        self._load_all_prompts()
        print("✅ Prompts reloaded")

# Глобальный экземпляр для использования в main.py
prompt_loader = PromptLoader()