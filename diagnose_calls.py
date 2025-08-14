#!/usr/bin/env python3

import os
from main import authenticate_telfin, get_recent_calls
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv

load_dotenv()

def diagnose_call_types():
    """Analyze call types in 48-hour window to understand filtering needs"""
    print("=== Diagnosing Call Types ===")
    
    os.environ["TIME_WINDOW_HOURS"] = "48"
    
    hostname = os.getenv("TELFIN_HOSTNAME")
    login = os.getenv("TELFIN_LOGIN") 
    password = os.getenv("TELFIN_PASSWORD")
    
    if not all([hostname, login, password]):
        print("❌ Missing credentials in .env file")
        return
    
    print(f"Testing with TIME_WINDOW_HOURS=48 to analyze call types...")
    
    token = authenticate_telfin(hostname, login, password)
    if not token:
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    print("\nRetrieving calls with 48-hour window...")
    
    calls = get_recent_calls(hostname, token)
    
    if not calls:
        print("❌ No calls found in 48-hour window")
        return
    
    print(f"Retrieved {len(calls)} calls from last 48 hours")
    
    incoming_calls = []
    outgoing_calls = []
    answered_calls = []
    calls_with_duration = []
    
    for call in calls:
        flow = call.get('flow', 'unknown')
        result = call.get('result', 'unknown')
        duration = call.get('duration', 0)
        bridged_duration = call.get('bridged_duration', 0)
        
        if flow == 'in':
            incoming_calls.append(call)
        elif flow == 'out':
            outgoing_calls.append(call)
        
        if result == 'answered':
            answered_calls.append(call)
        
        if duration > 0 or bridged_duration > 0:
            calls_with_duration.append(call)
    
    print(f"\n=== Call Analysis ===")
    print(f"Total calls: {len(calls)}")
    print(f"Incoming calls (flow='in'): {len(incoming_calls)}")
    print(f"Outgoing calls (flow='out'): {len(outgoing_calls)}")
    print(f"Answered calls: {len(answered_calls)}")
    print(f"Calls with duration > 0: {len(calls_with_duration)}")
    
    incoming_answered = [c for c in incoming_calls if c.get('result') == 'answered']
    incoming_with_duration = [c for c in incoming_calls if c.get('duration', 0) > 0 or c.get('bridged_duration', 0) > 0]
    
    print(f"\nIncoming + answered: {len(incoming_answered)}")
    print(f"Incoming + duration > 0: {len(incoming_with_duration)}")
    
    target_calls = [c for c in incoming_calls if (c.get('result') == 'answered' and (c.get('duration', 0) > 0 or c.get('bridged_duration', 0) > 0))]
    print(f"Target calls (incoming + answered + duration): {len(target_calls)}")
    
    if target_calls:
        print(f"\n=== Sample Target Call ===")
        sample = target_calls[0]
        for key, value in sample.items():
            print(f"{key}: {value}")
    
    moscow_tz = pytz.timezone('Europe/Moscow')
    moscow_now = datetime.now(moscow_tz)
    one_hour_ago = moscow_now - timedelta(hours=1)
    
    print(f"\n=== Time Window Analysis ===")
    print(f"Current Moscow time: {moscow_now.strftime('%Y-%m-%d %H:%M:%S MSK')}")
    print(f"One hour ago: {one_hour_ago.strftime('%Y-%m-%d %H:%M:%S MSK')}")
    
    recent_target_calls = []
    for call in target_calls:
        call_time_str = call.get('start_time_gmt') or call.get('init_time_gmt')
        if call_time_str:
            try:
                call_time = datetime.strptime(call_time_str, '%Y-%m-%d %H:%M:%S')
                call_time = call_time.replace(tzinfo=pytz.UTC)
                call_time_moscow = call_time.astimezone(moscow_tz)
                
                if call_time_moscow >= one_hour_ago:
                    recent_target_calls.append(call)
                    print(f"Recent target call: {call_time_moscow.strftime('%Y-%m-%d %H:%M:%S MSK')}")
            except:
                pass
    
    print(f"\nTarget calls in last hour: {len(recent_target_calls)}")
    
    if len(recent_target_calls) == 0:
        print("✅ This explains why system finds 0 calls with 1-hour window")
        print("   No incoming answered calls with duration in last hour")
    else:
        print("⚠️ Found target calls in last hour - filtering logic may need update")

if __name__ == "__main__":
    diagnose_call_types()
