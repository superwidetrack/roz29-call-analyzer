#!/usr/bin/env python3

import os
from main import load_processed_calls, save_processed_call

def test_tracking_system():
    """Test the new environment variable-based tracking system"""
    print("=== Testing New Tracking System ===")
    
    if "PROCESSED_CALLS" in os.environ:
        del os.environ["PROCESSED_CALLS"]
        print("Cleared existing PROCESSED_CALLS env var")
    
    processed = load_processed_calls()
    print(f"Initial processed calls: {len(processed)}")
    assert len(processed) == 0, "Should start with empty set"
    
    test_call_id1 = 'test-call-123'
    save_processed_call(test_call_id1)
    print(f"Saved test call: {test_call_id1}")
    
    processed = load_processed_calls()
    print(f"After save: {len(processed)} calls")
    assert len(processed) == 1, "Should have 1 call after saving"
    assert test_call_id1 in processed, "Should contain the saved call"
    
    test_call_id2 = 'test-call-456'
    save_processed_call(test_call_id2)
    print(f"Saved second test call: {test_call_id2}")
    
    processed = load_processed_calls()
    print(f"After second save: {len(processed)} calls")
    assert len(processed) == 2, "Should have 2 calls after saving both"
    assert test_call_id1 in processed, "Should contain first call"
    assert test_call_id2 in processed, "Should contain second call"
    
    save_processed_call(test_call_id1)
    processed = load_processed_calls()
    print(f"After duplicate save: {len(processed)} calls")
    assert len(processed) == 2, "Should still have 2 calls after duplicate save"
    
    print(f"Environment variable content: {os.environ.get('PROCESSED_CALLS', 'EMPTY')}")
    
    for i in range(3, 105):
        save_processed_call(f'test-call-{i}')
    
    processed = load_processed_calls()
    print(f"After adding 102 more calls: {len(processed)} calls")
    assert len(processed) <= 100, "Should limit to 100 calls max"
    
    if "PROCESSED_CALLS" in os.environ:
        del os.environ["PROCESSED_CALLS"]
        print("Cleaned up test environment variable")
    
    print("✅ All tracking system tests passed!")

if __name__ == "__main__":
    test_tracking_system()
