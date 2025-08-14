#!/usr/bin/env python3

import os
from main import authenticate_telfin, get_recent_calls
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv

load_dotenv()

def analyze_call_timestamps():
    """Analyze the timestamps of calls to understand time distribution"""
    print("=== Analyzing Call Timestamps ===")
    
    # Check both 1-hour and 48-hour windows
    moscow_tz = pytz.timezone('Europe/Moscow')
    moscow_now = datetime.now(moscow_tz)
    
    print(f"Current Moscow time: {moscow_now.strftime('%Y-%m-%d %H:%M:%S MSK')}")
    print(f"1-hour ago: {(moscow_now - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S MSK')}")
    print(f"48-hours ago: {(moscow_now - timedelta(hours=48)).strftime('%Y-%m-%d %H:%M:%S MSK')}")
    
    hostname = os.getenv("TELFIN_HOSTNAME")
    login = os.getenv("TELFIN_LOGIN") 
    password = os.getenv("TELFIN_PASSWORD")
    
    if not all([hostname, login, password]):
        print("❌ Missing credentials in .env file")
        return
    
    token = authenticate_telfin(hostname, login, password)
    if not token:
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    
    # Get 48-hour window calls
    os.environ["TIME_WINDOW_HOURS"] = "48"
    calls_48h = get_recent_calls(hostname, token)
    
    if not calls_48h:
        print("❌ No calls found in 48-hour window")
        return
    
    print(f"\n📋 Retrieved {len(calls_48h)} calls from last 48 hours")
    
    # Filter for incoming calls with duration
    incoming_calls = []
    for call in calls_48h:
        flow = call.get('flow', '')
        duration = call.get('duration', 0)
        bridged_duration = call.get('bridged_duration', 0)
        
        if flow == 'in' and (duration > 0 or bridged_duration > 0):
            incoming_calls.append(call)
    
    print(f"📋 Found {len(incoming_calls)} incoming calls with duration")
    
    if not incoming_calls:
        print("❌ No incoming calls with duration found")
        return
    
    # Analyze timestamps
    one_hour_ago = moscow_now - timedelta(hours=1)
    recent_calls = []
    old_calls = []
    
    print(f"\n=== Timestamp Analysis ===")
    for i, call in enumerate(incoming_calls):
        call_uuid = call.get('call_uuid', 'N/A')
        call_time_str = call.get('start_time_gmt') or call.get('init_time_gmt')
        duration = call.get('duration', 0)
        result = call.get('result', 'N/A')
        
        if call_time_str:
            try:
                call_time = datetime.strptime(call_time_str, '%Y-%m-%d %H:%M:%S')
                call_time = call_time.replace(tzinfo=pytz.UTC)
                call_time_moscow = call_time.astimezone(moscow_tz)
                
                if call_time_moscow >= one_hour_ago:
                    recent_calls.append(call)
                    print(f"✅ RECENT: {call_time_moscow.strftime('%Y-%m-%d %H:%M:%S MSK')} | {duration}s | {result} | {call_uuid}")
                else:
                    old_calls.append(call)
                    if i < 5:  # Show first 5 old calls
                        print(f"⏰ OLD: {call_time_moscow.strftime('%Y-%m-%d %H:%M:%S MSK')} | {duration}s | {result} | {call_uuid}")
            except Exception as e:
                print(f"❌ Error parsing time for {call_uuid}: {e}")
    
    print(f"\n=== Summary ===")
    print(f"Total incoming calls with duration (48h): {len(incoming_calls)}")
    print(f"Recent calls (last 1 hour): {len(recent_calls)}")
    print(f"Older calls (1-48 hours ago): {len(old_calls)}")
    
    if len(recent_calls) == 0:
        print("\n✅ EXPLANATION: All incoming calls with recordings are older than 1 hour")
        print("   This is why the system correctly reports 'No new calls to process'")
        print("   The system is working as intended with 1-hour window")
    else:
        print(f"\n⚠️ ISSUE: Found {len(recent_calls)} recent incoming calls with recordings")
        print("   These should be processed but system reports 0 calls")
        print("   There may be a bug in the filtering or API call logic")
        
        # Show details of recent calls that should be processed
        for call in recent_calls:
            print(f"   - {call.get('call_uuid')}: {call.get('duration')}s, result={call.get('result')}")

if __name__ == "__main__":
    analyze_call_timestamps()
