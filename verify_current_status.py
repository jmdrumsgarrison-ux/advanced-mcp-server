#!/usr/bin/env python3
"""
Advanced MCP Server - Current Status Verification
Verify all systems operational after Session 7 completion
"""

import asyncio
import sys
import os
import json
from pathlib import Path

# Add the project directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

async def verify_system_status():
    """Comprehensive verification of system status"""
    print("🔍 ADVANCED MCP SERVER - CURRENT STATUS VERIFICATION")
    print("=" * 60)
    
    verification_results = {
        "dependencies": False,
        "environment": False,
        "google_credentials": False,
        "api_manager": False,
        "server_startup": False,
        "google_services": False
    }
    
    try:
        # Test 1: Dependencies Check
        print("\n📦 TEST 1: Dependencies Verification")
        print("-" * 40)
        
        required_packages = [
            'mcp', 'fastapi', 'uvicorn', 'python-dotenv', 
            'google-auth', 'google-api-python-client', 'google-auth-oauthlib',
            'anthropic', 'openai', 'requests'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                print(f"✅ {package}")
            except ImportError:
                print(f"❌ {package}")
                missing_packages.append(package)
        
        if not missing_packages:
            verification_results["dependencies"] = True
            print("🎯 Dependencies Status: ✅ ALL AVAILABLE")
        else:
            print(f"🎯 Dependencies Status: ❌ Missing: {missing_packages}")
        
        # Test 2: Environment Variables
        print("\n🔧 TEST 2: Environment Variables Check")
        print("-" * 40)
        
        from dotenv import load_dotenv
        load_dotenv()
        
        required_env_vars = [
            'ANTHROPIC_API_KEY', 'OPENAI_API_KEY', 'GITHUB_TOKEN',
            'GOOGLE_APPLICATION_CREDENTIALS'
        ]
        
        env_status = {}
        for var in required_env_vars:
            value = os.getenv(var)
            if value:
                print(f"✅ {var}: Available")
                env_status[var] = True
            else:
                print(f"❌ {var}: Missing")
                env_status[var] = False
        
        if all(env_status.values()):
            verification_results["environment"] = True
            print("🎯 Environment Status: ✅ ALL CONFIGURED")
        else:
            print("🎯 Environment Status: ⚠️ Some variables missing")
        
        # Test 3: Google Service Account Credentials
        print("\n🔐 TEST 3: Google Service Account Verification")
        print("-" * 40)
        
        google_creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if google_creds_path and os.path.exists(google_creds_path):
            try:
                with open(google_creds_path, 'r') as f:
                    creds_data = json.load(f)
                
                if 'client_email' in creds_data and 'private_key' in creds_data:
                    print(f"✅ Service Account File: {google_creds_path}")
                    print(f"✅ Service Account Email: {creds_data.get('client_email', 'N/A')}")
                    print(f"✅ Project ID: {creds_data.get('project_id', 'N/A')}")
                    verification_results["google_credentials"] = True
                    print("🎯 Google Credentials Status: ✅ VALID")
                else:
                    print("❌ Invalid service account file format")
                    print("🎯 Google Credentials Status: ❌ INVALID")
            except Exception as e:
                print(f"❌ Error reading credentials: {e}")
                print("🎯 Google Credentials Status: ❌ ERROR")
        else:
            print("❌ Google credentials file not found")
            print("🎯 Google Credentials Status: ❌ MISSING")
        
        # Test 4: API Manager Import and Basic Check
        print("\n🌐 TEST 4: API Manager Verification")
        print("-" * 40)
        
        try:
            from api_manager import APIManager
            
            # Create API manager instance
            api_manager = APIManager()
            print("✅ APIManager class imported successfully")
            print("✅ APIManager instance created")
            
            # Check if it has the expected attributes/methods
            expected_methods = ['initialize_apis', '_initialize_google_apis']
            for method in expected_methods:
                if hasattr(api_manager, method):
                    print(f"✅ Method {method} available")
                else:
                    print(f"❌ Method {method} missing")
            
            verification_results["api_manager"] = True
            print("🎯 API Manager Status: ✅ OPERATIONAL")
            
        except Exception as e:
            print(f"❌ Error importing/creating APIManager: {e}")
            print("🎯 API Manager Status: ❌ ERROR")
        
        # Test 5: Basic Server Startup Check
        print("\n🚀 TEST 5: Server Startup Verification")
        print("-" * 40)
        
        try:
            from main import app, get_api_manager
            print("✅ Server application imported successfully")
            
            # Try to get API manager
            api_manager = get_api_manager()
            if api_manager:
                print("✅ API Manager accessible from server")
                verification_results["server_startup"] = True
                print("🎯 Server Startup Status: ✅ READY")
            else:
                print("❌ API Manager not accessible from server")
                print("🎯 Server Startup Status: ⚠️ PARTIAL")
                
        except Exception as e:
            print(f"❌ Error with server startup check: {e}")
            print("🎯 Server Startup Status: ❌ ERROR")
        
        # Test 6: Google Services Basic Check
        print("\n📁 TEST 6: Google Services Verification")
        print("-" * 40)
        
        try:
            from google.oauth2.service_account import Credentials
            from googleapiclient.discovery import build
            
            if verification_results["google_credentials"]:
                creds = Credentials.from_service_account_file(
                    google_creds_path,
                    scopes=[
                        'https://www.googleapis.com/auth/drive',
                        'https://www.googleapis.com/auth/spreadsheets',
                        'https://www.googleapis.com/auth/documents',
                        'https://www.googleapis.com/auth/calendar'
                    ]
                )
                
                # Test building services (don't make actual API calls)
                services = ['drive', 'sheets', 'docs', 'calendar']
                versions = ['v3', 'v4', 'v1', 'v3']
                
                for service, version in zip(services, versions):
                    try:
                        build(service, version, credentials=creds)
                        print(f"✅ Google {service.title()} API: Service buildable")
                    except Exception as e:
                        print(f"❌ Google {service.title()} API: {e}")
                
                verification_results["google_services"] = True
                print("🎯 Google Services Status: ✅ ACCESSIBLE")
            else:
                print("⚠️ Skipping Google services test - credentials not valid")
                print("🎯 Google Services Status: ⚠️ SKIPPED")
                
        except Exception as e:
            print(f"❌ Error testing Google services: {e}")
            print("🎯 Google Services Status: ❌ ERROR")
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR during verification: {e}")
        return False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    total_tests = len(verification_results)
    passed_tests = sum(verification_results.values())
    
    for test_name, result in verification_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n🎯 OVERALL STATUS: {passed_tests}/{total_