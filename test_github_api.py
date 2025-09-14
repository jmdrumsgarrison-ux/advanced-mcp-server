import os
import json
from datetime import datetime
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print("=== PHASE 2.4: GITHUB API LIVE TEST ===")
print(f"{datetime.now()} - Testing live GitHub API connection")

try:
    # Test credential access
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("[ERROR] GITHUB_TOKEN not found in environment")
        sys.exit(1)
    
    print(f"[OK] GitHub Token accessible (length: {len(token)} chars)")
    
    # Test import of requests library for GitHub API
    try:
        import requests
        print("[OK] Requests library imported successfully")
    except ImportError as e:
        print(f"[ERROR] Failed to import requests library: {e}")
        sys.exit(1)
    
    # Test API connection with user info request
    print("[INFO] Testing live API connection...")
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Advanced-MCP-Server-Test'
    }
    
    # Test authenticated user endpoint
    response = requests.get('https://api.github.com/user', headers=headers)
    
    if response.status_code == 200:
        user_data = response.json()
        print(f"[INFO] Successfully authenticated as: {user_data.get('login', 'Unknown')}")
        print(f"[INFO] User ID: {user_data.get('id', 'Unknown')}")
        
        # Test repository access
        repos_response = requests.get('https://api.github.com/user/repos?per_page=1', headers=headers)
        if repos_response.status_code == 200:
            repos_data = repos_response.json()
            print(f"[INFO] Repository access verified (found {len(repos_data)} repos in first page)")
            
            print("[SUCCESS] GitHub API live connection test PASSED")
            print(f"[INFO] User: {user_data.get('login', 'Unknown')}")
            print(f"[INFO] API Rate Limit: {response.headers.get('X-RateLimit-Remaining', 'Unknown')}/{response.headers.get('X-RateLimit-Limit', 'Unknown')}")
        else:
            print(f"[WARNING] Repository access failed: {repos_response.status_code}")
            print("[PARTIAL] GitHub API user auth working but repo access limited")
    
    elif response.status_code == 401:
        print("[ERROR] GitHub API authentication failed - invalid token")
        sys.exit(1)
    else:
        print(f"[ERROR] GitHub API request failed with status: {response.status_code}")
        print(f"[ERROR] Response: {response.text}")
        sys.exit(1)
    
except Exception as e:
    print(f"[ERROR] GitHub API test failed: {str(e)}")
    print(f"[ERROR] Exception type: {type(e).__name__}")
    sys.exit(1)

print("=== PHASE 2.4 COMPLETE ===")
