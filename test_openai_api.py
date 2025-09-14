import os
import json
from datetime import datetime
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print("=== PHASE 2.2: OPENAI API LIVE TEST ===")
print(f"{datetime.now()} - Testing live OpenAI API connection")

try:
    # Test credential access
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("[ERROR] OPENAI_API_KEY not found in environment")
        sys.exit(1)
    
    print(f"[OK] API Key accessible (length: {len(api_key)} chars)")
    
    # Test import of openai library
    try:
        import openai
        print("[OK] OpenAI library imported successfully")
    except ImportError as e:
        print(f"[ERROR] Failed to import openai library: {e}")
        sys.exit(1)
    
    # Test API connection with simple request
    print("[INFO] Testing live API connection...")
    
    client = openai.OpenAI(api_key=api_key)
    
    # Simple test message
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        max_tokens=50,
        messages=[{"role": "user", "content": "Hello! Please respond with exactly: 'API_TEST_SUCCESS'"}]
    )
    
    response_text = response.choices[0].message.content.strip()
    print(f"[INFO] API Response received: {response_text}")
    
    if "API_TEST_SUCCESS" in response_text:
        print("[SUCCESS] OpenAI API live connection test PASSED")
        print(f"[INFO] Model: {response.model}")
        print(f"[INFO] Usage: {response.usage}")
    else:
        print(f"[WARNING] Unexpected response: {response_text}")
        print("[PARTIAL] OpenAI API responding but unexpected content")
    
except Exception as e:
    print(f"[ERROR] OpenAI API test failed: {str(e)}")
    print(f"[ERROR] Exception type: {type(e).__name__}")
    sys.exit(1)

print("=== PHASE 2.2 COMPLETE ===")
