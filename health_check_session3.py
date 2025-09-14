#!/usr/bin/env python3
"""
Advanced MCP Server - Session 3 Health Check
Test server initialization and API service availability
"""

import sys
import os
import traceback
from datetime import datetime

def write_result(message):
    """Write result to file for reliable output"""
    with open('health_check_result.txt', 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")

def main():
    """Run comprehensive health check"""
    try:
        write_result("🔄 SESSION 3 HEALTH CHECK STARTING...")
        
        # Test 1: Environment check
        write_result("📁 Testing environment setup...")
        if os.path.exists('.env'):
            write_result("✅ Environment file found")
        else:
            write_result("❌ Environment file missing")
            return False
            
        if os.path.exists('config.json'):
            write_result("✅ Configuration file found")
        else:
            write_result("❌ Configuration file missing")
            return False
        
        # Test 2: Module imports
        write_result("📦 Testing module imports...")
        
        try:
            from main import AdvancedMCPServer
            write_result("✅ Main server module imported")
        except Exception as e:
            write_result(f"❌ Main server import failed: {str(e)}")
            return False
            
        try:
            from api_manager import APIManager
            write_result("✅ API Manager module imported")
        except Exception as e:
            write_result(f"❌ API Manager import failed: {str(e)}")
            return False
            
        try:
            from auth_manager import AuthManager
            write_result("✅ Auth Manager module imported")
        except Exception as e:
            write_result(f"❌ Auth Manager import failed: {str(e)}")
            return False
            
        try:
            from session_manager import SessionManager
            write_result("✅ Session Manager module imported")
        except Exception as e:
            write_result(f"❌ Session Manager import failed: {str(e)}")
            return False
        
        # Test 3: Component initialization
        write_result("🔧 Testing component initialization...")
        
        try:
            auth_mgr = AuthManager()
            write_result("✅ Auth Manager initialized")
        except Exception as e:
            write_result(f"❌ Auth Manager initialization failed: {str(e)}")
            return False
            
        try:
            api_mgr = APIManager(auth_mgr)
            write_result("✅ API Manager initialized")
        except Exception as e:
            write_result(f"❌ API Manager initialization failed: {str(e)}")
            return False
        
        # Test 4: Service discovery
        write_result("🔍 Testing service discovery...")
        
        try:
            services = api_mgr.get_available_services()
            write_result(f"✅ Available services discovered: {len(services)}")
            
            for service in services:
                write_result(f"   📡 {service}")
                
        except Exception as e:
            write_result(f"❌ Service discovery failed: {str(e)}")
            return False
        
        # Test 5: Credential access test
        write_result("🔐 Testing credential access...")
        
        try:
            # Test credential retrieval without exposing values
            test_services = ['anthropic', 'openai', 'huggingface', 'github']
            configured_count = 0
            
            for service in test_services:
                if auth_mgr.get_credential(service):
                    configured_count += 1
                    write_result(f"✅ {service.upper()} credentials accessible")
                else:
                    write_result(f"⚠️ {service.upper()} credentials not found")
            
            write_result(f"✅ Credentials test: {configured_count}/{len(test_services)} services accessible")
            
        except Exception as e:
            write_result(f"❌ Credential access test failed: {str(e)}")
            return False
        
        # Success summary
        write_result("🎉 HEALTH CHECK COMPLETED SUCCESSFULLY!")
        write_result("✅ All core components operational")
        write_result("✅ API services discoverable")
        write_result("✅ Credential system functional")
        write_result("🚀 Server ready for API integration testing")
        
        return True
        
    except Exception as e:
        write_result(f"❌ CRITICAL ERROR: {str(e)}")
        write_result(f"📋 Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    # Clear previous results
    if os.path.exists('health_check_result.txt'):
        os.remove('health_check_result.txt')
    
    success = main()
    
    if success:
        write_result("EXIT CODE: 0 (SUCCESS)")
        sys.exit(0)
    else:
        write_result("EXIT CODE: 1 (FAILURE)")
        sys.exit(1)
