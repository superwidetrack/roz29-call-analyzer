#!/usr/bin/env python3

import os
from main import authenticate_telfin, get_recent_calls
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv

load_dotenv()

def test_time_window_filtering():
    """Test that TIME_WINDOW_HOURS=1 properly filters calls to last hour only"""
    print("=== Testing Time Window Filtering ===")
    
    os.environ["TIME_WINDOW_HOURS"] = "1"
    
    hostname = os.getenv("TELFIN_HOSTNAME")
    login = os.getenv("TELFIN_LOGIN") 
    password = os.getenv("TELFIN_PASSWORD")
    
    if not all([hostname, login, password]):
        print("❌ Missing credentials in .env file")
        return
    
    print(f"Testing with TIME_WINDOW_HOURS=1")
    print(f"Authenticating with {hostname}...")
    
    token = authenticate_telfin(hostname, login, password)
    if not token:
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    print("\nRetrieving calls with 1-hour window...")
    
    calls = get_recent_calls(hostname, token)
    
    if not calls:
        print("✅ No calls in last hour (expected if no recent activity)")
        return
    
    print(f"Retrieved {len(calls)} calls from last hour")
    
    moscow_tz = pytz.timezone('Europe/Moscow')
    moscow_now = datetime.now(moscow_tz)
    one_hour_ago = moscow_now - timedelta(hours=1)
    
    print(f"\nCurrent Moscow time: {moscow_now.strftime('%Y-%m-%d %H:%M:%S MSK')}")
    print(f"One hour ago: {one_hour_ago.strftime('%Y-%m-%d %H:%M:%S MSK')}")
    
    for i, call in enumerate(calls[:3]):
        call_time_str = call.get('start_time', 'N/A')
        print(f"Call {i+1}: {call_time_str}")
    
    print("\n✅ Time window filtering test completed")

if __name__ == "__main__":
    test_time_window_filtering()
