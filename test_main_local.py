#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from main import authenticate_telfin, get_recent_calls

def test_main_with_6hour_window():
    """Test the main application with 6-hour window"""
    load_dotenv()
    
    print("=== Testing Main Application with 6-hour Window ===")
    
    # Set the time window to 6 hours
    os.environ["TIME_WINDOW_HOURS"] = "6"
    
    # Authenticate
    login = os.getenv("TELFIN_LOGIN")
    password = os.getenv("TELFIN_PASSWORD")
    hostname = os.getenv("TELFIN_HOSTNAME")
    
    print(f"Authenticating with hostname: {hostname}")
    token = authenticate_telfin(hostname, login, password)
    
    if not token:
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    
    # Get recent calls with 6-hour window
    calls = get_recent_calls(hostname, token)
    
    if calls:
        print(f"✅ Retrieved {len(calls)} calls with 6-hour window")
        
        # Count answered calls
        answered_calls = [call for call in calls if call.get('result') == 'answered' or call.get('duration', 0) > 0]
        print(f"Found {len(answered_calls)} answered calls with potential recordings")
        
        # Show sample answered calls
        for i, call in enumerate(answered_calls[:3]):
            print(f"  {i+1}. {call.get('start_time_gmt')} | {call.get('duration')}s | {call.get('result')} | {call.get('flow')}")
    else:
        print("❌ Failed to retrieve calls")

if __name__ == "__main__":
    test_main_with_6hour_window()
