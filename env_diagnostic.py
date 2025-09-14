import os
from datetime import datetime

print("=== ENVIRONMENT VARIABLE DIAGNOSTIC ===")
print(f"{datetime.now()} - Checking environment variable access")

# Test direct environment access
print("\nDirect Environment Variable Check:")
env_vars = ['ANTHROPIC_API_KEY', 'OPENAI_API_KEY', 'HUGGINGFACE_TOKEN', 'GITHUB_TOKEN', 
           'TOGETHER_API_KEY', 'GOOGLE_CLOUD_API_KEY', 'GOOGLE_SEARCH_API_KEY']

for var in env_vars:
    value = os.getenv(var)
    if value:
        print(f"[OK] {var}: Found (length: {len(value)})")
    else:
        print(f"[ERROR] {var}: Not found")

# Test loading .env file
print("\nTesting .env file loading:")
try:
    from dotenv import load_dotenv
    print("[INFO] python-dotenv available, loading .env file...")
    
    # Load from current directory
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        print(f"[INFO] .env file found at: {env_path}")
        load_dotenv(env_path)
        print("[OK] .env file loaded")
        
        # Test again after loading
        print("\nAfter loading .env file:")
        for var in env_vars:
            value = os.getenv(var)
            if value:
                print(f"[OK] {var}: Found (length: {len(value)})")
            else:
                print(f"[ERROR] {var}: Still not found")
                
    else:
        print(f"[ERROR] .env file not found at: {env_path}")
        
except ImportError:
    print("[ERROR] python-dotenv not available, trying manual .env parsing...")
    
    # Manual .env file parsing
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        print(f"[INFO] .env file found, parsing manually...")
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    os.environ[key] = value
                    print(f"[INFO] Set {key} (length: {len(value)})")
        
        print("\nAfter manual .env parsing:")
        for var in env_vars:
            value = os.getenv(var)
            if value:
                print(f"[OK] {var}: Found (length: {len(value)})")
            else:
                print(f"[ERROR] {var}: Still not found")
    else:
        print(f"[ERROR] .env file not found at: {env_path}")

print("\n=== DIAGNOSTIC COMPLETE ===")
