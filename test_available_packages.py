import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("===== SESSION 6 PHASE 2B: PRODUCTION SERVER WITH AVAILABLE PACKAGES =====")
print(f"{datetime.now()} - Testing production server with pre-installed packages")

def test_available_packages():
    """Test what packages are available in the Windows-MCP environment"""
    print("\n=== AVAILABLE PACKAGES TEST ===")
    
    available_packages = []
    
    # Test core packages that should be available
    test_packages = [
        ('dotenv', 'python-dotenv'),
        ('httpx', 'httpx HTTP client'),
        ('mcp', 'MCP protocol'),
        ('starlette', 'Starlette web framework'),
        ('uvicorn', 'Uvicorn ASGI server'),
        ('pydantic', 'Pydantic data validation'),
        ('requests', 'Requests HTTP library'),
        ('json', 'JSON (built-in)'),
        ('asyncio', 'Asyncio (built-in)')
    ]
    
    for package_name, description in test_packages:
        try:
            __import__(package_name)
            print(f"[OK] {description}: AVAILABLE")
            available_packages.append(package_name)
        except ImportError:
            print(f"[MISSING] {description}: NOT AVAILABLE")
    
    return available_packages

def test_environment_with_available_packages():
    """Test environment access using available packages"""
    print("\n=== ENVIRONMENT ACCESS WITH AVAILABLE PACKAGES ===")
    
    try:
        # Test environment variable access (should work with python-dotenv)
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        github_token = os.getenv('GITHUB_TOKEN')
        
        print(f"[INFO] Environment variables accessible:")
        print(f"  - ANTHROPIC_API_KEY: {'FOUND' if anthropic_key else 'MISSING'}")
        print(f"  - OPENAI_API_KEY: {'FOUND' if openai_key else 'MISSING'}")
        print(f"  - GITHUB_TOKEN: {'FOUND' if github_token else 'MISSING'}")
        
        if anthropic_key:
            print("[SUCCESS] Environment access working with available packages!")
            return True
        else:
            print("[ERROR] ANTHROPIC_API_KEY not found!")
            return False
            
    except Exception as e:
        print(f"[ERROR] Environment test failed: {e}")
        return False

def test_httpx_api_call():
    """Test making API calls using httpx instead of anthropic library"""
    print("\n=== HTTPX API CALL TEST ===")
    
    try:
        import httpx
        import json
        
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            print("[ERROR] No API key available for testing")
            return False
        
        print("[INFO] Testing Anthropic API call using httpx...")
        
        # Anthropic API call using httpx
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01'
        }
        
        data = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 50,
            "messages": [{"role": "user", "content": "Hello! Please respond with: HTTPX_API_SUCCESS"}]
        }
        
        with httpx.Client() as client:
            response = client.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result['content'][0]['text'] if result.get('content') else 'No content'
                print(f"[SUCCESS] API call successful! Response: {response_text}")
                
                if "HTTPX_API_SUCCESS" in response_text:
                    print("[SUCCESS] Production server can make API calls with available packages!")
                    return True
                else:
                    print("[WARNING] API call succeeded but unexpected response")
                    return True
            else:
                print(f"[ERROR] API call failed with status {response.status_code}: {response.text}")
                return False
                
    except Exception as e:
        print(f"[ERROR] HTTPX API test failed: {e}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return False

def main():
    """Run production server tests with available packages"""
    print("Testing production server with Windows-MCP pre-installed packages")
    print()
    
    # Test 1: Check available packages
    available_packages = test_available_packages()
    
    # Test 2: Environment access
    env_success = test_environment_with_available_packages()
    
    # Test 3: API call with httpx (if available)
    api_success = False
    if 'httpx' in available_packages and env_success:
        api_success = test_httpx_api_call()
    else:
        print("\n[SKIP] Skipping API test - missing httpx or environment access failed")
    
    # Summary
    print("\n===== PRODUCTION SERVER WITH AVAILABLE PACKAGES SUMMARY =====")
    print(f"Available Packages: {len(available_packages)} packages found")
    print(f"Environment Access: {'PASS' if env_success else 'FAIL'}")
    print(f"API Integration (httpx): {'PASS' if api_success else 'FAIL'}")
    
    if env_success and available_packages and ('httpx' in available_packages):
        print("\nSUCCESS: Production server CAN work with available packages!")
        print("- Environment variables: Working")
        print("- HTTP client (httpx): Available")
        print("- Core packages: Available")
        
        if api_success:
            print("- Live API calls: Working")
            print("\nRECOMMENDATION: Update production server to use httpx instead of aiohttp/anthropic")
        else:
            print("- Live API calls: Needs debugging")
            
        return 0
    else:
        print("\nIssues found - see details above")
        return 1
        
    print("\n===== AVAILABLE PACKAGES TEST COMPLETE =====")

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
