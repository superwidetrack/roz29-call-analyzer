#!/usr/bin/env python3

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_telegram_bot():
    """Test Telegram bot connectivity and configuration"""
    print("=== Testing Telegram Bot ===")
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token:
        print("❌ No Telegram bot token found in environment")
        return False
    
    if not chat_id:
        print("❌ No Telegram chat ID found in environment")
        return False
    
    print(f"Bot token: {bot_token[:20]}...{bot_token[-10:]}")
    print(f"Chat ID: {chat_id}")
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url)
        
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get("ok"):
                print(f"✅ Bot is valid: {bot_info['result']['first_name']} (@{bot_info['result']['username']})")
            else:
                print(f"❌ Bot API error: {bot_info}")
                return False
        else:
            print(f"❌ Bot API request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Bot info test failed: {e}")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": "🔧 Test message from call analyzer system",
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                print("✅ Test message sent successfully!")
                return True
            else:
                print(f"❌ Message send error: {result}")
                return False
        else:
            print(f"❌ Message send failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Message send test failed: {e}")
        return False

if __name__ == "__main__":
    test_telegram_bot()
