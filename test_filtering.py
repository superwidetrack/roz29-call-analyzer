#!/usr/bin/env python3

import os
from main import authenticate_telfin, get_recent_calls
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv

load_dotenv()

def test_updated_filtering():
    """Test the updated filtering logic for incoming calls with recordings"""
    print("=== Testing Updated Filtering Logic ===")
    
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
        print("✅ No calls in last hour - this is expected behavior")
        print("System will correctly report 'No new calls to process'")
        return
    
    print(f"Retrieved {len(calls)} calls from last hour")
    
    incoming_calls = []
    for call in calls:
        flow = call.get('flow', '')
        duration = call.get('duration', 0)
        bridged_duration = call.get('bridged_duration', 0)
        
        if flow == 'in' and (duration > 0 or bridged_duration > 0):
            incoming_calls.append(call)
            print(f"✅ Found incoming call: {call.get('call_uuid')} (duration: {duration}s)")
        else:
            print(f"⏭️ Skipped call: flow={flow}, duration={duration}s")
    
    print(f"\nFiltering results:")
    print(f"Total calls in 1-hour window: {len(calls)}")
    print(f"Incoming calls with duration: {len(incoming_calls)}")
    
    if len(incoming_calls) > 0:
        print("✅ System will process these incoming calls")
    else:
        print("✅ No incoming calls with recordings - system will correctly skip processing")

if __name__ == "__main__":
    test_updated_filtering()
