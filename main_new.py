#!/usr/bin/env python3
"""
Новая версия main.py с обновленной логикой анализа звонков
"""
import os
import requests
import openai
import asyncio
import json
from telegram import Bot
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pytz
from prompt_loader import prompt_loader

# Импортируем все функции из старого main.py
from main import (
    load_processed_calls, save_processed_call, authenticate_telfin, 
    get_recent_calls, download_recording, transcribe_with_yandex, 
    transcribe_with_openai, send_telegram_report, has_recording, 
    get_call_cdr, MOSCOW_TZ
)

def analyze_with_gpt_new(transcript, call_info=None):
    """
    NEW: Analyze call transcript with JSON-based logic focused on critical manager errors.
    
    Args:
        transcript (str): Transcribed text from the call
        call_info (dict): Optional call metadata (duration, time, etc.)
    
    Returns:
        dict: JSON response with analysis or {"status": "ignore"}
    """
    openai_api_key = os.environ.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key or openai_api_key == "your_openai_api_key":
        print("Error: OPENAI_API_KEY not configured")
        return {"status": "ignore", "error": "no_api_key"}
        
    if not transcript:
        print("Error: No transcript provided for analysis")
        return {"status": "ignore", "error": "no_transcript"}
    
    try:
        # Используем новые внешние промпты
        print("📝 Loading prompts for critical error detection...")
        full_prompt = prompt_loader.get_full_analysis_prompt(transcript, call_info)
        
        print("🤖 Sending to GPT-4 for critical error analysis...")
        client = openai.OpenAI(api_key=openai_api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=800,   # Уменьшили - нужен только JSON
            temperature=0.1   # Минимальная температура для стабильности JSON
        )
        
        raw_response = response.choices[0].message.content.strip()
        print(f"✅ GPT-4 response received: {len(raw_response)} characters")
        
        # Парсим JSON ответ
        try:
            # Убираем возможные markdown обёртки
            if raw_response.startswith('```json'):
                raw_response = raw_response[7:-3].strip()
            elif raw_response.startswith('```'):
                raw_response = raw_response[3:-3].strip()
                
            analysis_json = json.loads(raw_response)
            print(f"✅ JSON parsed successfully: status = {analysis_json.get('status', 'unknown')}")
            return analysis_json
            
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parse error: {e}")
            print(f"⚠️ Raw response: {raw_response[:200]}...")
            # В случае ошибки парсинга - игнорируем
            return {"status": "ignore", "error": "json_parse_failed"}
        
    except Exception as e:
        print(f"❌ Error during GPT-4 analysis: {e}")
        return {"status": "ignore", "error": str(e)}

