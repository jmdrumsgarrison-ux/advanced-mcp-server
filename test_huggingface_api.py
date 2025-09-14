import os
import json
from datetime import datetime
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print("=== PHASE 2.3: HUGGINGFACE HUB API LIVE TEST ===")
print(f"{datetime.now()} - Testing live HuggingFace Hub API connection")

try:
    # Test credential access
    token = os.getenv('HUGGINGFACE_TOKEN')
    if not token:
        print("[ERROR] HUGGINGFACE_TOKEN not found in environment")
        sys.exit(1)
    
    print(f"[OK] HuggingFace Token accessible (length: {len(token)} chars)")
    
    # Test import of huggingface_hub library
    try:
        from huggingface_hub import HfApi, login
        print("[OK] HuggingFace Hub library imported successfully")
    except ImportError as e:
        print(f"[ERROR] Failed to import huggingface_hub library: {e}")
        print("[INFO] Attempting to install huggingface_hub library...")
        import subprocess
        result = subprocess.run([sys.executable, "-m", "pip", "install", "huggingface_hub"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            from huggingface_hub import HfApi, login
            print("[OK] HuggingFace Hub library installed and imported")
        else:
            print(f"[ERROR] Failed to install huggingface_hub: {result.stderr}")
            sys.exit(1)
    
    # Test API connection with token validation
    print("[INFO] Testing live API connection...")
    
    # Login with token
    login(token=token)
    
    # Create API client and test basic functionality
    api = HfApi(token=token)
    
    # Test by getting user info (validates token)
    user_info = api.whoami()
    print(f"[INFO] Successfully authenticated as: {user_info['name']}")
    
    # Test by listing a popular model to verify access
    model_info = api.model_info("microsoft/DialoGPT-medium")
    print(f"[INFO] Successfully accessed model: {model_info.modelId}")
    
    print("[SUCCESS] HuggingFace Hub API live connection test PASSED")
    print(f"[INFO] User: {user_info['name']}")
    print(f"[INFO] Model access: Verified")
    
except Exception as e:
    print(f"[ERROR] HuggingFace Hub API test failed: {str(e)}")
    print(f"[ERROR] Exception type: {type(e).__name__}")
    sys.exit(1)

print("=== PHASE 2.3 COMPLETE ===")
