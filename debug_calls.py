#!/usr/bin/env python3

import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

def debug_calls_retrieval():
    """Debug call retrieval with different time windows"""
    load_dotenv()
    
    hostname = os.getenv("TELFIN_HOSTNAME")
    login = os.getenv("TELFIN_LOGIN") 
    password = os.getenv("TELFIN_PASSWORD")
    
    print("=== Debugging Call Retrieval ===")
    print(f"Hostname: {hostname}")
    
    # Authenticate
    auth_url = f"https://apiproxy.telphin.ru/oauth/token"
    auth_data = {
        "grant_type": "client_credentials",
        "client_id": login,
        "client_secret": password
    }
    
    try:
        auth_response = requests.post(auth_url, data=auth_data)
        auth_response.raise_for_status()
        token = auth_response.json().get("access_token")
        print("✅ Authentication successful")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return
    
    # Test different time windows
    time_windows = [
        ("1 hour", 1),
        ("6 hours", 6), 
        ("24 hours", 24),
        ("3 days", 72)
    ]
    
    for window_name, hours in time_windows:
        print(f"\n--- Testing {window_name} window ---")
        
        end_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start_datetime = (datetime.now() - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"From: {start_datetime}")
        print(f"To: {end_datetime}")
        
        calls_url = f"https://{hostname}/api/ver1.0/client/@me/calls/"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        params = {
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "per_page": 100
        }
        
        try:
            response = requests.get(calls_url, headers=headers, params=params)
            response.raise_for_status()
            calls_data = response.json()
            
            if isinstance(calls_data, dict) and 'calls' in calls_data:
                calls_list = calls_data['calls']
            elif isinstance(calls_data, list):
                calls_list = calls_data
            elif isinstance(calls_data, dict) and 'results' in calls_data:
                calls_list = calls_data['results']
            else:
                calls_list = []
            
            print(f"Total calls found: {len(calls_list)}")
            
            # Analyze call types
            answered_calls = 0
            unanswered_calls = 0
            calls_with_duration = 0
            
            for call in calls_list:
                duration = call.get('duration', 0)
                result = call.get('result', '')
                
                if result == 'answered' or duration > 0:
                    answered_calls += 1
                else:
                    unanswered_calls += 1
                    
                if duration > 0:
                    calls_with_duration += 1
            
            print(f"Answered calls: {answered_calls}")
            print(f"Unanswered calls: {unanswered_calls}")
            print(f"Calls with duration > 0: {calls_with_duration}")
            
            # Show sample calls
            if calls_list:
                print("Sample calls:")
                for i, call in enumerate(calls_list[:3]):
                    print(f"  {i+1}. {call.get('start_time_gmt')} | {call.get('duration')}s | {call.get('result')} | {call.get('flow')}")
                    
        except Exception as e:
            print(f"❌ Error retrieving calls: {e}")

if __name__ == "__main__":
    debug_calls_retrieval()