def main_new():
    """
    NEW: Main function with updated logic - only alerts on critical manager errors
    """
    print("=== NEW: Critical Error Detection System for 29ROZ ===")
    print("🎯 Focus: ONLY manager errors that cost sales")
    
    hostname = os.environ.get("TELFIN_HOSTNAME") or os.getenv("TELFIN_HOSTNAME")
    login = os.environ.get("TELFIN_LOGIN") or os.getenv("TELFIN_LOGIN")
    password = os.environ.get("TELFIN_PASSWORD") or os.getenv("TELFIN_PASSWORD")
    yandex_api_key = os.environ.get("YANDEX_API_KEY") or os.getenv("YANDEX_API_KEY")
    
    if not hostname or not login or not password:
        print("Error: TELFIN_HOSTNAME, TELFIN_LOGIN and TELFIN_PASSWORD must be set")
        return
    
    if not yandex_api_key:
        print("Error: YANDEX_API_KEY must be set")
        return
    
    print(f"\n1. Authenticating with Telphin API at {hostname}...")
    token = authenticate_telfin(hostname, login, password)
    
    if not token:
        print("Authentication failed. Cannot proceed.")
        return
    
    print("\n2. Loading processed calls history...")
    processed_calls = load_processed_calls()
    print(f"Found {len(processed_calls)} previously processed calls")
    
    print("\n3. Retrieving recent calls...")
    calls = get_recent_calls(hostname, token)
    
    if calls is None:
        print("Failed to retrieve calls.")
        return
    
    new_calls = [call for call in calls if call.get('call_uuid') not in processed_calls]
    
    print(f"Found {len(calls)} total calls, {len(new_calls)} new calls to process")
    
    if not new_calls:
        print("✅ No new calls to process.")
        return
    
    processed_count = 0
    critical_alerts = 0
    
    print("\n4. Filtering for incoming calls with recordings...")
    incoming_calls_with_recordings = []
    
    for call in new_calls:
        flow = call.get('flow', '')
        call_uuid = call.get('call_uuid')
        
        if flow != 'in':
            print(f"Skipping call {call_uuid}: flow={flow} (not incoming)")
            continue
            
        if not call_uuid:
            print(f"Skipping call: missing call_uuid")
            continue
            
        has_rec, rec_size = has_recording(hostname, token, call_uuid)
        
        if has_rec:
            incoming_calls_with_recordings.append(call)
            print(f"✅ Found incoming call with recording: {call_uuid} ({rec_size} bytes)")
        else:
            print(f"Skipping call {call_uuid}: no recording available")
    
    print(f"Filtered to {len(incoming_calls_with_recordings)} incoming calls with recordings")
    
    if not incoming_calls_with_recordings:
        print("✅ No incoming calls with recordings to process.")
        return
    
    for i, call in enumerate(incoming_calls_with_recordings):
        call_uuid = call.get('call_uuid')
        
        # 🔒 EARLY SAVE: Mark call as being processed
        print(f"🔒 Marking call {call_uuid} as processing...")
        save_processed_call(call_uuid, "processing")
            
        call_time_str = call.get('start_time_gmt', 'N/A')
        try:
            call_time_utc = datetime.strptime(call_time_str, "%Y-%m-%d %H:%M:%S")
            call_time_moscow = call_time_utc.replace(tzinfo=pytz.UTC).astimezone(MOSCOW_TZ)
            moscow_time_str = call_time_moscow.strftime("%Y-%m-%d %H:%M:%S MSK")
        except (ValueError, TypeError):
            moscow_time_str = call_time_str
        
        print(f"\nProcessing call {i+1}/{len(incoming_calls_with_recordings)}: {call_uuid}")
        print(f"  Details: {moscow_time_str} | {call.get('duration')}s | {call.get('flow')} | {call.get('result')}")
        
        audio_data = download_recording(hostname, token, call_uuid)
        
        if audio_data:
            processed_count += 1
            print(f"✅ Recording found! Processing...")
            
            # Transcribe with Yandex SpeechKit first, fallback to OpenAI
            transcribed_text = transcribe_with_yandex(yandex_api_key, audio_data)
            
            if transcribed_text == "Аудиозапись слишком длинная для транскрипции (более 30 секунд)":
                print("Yandex limit exceeded, trying OpenAI Whisper...")
                openai_api_key = os.environ.get("OPENAI_API_KEY")
                if openai_api_key:
                    transcribed_text = transcribe_with_openai(openai_api_key, audio_data)
                    if transcribed_text:
                        print("✅ OpenAI Whisper transcription completed")
                    else:
                        print("❌ OpenAI Whisper transcription failed")
                else:
                    print("❌ OPENAI_API_KEY not configured")
            
            if transcribed_text:
                print(f"✅ Transcription completed")
                
                # Передаём информацию о звонке для анализа
                call_info_for_analysis = {
                    'duration': call.get('duration', 0),
                    'time': call.get('start_time_gmt', ''),
                    'direction': call.get('flow', 'unknown')
                }
                
                analysis_result = analyze_with_gpt_new(transcribed_text, call_info_for_analysis)
                
                if analysis_result and isinstance(analysis_result, dict):
                    # Проверяем статус анализа
                    if analysis_result.get('status') == 'alert':
                        print(f"🚨 КРИТИЧЕСКАЯ ОШИБКА МЕНЕДЖЕРА ОБНАРУЖЕНА!")
                        print(f"⚙️ Код: {analysis_result.get('error_code', 'UNKNOWN')}")
                        print(f"📋 Описание: {analysis_result.get('error_description', 'N/A')}")
                        
                        # Извлекаем номер клиента
                        def clean_phone_number(number):
                            if number and number != 'N/A':
                                return number.split('@')[0]
                            return 'N/A'
                        
                        # Определяем номер клиента в зависимости от направления звонка
                        if call.get('flow') == 'in':  # Входящий - клиент звонит нам
                            client_phone = clean_phone_number(call.get('bridged_username') or call.get('from_username'))
                        else:  # Исходящий - мы звоним клиенту
                            client_phone = clean_phone_number(call.get('to_username') or call.get('bridged_username'))
                        
                        # Создаём критический отчёт
                        alert_template = prompt_loader.get_alert_template()
                        critical_report = alert_template.format(
                            error_code=analysis_result.get('error_code', 'UNKNOWN'),
                            error_description=analysis_result.get('error_description', 'N/A'),
                            client_phone=client_phone,
                            context=analysis_result.get('context', 'N/A'),
                            solution=analysis_result.get('solution', 'N/A')
                        )
                        
                        # Отправляем критический отчёт
                        telegram_success = asyncio.run(send_telegram_report(critical_report))
                        
                        if telegram_success:
                            critical_alerts += 1
                            save_processed_call(call_uuid, "critical_alert_sent")
                            print("🚨 Критический отчёт отправлен в Telegram!")
                        else:
                            print("❌ Ошибка отправки критического отчёта")
                            save_processed_call(call_uuid, "alert_failed")
                            
                    elif analysis_result.get('status') == 'ignore':
                        print(f"✅ Звонок проанализирован: не требует вмешательства")
                        save_processed_call(call_uuid, "analyzed_ignore")
                    else:
                        print(f"❌ Неожиданный результат анализа: {analysis_result}")
                        save_processed_call(call_uuid, "analysis_unexpected")
                else:
                    print(f"❌ Ошибка анализа звонка")
                    save_processed_call(call_uuid, "analysis_failed")
            else:
                print("❌ Transcription failed")
                save_processed_call(call_uuid, "transcription_error")
        else:
            print(f"❌ No recording available")
            save_processed_call(call_uuid, "no_recording")
    
    print(f"\n=== NEW ANALYSIS COMPLETE ===")
    print(f"Total calls retrieved: {len(calls)}")
    print(f"New calls found: {len(new_calls)}")
    print(f"Incoming calls with recordings: {len(incoming_calls_with_recordings)}")
    print(f"Calls processed: {processed_count}")
    print(f"🚨 CRITICAL ALERTS SENT: {critical_alerts}")
    print("🎯 System focused on critical manager errors only")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "scheduler":
        main_new()
    elif os.environ.get("PORT"):
        # Keep web handler from original main.py
        from main import web_handler
        web_handler()
    else:
        main_new()