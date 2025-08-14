import os
import requests
import openai
import asyncio
import json
from telegram import Bot
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pytz
import fcntl  # For file locking

MOSCOW_TZ = pytz.timezone('Europe/Moscow')

# Load local .env file for development
load_dotenv(".env.local")

PROCESSED_CALLS_FILE = "processed_calls.txt"
LOCK_FILE = "processed_calls.lock"

def acquire_file_lock():
    """Acquire exclusive lock on processed calls file to prevent race conditions"""
    try:
        lock_fd = open(LOCK_FILE, 'w')
        fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        print("🔒 Acquired file lock successfully")
        return lock_fd
    except (IOError, OSError) as e:
        print(f"⚠️ Could not acquire file lock: {e}")
        print("⚠️ Another instance may be running - exiting to prevent duplicates")
        return None

def release_file_lock(lock_fd):
    """Release file lock"""
    if lock_fd:
        try:
            fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
            lock_fd.close()
            os.unlink(LOCK_FILE)
            print("🔓 Released file lock")
        except:
            pass

def load_processed_calls():
    """Load processed calls with better error handling"""
    try:
        if os.path.exists(PROCESSED_CALLS_FILE):
            with open(PROCESSED_CALLS_FILE, 'r') as f:
                calls = set()
                for line in f:
                    call_id = line.strip()
                    if call_id and not call_id.startswith('#'):  # Skip comments
                        calls.add(call_id)
                print(f"📋 Loaded {len(calls)} processed calls from file")
                return calls
        print("📋 No processed calls file found - starting fresh")
        return set()
    except Exception as e:
        print(f"❌ Error loading processed calls: {e}")
        return set()

def save_processed_call_atomic(call_id, status="processing"):
    """
    Atomic save of processed call with status.
    This prevents race conditions and ensures immediate persistence.
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Read existing calls
        existing_calls = load_processed_calls()
        
        if call_id not in existing_calls:
            # Append to file atomically
            with open(PROCESSED_CALLS_FILE, 'a') as f:
                f.write(f"{call_id}\n")
                f.flush()  # Force write to disk immediately
                os.fsync(f.fileno())  # Ensure it's written to storage
            
            print(f"✅ Saved call {call_id} as {status} at {timestamp}")
            
            # Cleanup old entries if file gets too large
            all_calls = load_processed_calls()
            if len(all_calls) > 1000:
                print("🧹 Cleaning up old processed calls...")
                recent_calls = list(all_calls)[-800:]  # Keep last 800
                with open(PROCESSED_CALLS_FILE, 'w') as f:
                    f.write(f"# Cleaned up at {timestamp}\n")
                    for call in recent_calls:
                        f.write(f"{call}\n")
                    f.flush()
                    os.fsync(f.fileno())
                print(f"🧹 Kept {len(recent_calls)} most recent calls")
        else:
            print(f"⚠️ Call {call_id} already processed - skipping duplicate")
            
    except Exception as e:
        print(f"❌ Error saving processed call: {e}")

def main_debug():
    """Debug version with improved duplicate prevention"""
    print("=== 🐛 DEBUG MODE: Duplicate Prevention Test ===")
    
    # Step 1: Acquire file lock
    lock_fd = acquire_file_lock()
    if not lock_fd:
        print("❌ Could not acquire lock - another instance running?")
        return
    
    try:
        # Step 2: Load environment
        hostname = os.environ.get("TELFIN_HOSTNAME")
        login = os.environ.get("TELFIN_LOGIN") 
        password = os.environ.get("TELFIN_PASSWORD")
        
        if not all([hostname, login, password]):
            print("❌ Missing Telphin credentials")
            return
            
        print(f"🔧 Telphin: {hostname}")
        print(f"🔧 Login: {login[:8]}...")
        
        # Step 3: Test duplicate prevention system
        print("\\n=== Testing Duplicate Prevention ===")
        
        # Load existing processed calls
        processed_calls = load_processed_calls()
        print(f"Found {len(processed_calls)} existing processed calls")
        
        # Test saving a call
        test_call_id = "TEST_CALL_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        print(f"\\n🧪 Testing save for: {test_call_id}")
        
        save_processed_call_atomic(test_call_id, "test")
        
        # Verify it was saved
        updated_calls = load_processed_calls()
        if test_call_id in updated_calls:
            print(f"✅ Test call saved successfully")
        else:
            print(f"❌ Test call NOT found after save")
            
        # Test duplicate prevention
        print(f"\\n🧪 Testing duplicate prevention for: {test_call_id}")
        save_processed_call_atomic(test_call_id, "duplicate_test")
        
        print("\\n=== Debug Complete ===")
        
    finally:
        release_file_lock(lock_fd)

if __name__ == "__main__":
    main_debug()