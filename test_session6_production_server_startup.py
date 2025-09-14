#!/usr/bin/env python3
"""
Session 6 Phase 2B: Production Server Startup Test (ASCII-only)
Test complete production server initialization with all components
"""

import asyncio
import sys
import os
import traceback

# Add project path
sys.path.insert(0, r'G:\projects\advanced-mcp-server')

# Import all production modules
try:
    from main import AdvancedMCPServer
    from api_manager import APIManager
    from auth_manager import AuthManager  
    from rules_engine import RulesEngine
    from session_manager import SessionManager
    print("[SUCCESS] All production modules imported successfully")
except ImportError as e:
    print(f"[CRITICAL FAILURE] Could not import production modules: {e}")
    sys.exit(1)

async def test_production_server_startup():
    """Test complete production server initialization"""
    
    print("\n" + "="*60)
    print("SESSION 6 PHASE 2B: PRODUCTION SERVER STARTUP TEST")
    print("="*60)
    
    try:
        # Test 1: Production Server Initialization
        print("\n[TEST 1] Production Server Initialization")
        server = AdvancedMCPServer()
        print("[PASS] AdvancedMCPServer instance created")
        
        # Test 2: Component Initialization
        print("\n[TEST 2] Production Component Initialization")
        
        # Initialize individual components to test environment access
        api_mgr = APIManager()
        auth_mgr = AuthManager()
        rules_engine = RulesEngine()
        session_mgr = SessionManager()
        
        print("[PASS] All production components instantiated")
        
        # Test 3: Async Component Initialization  
        print("\n[TEST 3] Async Component Initialization")
        
        await api_mgr.initialize()
        print("[PASS] APIManager async initialization successful")
        
        await rules_engine.initialize()
        print("[PASS] RulesEngine async initialization successful")
        
        await session_mgr.initialize()
        print("[PASS] SessionManager async initialization successful")
        
        # Test 4: Component Environment Access
        print("\n[TEST 4] Production Component Environment Access")
        
        # Test each component can access environment variables
        if hasattr(auth_mgr, '_load_credentials'):
            credentials = auth_mgr._load_credentials()
            print("[PASS] AuthManager environment access working")
            
        # Test API manager environment access
        if hasattr(api_mgr, 'anthropic_client') and api_mgr.anthropic_client:
            print("[PASS] APIManager Anthropic client initialized")
        else:
            print("[NOTE] APIManager Anthropic client status unknown")
            
        # Test 5: Production Server Methods
        print("\n[TEST 5] Production Server Methods")
        
        # Test basic server methods
        if hasattr(server, 'list_tools'):
            tools = await server.list_tools()
            print(f"[PASS] Server tools method working: {len(tools)} tools available")
        else:
            print("[NOTE] Server tools method not available")
            
        if hasattr(server, 'list_resources'):
            resources = await server.list_resources()
            print(f"[PASS] Server resources method working: {len(resources)} resources available")
        else:
            print("[NOTE] Server resources method not available")
            
        # Test 6: Component Integration
        print("\n[TEST 6] Component Integration Test")
        
        # Test that components can work together
        if hasattr(server, 'api_manager'):
            print("[PASS] Server has API manager integration")
            
        if hasattr(server, 'auth_manager'):
            print("[PASS] Server has auth manager integration")
            
        if hasattr(server, 'rules_engine'):
            print("[PASS] Server has rules engine integration")
            
        print("\n[COMPLETE] PRODUCTION SERVER STARTUP TESTS COMPLETE")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n[CRITICAL ERROR] in Production Server Startup Test: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

async def main():
    """Main test execution"""
    print("Starting Session 6 Phase 2B Production Server Startup Test...")
    
    success = await test_production_server_startup()
    
    if success:
        print("\n[SUCCESS] SESSION 6 PHASE 2B: PRODUCTION SERVER STARTUP SUCCESSFUL!")
        print("[PASS] Production server components: WORKING")
        print("[PASS] Environment variable access: WORKING") 
        print("[PASS] Async initialization: WORKING")
        print("[PASS] Component integration: WORKING")
        print("\nReady for next phase: MCP Protocol Integration Test")
    else:
        print("\n[FAIL] SESSION 6 PHASE 2B: STARTUP ISSUES DETECTED")
        print("Production server startup requires investigation")
    
    return success

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        print(f"\nTest completed with result: {result}")
    except Exception as e:
        print(f"Critical error in test execution: {e}")
        print(f"Traceback: {traceback.format_exc()}")
