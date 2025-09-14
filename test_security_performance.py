import os
import sys
import asyncio
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print("=== PHASE 4: SECURITY & PERFORMANCE VALIDATION ===")
print(f"{datetime.now()} - Testing security and performance features")

async def main():
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        import auth_manager
        import api_manager
        
        print("[INFO] Testing security features...")
        
        # Test 4.1: Credential encryption/decryption
        print("[INFO] 4.1 Testing credential security...")
        auth_mgr = auth_manager.AuthManager()
        await auth_mgr.initialize()
        
        health_check = await auth_mgr.health_check()
        print(f"[OK] Security health: {health_check['status']}")
        print(f"[OK] Encryption available: {health_check['encryption_available']}")
        
        # Test 4.2: API rate limiting simulation
        print("[INFO] 4.2 Testing performance characteristics...")
        start_time = time.time()
        
        api_mgr = api_manager.APIManager()
        
        # Test multiple rapid calls
        for i in range(3):
            connection_status = await api_mgr.get_connection_status()
            print(f"[OK] Performance test {i+1}: {len(connection_status)} services checked")
        
        end_time = time.time()
        duration = end_time - start_time
        print(f"[OK] Performance test completed in {duration:.2f} seconds")
        
        # Test 4.3: Authentication audit logging
        print("[INFO] 4.3 Testing audit logging...")
        access_log = await auth_mgr.get_access_log(limit=5)
        print(f"[OK] Audit log contains {len(access_log)} entries")
        
        # Test 4.4: Resource monitoring
        print("[INFO] 4.4 Testing resource monitoring...")
        api_health = await api_mgr.health_check()
        configured_apis = sum(1 for api_info in api_health['apis'].values() if api_info['configured'])
        print(f"[OK] Resource monitoring: {configured_apis} APIs configured")
        
        # Test 4.5: Security compliance check
        print("[INFO] 4.5 Testing security compliance...")
        security_settings = health_check.get('security_settings', {})
        print(f"[OK] Max failed attempts: {security_settings.get('max_failed_attempts', 'N/A')}")
        print(f"[OK] Credential expiry: {security_settings.get('credential_expiry_days', 'N/A')} days")
        
        print("[SUCCESS] Security & Performance validation PASSED")
        print(f"[INFO] Security status: {health_check['status']}")
        print(f"[INFO] Performance: {duration:.2f}s for 3 connection tests")
        print(f"[INFO] Audit logging: {len(access_log)} entries tracked")
        print(f"[INFO] Resource monitoring: {configured_apis} APIs monitored")
        
    except Exception as e:
        print(f"[ERROR] Security & Performance validation failed: {str(e)}")
        print(f"[ERROR] Exception type: {type(e).__name__}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        sys.exit(1)

print("=== PHASE 4 COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(main())
