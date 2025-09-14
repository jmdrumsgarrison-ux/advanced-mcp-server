import os
import json
from datetime import datetime
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("=== PHASE 2.1: ANTHROPIC CLAUDE API LIVE TEST ===")
print(f"{datetime.now()} - Testing live Anthropic API connection")

try:
    # Test credential access
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("[ERROR] ANTHROPIC_API_KEY not found in environment")
        sys.exit(1)
    
    print(f"[OK] API Key accessible (length: {len(api_key)} chars)")
    
    # Test import of anthropic library
    try:
        import anthropic
        print("[OK] Anthropic library imported successfully")
    except ImportError as e:
        print(f"[ERROR] Failed to import anthropic library: {e}")
        print("[INFO] Attempting to install anthropic library...")
        import subprocess
        result = subprocess.run([sys.executable, "-m", "pip", "install", "anthropic"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            import anthropic
            print("[OK] Anthropic library installed and imported")
        else:
            print(f"[ERROR] Failed to install anthropic: {result.stderr}")
            sys.exit(1)
    
    # Test API connection with simple request
    print("[INFO] Testing live API connection...")
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Simple test message
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=50,
        messages=[{"role": "user", "content": "Hello! Please respond with exactly: 'API_TEST_SUCCESS'"}]
    )
    
    response_text = response.content[0].text.strip()
    print(f"[INFO] API Response received: {response_text}")
    
    if "API_TEST_SUCCESS" in response_text:
        print("[SUCCESS] Anthropic API live connection test PASSED")
        print(f"[INFO] Model: {response.model}")
        print(f"[INFO] Usage: {response.usage}")
    else:
        print(f"[WARNING] Unexpected response: {response_text}")
        print("[PARTIAL] Anthropic API responding but unexpected content")
    
except Exception as e:
    print(f"[ERROR] Anthropic API test failed: {str(e)}")
    print(f"[ERROR] Exception type: {type(e).__name__}")
    sys.exit(1)

print("=== PHASE 2.1 COMPLETE ===")
