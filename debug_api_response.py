#!/usr/bin/env python3

import os
import json
from main import authenticate_telfin, get_recent_calls

def debug_api_response():
    """Debug script to examine actual API response structure"""
    print("=== Debugging API Response Structure ===")
    
    hostname = os.getenv("TELFIN_HOSTNAME")
    login = os.getenv("TELFIN_LOGIN") 
    password = os.getenv("TELFIN_PASSWORD")
    
    if not all([hostname, login, password]):
        print("❌ Missing credentials in .env file")
        return
    
    print(f"Authenticating with {hostname}...")
    token = authenticate_telfin(hostname, login, password)
    
    if not token:
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    print("\nRetrieving recent calls...")
    
    calls = get_recent_calls(hostname, token)
    
    if not calls:
        print("❌ No calls retrieved")
        return
    
    print(f"✅ Retrieved {len(calls)} calls")
    
    print("\n=== ANALYZING FIRST CALL STRUCTURE ===")
    if calls:
        first_call = calls[0]
        print("Available fields in call data:")
        for key, value in first_call.items():
            print(f"  {key}: {value}")
        
        print(f"\n=== PHONE NUMBER FIELDS ===")
        caller_fields = ['caller_number', 'from', 'caller', 'source', 'from_number']
        called_fields = ['called_number', 'to', 'called', 'destination', 'to_number']
        
        print("Checking for caller number fields:")
        for field in caller_fields:
            if field in first_call:
                print(f"  ✅ {field}: {first_call[field]}")
            else:
                print(f"  ❌ {field}: NOT FOUND")
        
        print("\nChecking for called number fields:")
        for field in called_fields:
            if field in first_call:
                print(f"  ✅ {field}: {first_call[field]}")
            else:
                print(f"  ❌ {field}: NOT FOUND")
    
    print(f"\n=== CHECKING PROCESSED CALLS TRACKING ===")
    if os.path.exists('processed_calls.json'):
        with open('processed_calls.json', 'r') as f:
            data = json.load(f)
            processed_calls = data.get('processed_calls', [])
            print(f"Found {len(processed_calls)} processed calls in tracking file")
            if processed_calls:
                print("Recent processed calls:")
                for call_id in processed_calls[-5:]:
                    print(f"  - {call_id}")
    else:
        print("❌ No processed_calls.json file found")
    
    print(f"\n=== CALL DETAILS FOR DEBUGGING ===")
    for i, call in enumerate(calls[:3]):
        print(f"\nCall {i+1}:")
        print(f"  UUID: {call.get('call_uuid', 'N/A')}")
        print(f"  Start time: {call.get('start_time_gmt', 'N/A')}")
        print(f"  Duration: {call.get('duration', 'N/A')} seconds")
        print(f"  Flow: {call.get('flow', 'N/A')}")
        print(f"  Result: {call.get('result', 'N/A')}")
        print(f"  Raw caller info: {call.get('caller_number', call.get('from', 'N/A'))}")
        print(f"  Raw called info: {call.get('called_number', call.get('to', 'N/A'))}")

if __name__ == "__main__":
    debug_api_response()
