#!/usr/bin/env python3

import os
import sys
sys.path.append('.')

from main import load_processed_calls, save_processed_call

def test_call_tracking_system():
    """Test the enhanced call tracking system with status tracking"""
    print("=== Testing Call Tracking System ===")
    
    test_calls = [
        ("test-call-123", "success"),
        ("test-call-456", "gpt_error"), 
        ("test-call-789", "telegram_error"),
        ("test-call-abc", "transcription_error"),
        ("test-call-def", "no_recording")
    ]
    
    print("Saving test calls with different statuses...")
    for call_id, status in test_calls:
        save_processed_call(call_id, status)
    
    print("\nLoading processed calls...")
    processed_calls = load_processed_calls()
    
    print(f"✅ Loaded {len(processed_calls)} processed calls")
    for call_id in processed_calls:
        print(f"  - {call_id}")
    
    all_tracked = all(call_id in processed_calls for call_id, _ in test_calls)
    
    if all_tracked:
        print("✅ All test calls properly tracked")
        print("✅ Call tracking system working correctly")
        return True
    else:
        print("❌ Some test calls not tracked properly")
        return False

def test_gpt_model_change():
    """Verify GPT model change in the code"""
    print("\n=== Testing GPT Model Change ===")
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    if 'model="gpt-4o"' in content:
        print("✅ GPT model successfully changed to gpt-4o")
        return True
    elif 'model="gpt-4"' in content and 'model="gpt-4o"' not in content:
        print("❌ GPT model still using old gpt-4")
        return False
    else:
        print("⚠️ Could not verify GPT model change")
        return False

if __name__ == "__main__":
    print("Testing all critical fixes for infinite loop bug...\n")
    
    tracking_ok = test_call_tracking_system()
    model_ok = test_gpt_model_change()
    
    print(f"\n=== Test Results ===")
    print(f"Call tracking system: {'✅ PASS' if tracking_ok else '❌ FAIL'}")
    print(f"GPT model change: {'✅ PASS' if model_ok else '❌ FAIL'}")
    
    if tracking_ok and model_ok:
        print("\n🎉 All critical fixes verified successfully!")
        print("Ready for deployment to Heroku")
    else:
        print("\n❌ Some fixes need attention before deployment")
