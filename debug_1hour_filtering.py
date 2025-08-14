#!/usr/bin/env python3

import os
from main import authenticate_telfin, get_recent_calls
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv

load_dotenv()

def debug_1hour_filtering():
    """Debug exactly what happens with 1-hour filtering using the same logic as main.py"""
    print("=== Debugging 1-Hour Filtering Logic ===")
    
    os.environ["TIME_WINDOW_HOURS"] = "1"
    
    hostname = os.getenv("TELFIN_HOSTNAME")
    login = os.getenv("TELFIN_LOGIN") 
    password = os.getenv("TELFIN_PASSWORD")
    
    if not all([hostname, login, password]):
        print("❌ Missing credentials in .env file")
        return
    
    print(f"Testing with TIME_WINDOW_HOURS=1 (production setting)")
    
    token = authenticate_telfin(hostname, login, password)
    if not token:
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    print("\nRetrieving calls with 1-hour window...")
    
    calls = get_recent_calls(hostname, token)
    
    if not calls:
        print("📋 No calls found in 1-hour window")
        print("This explains why system reports 'No new calls to process'")
        return
    
    print(f"📋 Retrieved {len(calls)} calls from last hour")
    
    incoming_calls = []
    for call in calls:
        flow = call.get('flow', '')
        duration = call.get('duration', 0)
        bridged_duration = call.get('bridged_duration', 0)
        
        print(f"Call {call.get('call_uuid', 'N/A')}: flow={flow}, duration={duration}s, bridged_duration={bridged_duration}s, result={call.get('result', 'N/A')}")
        
        if flow == 'in' and (duration > 0 or bridged_duration > 0):
            incoming_calls.append(call)
            print(f"  ✅ MATCHES: Incoming call with duration")
        else:
            print(f"  ❌ SKIPPED: Not incoming with duration")
    
    print(f"\n=== Filtering Results ===")
    print(f"Total calls in 1-hour window: {len(calls)}")
    print(f"Incoming calls with duration: {len(incoming_calls)}")
    
    if len(incoming_calls) > 0:
        print("✅ System SHOULD process these calls")
        for call in incoming_calls:
            print(f"  - {call.get('call_uuid')}: {call.get('duration')}s")
    else:
        print("✅ No incoming calls with recordings in 1-hour window")
        print("   This is the correct behavior - system should report 'No new calls to process'")
    
    moscow_tz = pytz.timezone('Europe/Moscow')
    moscow_now = datetime.now(moscow_tz)
    print(f"\nCurrent Moscow time: {moscow_now.strftime('%Y-%m-%d %H:%M:%S MSK')}")
    print(f"1-hour window: {(moscow_now - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S MSK')} to {moscow_now.strftime('%Y-%m-%d %H:%M:%S MSK')}")

if __name__ == "__main__":
    debug_1hour_filtering()
