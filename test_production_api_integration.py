#!/usr/bin/env python3
"""
Session 6 Phase 2A: Production Server API Integration Test
Test production APIManager with live Anthropic API calls
"""

import sys
import os
import asyncio
import traceback
from pathlib import Path

# Ensure we can import from the production server directory
sys.path.insert(0, str(Path(__file__).parent))

def test_production_environment():
    """Test that production environment setup is working"""
    print("=== PRODUCTION ENVIRONMENT TEST ===")
    
    try:
        # Test environment variable access (should work after Session 5 fixes)
        from dotenv import load_dotenv
        load_dotenv()
        
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        github_token = os.getenv('GITHUB_TOKEN')
        
        print(f"[INFO] Environment variables accessible:")
        print(f"  - ANTHROPIC_API_KEY: {'FOUND' if anthropic_key else 'MISSING'}")
        print(f"  - OPENAI_API_KEY: {'FOUND' if openai_key else 'MISSING'}")
        print(f"  - GITHUB_TOKEN: {'FOUND' if github_token else 'MISSING'}")
        
        if not anthropic_key:
            print("[ERROR] ANTHROPIC_API_KEY not found!")
            return False
            
        print("[SUCCESS] Environment access working!")
        return True
        
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        print("[INFO] python-dotenv may need to be installed")
        return False
    except Exception as e:
        print(f"[ERROR] Environment test failed: {e}")
        return False

def test_production_imports():
    """Test that production modules can be imported"""
    print("\n=== PRODUCTION MODULE IMPORT TEST ===")
    
    try:
        # Test importing production modules (should work after Session 5 fixes)
        print("[INFO] Testing production module imports...")
        
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
        print(f"[ERROR] Import error: {e}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return False
    except Exception as e:
        print(f"[ERROR] Import test failed: {e}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return False

async def test_production_api_manager():
    """Test production APIManager with live API call"""
    print("\n=== PRODUCTION API MANAGER TEST ===")
    
    try:
        from api_manager import APIManager
        
        print("[INFO] Creating production APIManager instance...")
        api_mgr = APIManager()
        
        print("[INFO] Initializing APIManager...")
        await api_mgr.initialize()
        
        print("[INFO] Testing live Anthropic API call...")
        result = await api_mgr.claude_api_call("messages", "POST", {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 50,
            "messages": [{"role": "user", "content": "Hello! Please respond with: PRODUCTION_API_TEST_SUCCESS"}]
        })
        
        if result and 'content' in result:
            response_content = result['content'][0]['text'] if result['content'] else 'No content'
            print(f"[SUCCESS] API call successful! Response: {response_content}")
            
            if "PRODUCTION_API_TEST_SUCCESS" in response_content:
                print("[SUCCESS] Production APIManager working correctly!")
                return True
            else:
                print("[WARNING] API call succeeded but unexpected response")
                return True
        else:
            print(f"[ERROR] Unexpected API response format: {result}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Production API test failed: {e}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return False

async def main():
    """Run all production server tests"""
    print("===== SESSION 6 PHASE 2A: PRODUCTION SERVER API INTEGRATION TESTING =====")
    print("Testing production server with Session 5 fixes applied")
    print()
    
    # Test 1: Environment Access
    env_success = test_production_environment()
    
    # Test 2: Module Imports  
    import_success = test_production_imports()
    
    # Test 3: Live API Integration (only if previous tests pass)
    api_success = False
    if env_success and import_success:
        api_success = await test_production_api_manager()
    else:
        print("\n[SKIP] Skipping API test due to previous failures")
    
    # Summary
    print("\n===== PRODUCTION SERVER TEST SUMMARY =====")
    print(f"Environment Access: {'✅ PASS' if env_success else '❌ FAIL'}")
    print(f"Module Imports: {'✅ PASS' if import_success else '❌ FAIL'}")
    print(f"API Integration: {'✅ PASS' if api_success else '❌ FAIL'}")
    
    if env_success and import_success and api_success:
        print("\n🎆 SUCCESS: Production server ready for full testing!")
        print("Next: Test complete production server startup and MCP integration")
    else:
        print("\n⚠️  Some tests failed - investigation needed")
        
    print("\n===== TEST COMPLETE =====")

if __name__ == "__main__":
    asyncio.run(main())
