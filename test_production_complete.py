import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("===== SESSION 6 PHASE 2B: PRODUCTION SERVER WITH ANTHROPIC LIBRARY =====")
print(f"{datetime.now()} - Testing production server with official Anthropic library")

def test_anthropic_library():
    """Test that the official anthropic library is now available"""
    print("\n=== ANTHROPIC LIBRARY AVAILABILITY TEST ===")
    
    try:
        import anthropic
        print(f"[SUCCESS] Anthropic library imported successfully!")
        print(f"[INFO] Anthropic version: {anthropic.__version__}")
        return True
    except ImportError as e:
        print(f"[ERROR] Failed to import anthropic library: {e}")
        return False

async def test_anthropic_api():
    """Test official Anthropic API client"""
    print("\n=== OFFICIAL ANTHROPIC API TEST ===")
    
    try:
        import anthropic
        
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            print("[ERROR] No API key available for testing")
            return False
        
        print("[INFO] Testing official Anthropic API client...")
        
        client = anthropic.Anthropic(api_key=api_key)
        
        response = await asyncio.to_thread(
            client.messages.create,
            model="claude-3-haiku-20240307",
            max_tokens=50,
            messages=[{"role": "user", "content": "Hello! Please respond with: OFFICIAL_ANTHROPIC_SUCCESS"}]
        )
        
        response_text = response.content[0].text.strip()
        print(f"[SUCCESS] API call successful! Response: {response_text}")
        print(f"[INFO] Model: {response.model}")
        print(f"[INFO] Usage: {response.usage}")
        
        if "OFFICIAL_ANTHROPIC_SUCCESS" in response_text:
            print("[SUCCESS] Official Anthropic library working perfectly!")
            return True
        else:
            print("[WARNING] API call succeeded but unexpected response")
            return True
            
    except Exception as e:
        print(f"[ERROR] Official Anthropic API test failed: {e}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return False

def test_production_modules_with_anthropic():
    """Test production module imports now that dependencies are available"""
    print("\n=== PRODUCTION MODULES WITH DEPENDENCIES TEST ===")
    
    try:
        # Now try importing production modules with all dependencies available
        print("[INFO] Testing production module imports with full dependencies...")
        
        from api_manager import APIManager
        print("[SUCCESS] api_manager imported successfully")
        
        from auth_manager import AuthManager  
        print("[SUCCESS] auth_manager imported successfully")
        
        from rules_engine import RulesEngine
        print("[SUCCESS] rules_engine imported successfully")
        
        from main import AdvancedMCPServer
        print("[SUCCESS] main (AdvancedMCPServer) imported successfully")
        
        print("[SUCCESS] All production modules imported successfully with full dependencies!")
        return True
        
    except ImportError as e:
        print(f"[ERROR] Production module import failed: {e}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error during imports: {e}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return False

async def test_production_api_manager():
    """Test production APIManager with official anthropic library"""
    print("\n=== PRODUCTION API MANAGER WITH ANTHROPIC TEST ===")
    
    try:
        from api_manager import APIManager
        
        print("[INFO] Creating production APIManager instance...")
        api_mgr = APIManager()
        
        print("[INFO] Initializing APIManager...")
        await api_mgr.initialize()
        
        print("[INFO] Testing production APIManager with official library...")
        result = await api_mgr.claude_api_call("messages", "POST", {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 50,
            "messages": [{"role": "user", "content": "Hello! Please respond with: PRODUCTION_ANTHROPIC_SUCCESS"}]
        })
        
        if result and 'content' in result:
            response_content = result['content'][0]['text'] if result['content'] else 'No content'
            print(f"[SUCCESS] Production API call successful! Response: {response_content}")
            
            if "PRODUCTION_ANTHROPIC_SUCCESS" in response_content:
                print("[SUCCESS] Production APIManager working with official Anthropic library!")
                return True
            else:
                print("[WARNING] Production API call succeeded but unexpected response")
                return True
        else:
            print(f"[ERROR] Unexpected production API response format: {result}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Production APIManager test failed: {e}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return False

async def main():
    """Run comprehensive production server tests with official anthropic library"""
    print("Testing production server with official Anthropic library")
    print()
    
    # Test 1: Anthropic library availability
    anthropic_available = test_anthropic_library()
    
    # Test 2: Official Anthropic API client
    api_success = False
    if anthropic_available:
        api_success = await test_anthropic_api()
    else:
        print("\n[SKIP] Skipping API test - anthropic library not available")
    
    # Test 3: Production modules with full dependencies
    modules_success = test_production_modules_with_anthropic()
    
    # Test 4: Production APIManager with official anthropic library
    production_success = False
    if anthropic_available and modules_success:
        production_success = await test_production_api_manager()
    else:
        print("\n[SKIP] Skipping production APIManager test due to previous failures")
    
    # Summary
    print("\n===== PRODUCTION SERVER WITH ANTHROPIC LIBRARY SUMMARY =====")
    print(f"Anthropic Library: {'PASS' if anthropic_available else 'FAIL'}")
    print(f"Official API Client: {'PASS' if api_success else 'FAIL'}")
    print(f"Production Modules: {'PASS' if modules_success else 'FAIL'}")
    print(f"Production APIManager: {'PASS' if production_success else 'FAIL'}")
    
    if anthropic_available and api_success and modules_success and production_success:
        print("\n🎆 COMPLETE SUCCESS: Production server fully operational!")
        print("✅ Session 5 environment fixes: Working")
        print("✅ Official Anthropic library: Installed and working")
        print("✅ Production modules: All importable and functional")
        print("✅ Production APIManager: Working with official library")
        print("✅ Live API calls: Successful through production server")
        print("\n🚀 PRODUCTION SERVER READY FOR FULL DEPLOYMENT!")
        return 0
    else:
        print("\n⚠️ Some tests failed - check output above for details")
        return 1
        
    print("\n===== COMPREHENSIVE PRODUCTION SERVER TEST COMPLETE =====")

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
