import os
import json
from datetime import datetime
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print("=== PHASE 2.5: TOGETHER AI API LIVE TEST ===")
print(f"{datetime.now()} - Testing live Together AI API connection")

try:
    # Test credential access
    api_key = os.getenv('TOGETHER_API_KEY')
    if not api_key:
        print("[ERROR] TOGETHER_API_KEY not found in environment")
        sys.exit(1)
    
    print(f"[OK] Together AI API Key accessible (length: {len(api_key)} chars)")
    
    # Test import of requests library for Together AI API
    try:
        import requests
        print("[OK] Requests library imported successfully")
    except ImportError as e:
        print(f"[ERROR] Failed to import requests library: {e}")
        sys.exit(1)
    
    # Test API connection with simple inference request
    print("[INFO] Testing live API connection...")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Simple test request using the correct Together AI endpoint
    print("[INFO] Testing chat completions endpoint...")
    
    # Try the correct Together AI chat completions endpoint
    chat_data = {
        "model": "togethercomputer/RedPajama-INCITE-Chat-3B-v1",
        "messages": [
            {"role": "user", "content": "Hello! Please respond with exactly: API_TEST_SUCCESS"}
        ],
        "max_tokens": 50,
        "temperature": 0.1
    }
    
    chat_response = requests.post(
        'https://api.together.xyz/v1/chat/completions',
        headers=headers,
        json=chat_data
    )
    
    print(f"[DEBUG] Chat response status: {chat_response.status_code}")
    print(f"[DEBUG] Chat response headers: {dict(chat_response.headers)}")
    print(f"[DEBUG] Chat response text (first 200 chars): {chat_response.text[:200]}")
    
    if chat_response.status_code == 200:
        try:
            chat_result = chat_response.json()
            if 'choices' in chat_result and len(chat_result['choices']) > 0:
                response_text = chat_result['choices'][0]['message']['content'].strip()
                print(f"[INFO] API Response received: {response_text}")
                
                if "API_TEST_SUCCESS" in response_text:
                    print("[SUCCESS] Together AI API live connection test PASSED")
                else:
                    print(f"[PARTIAL] Together AI API responding but unexpected content: {response_text}")
                
                print(f"[INFO] Model: {chat_data['model']}")
                print(f"[INFO] Chat completion successful")
            else:
                print(f"[WARNING] Unexpected response format: {chat_result}")
                print("[PARTIAL] Together AI API accessible but response format unexpected")
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse JSON response: {e}")
            print(f"[ERROR] Response was: {chat_response.text}")
            sys.exit(1)
    elif chat_response.status_code == 401:
        print("[ERROR] Together AI API authentication failed - invalid API key")
        sys.exit(1)
    else:
        print(f"[ERROR] Together AI API request failed with status: {chat_response.status_code}")
        print(f"[ERROR] Response: {chat_response.text}")
        sys.exit(1)
    
except Exception as e:
    print(f"[ERROR] Together AI API test failed: {str(e)}")
    print(f"[ERROR] Exception type: {type(e).__name__}")
    sys.exit(1)

print("=== PHASE 2.5 COMPLETE ===")
