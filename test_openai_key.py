#!/usr/bin/env python3

import os
from dotenv import load_dotenv
import openai

load_dotenv()

def test_openai_api_key():
    """Test if the current OpenAI API key is valid"""
    print("=== Testing OpenAI API Key ===")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No OpenAI API key found in environment")
        return False
    
    print(f"Testing API key: {api_key[:20]}...{api_key[-10:]}")
    
    try:
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Say 'API key test successful'"}],
            max_tokens=10
        )
        
        print("✅ OpenAI API key is valid!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except openai.AuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

if __name__ == "__main__":
    test_openai_api_key()
