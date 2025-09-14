import os
import json
import sys
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("===== SESSION 6 PHASE 2A: PRODUCTION SERVER API INTEGRATION TEST =====")
print(f"{datetime.now()} - Testing production server with auto-dependency handling")

def install_missing_package(package_name):
    """Install a missing package using subprocess"""
    print(f"[INFO] Attempting to install {package_name}...")
    result = subprocess.run([sys.executable, "-m", "pip", "install", package_name], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print(f"[OK] {package_name} installed successfully")
        return True
    else:
        print(f"[ERROR] Failed to install {package_name}: {result.stderr}")
        return False

def test_environment_access():
    """Test environment variable access (Session 5 fix validation)"""
    print("\n=== PRODUCTION ENVIRONMENT ACCESS TEST ===")
    
    try:
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        github_token = os.getenv('GITHUB_TOKEN')
        
        print(f"[INFO] Environment variables accessible:")
        print(f"  - ANTHROPIC_API_KEY: {'FOUND' if anthropic_key else 'MISSING'}")
        print(f"  - OPENAI_API_KEY: {'FOUND' if openai_key else 'MISSING'}")
        print(f"  - GITHUB_TOKEN: {'FOUND' if github_token else 'MISSING'}")
        
        if anthropic_key:
            print("[SUCCESS] Session 5 environment fixes working correctly!")
            return True
        else:
            print("[ERROR] ANTHROPIC_API_KEY not found!")
            return False
            
    except Exception as e:
        print(f"[ERROR] Environment test failed: {e}")
        return False

def test_production_modules():
    """Test production module imports with auto-dependency installation"""
    print("\n=== PRODUCTION MODULE IMPORT TEST ===")
    
    # Required dependencies for production modules
    required_packages = [
        'aiohttp',
        'python-dotenv', 
        'anthropic',
        'openai'
    ]
    
    # Install missing dependencies
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"[OK] {package} already available")
        except ImportError:
            print(f"[INFO] {package} not found, installing...")
            if not install_missing_package(package):
                print(f"[ERROR] Failed to install required package: {package}")
                return False
    
    # Test production module imports
    print("[INFO] Testing production module imports...")
    
    try:
        from api_manager import APIManager
        print("[SUCCESS] api_manager imported successfully")
        
        from auth_manager import AuthManager  
        print("[SUCCESS] auth_manager imported successfully")
        
        from rules_engine import RulesEngine
        print("[SUCCESS] rules_engine imported successfully")
        
        from main import AdvancedMCPServer
        print("[SUCCESS] main (AdvancedMCPServer) imported successfully")
        
        print("[SUCCESS] All production modules imported successfully!")
        return True
        
    except ImportError as e:
        print(f"[ERROR] Production module import failed: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error during imports: {e}")
        return False

def test_production_api():
    """Test production APIManager with live API call"""
    print("\n=== PRODUCTION API MANAGER LIVE TEST ===")
    
    try:
        # Import asyncio for async operations
        import asyncio
        
        # Import production APIManager
        from api_manager import APIManager
        
        async def run_api_test():
            print("[INFO] Creating production APIManager instance...")
            api_mgr = APIManager()
            
            print("[INFO] Initializing APIManager...")
            await api_mgr.initialize()
            
            print("[INFO] Testing live Anthropic API call...")
            result = await api_mgr.claude_api_call("messages", "POST", {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 50,
                "messages": [{"role": "user", "content": "Hello! Please respond with: PRODUCTION_API_SUCCESS"}]
            })
            
            if result and 'content' in result:
                response_content = result['content'][0]['text'] if result['content'] else 'No content'
                print(f"[SUCCESS] API call successful! Response: {response_content}")
                
                if "PRODUCTION_API_SUCCESS" in response_content:
                    print("[SUCCESS] Production APIManager working correctly!")
                    return True
                else:
                    print("[WARNING] API call succeeded but unexpected response")
                    return True
            else:
                print(f"[ERROR] Unexpected API response format: {result}")
                return False
        
        # Run the async test
        return asyncio.run(run_api_test())
        
    except Exception as e:
        print(f"[ERROR] Production API test failed: {e}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return False

def main():
    """Run all production server tests"""
    print("Testing production server with Session 5 fixes and auto-dependency handling")
    print()
    
    # Test 1: Environment Access (validates Session 5 fixes)
    env_success = test_environment_access()
    
    # Test 2: Module Imports with auto-dependency installation
    import_success = test_production_modules()
    
    # Test 3: Live API Integration (only if previous tests pass)
    api_success = False
    if env_success and import_success:
        api_success = test_production_api()
    else:
        print("\n[SKIP] Skipping API test due to previous failures")
    
    # Summary
    print("\n===== PRODUCTION SERVER TEST SUMMARY =====")
    print(f"Environment Access: {'PASS' if env_success else 'FAIL'}")
    print(f"Module Imports: {'PASS' if import_success else 'FAIL'}")
    print(f"API Integration: {'PASS' if api_success else 'FAIL'}")
    
    if env_success and import_success and api_success:
        print("\nSUCCESS: Production server ready for full MCP testing!")
        print("Session 5 fixes working + Dependencies resolved + API calls successful")
        print("Next: Test complete production server startup and MCP integration")
        return 0
    else:
        print("\nSome tests failed - check output above for details")
        return 1
        
    print("\n===== PRODUCTION SERVER INTEGRATION TEST COMPLETE =====")

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
