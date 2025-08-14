#!/usr/bin/env python3

import os
from main import authenticate_telfin, get_recent_calls

def test_phone_extraction():
    """Test phone number extraction from API response"""
    print("=== Testing Phone Number Extraction ===")
    
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
    
    def clean_phone_number(number):
        if number and number != 'N/A':
            return number.split('@')[0]
        return number
    
    print("\n=== TESTING PHONE NUMBER EXTRACTION ===")
    for i, call in enumerate(calls[:3]):
        print(f"\nCall {i+1}:")
        print(f"  UUID: {call.get('call_uuid', 'N/A')}")
        print(f"  Flow: {call.get('flow', 'N/A')}")
        print(f"  Raw from_username: {call.get('from_username', 'N/A')}")
        print(f"  Raw to_username: {call.get('to_username', 'N/A')}")
        print(f"  Raw bridged_username: {call.get('bridged_username', 'N/A')}")
        
        from_number = call.get('from_username', 'N/A')
        to_number = call.get('to_username', 'N/A') 
        bridged_number = call.get('bridged_username', 'N/A')
        
        if call.get('flow') == 'out':
            caller_number = from_number
            called_number = to_number if to_number != 'N/A' else bridged_number
        else:
            caller_number = bridged_number if bridged_number != 'N/A' else from_number
            called_number = to_number
        
        caller_number = clean_phone_number(caller_number)
        called_number = clean_phone_number(called_number)
        
        print(f"  ✅ Extracted caller: {caller_number}")
        print(f"  ✅ Extracted called: {called_number}")
        print(f"  📞 Report format: с {caller_number} на {called_number}")

if __name__ == "__main__":
    test_phone_extraction()
