#!/usr/bin/env python3
"""
Session 7 - Google Service Account Integration Test (Console Safe)
Tests the new service account authentication for all Google services
"""

import asyncio
import logging
import os
import sys
import traceback
from datetime import datetime

# Add project directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from api_manager import APIManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_service_account_authentication():
    """Test Google service account authentication and initialization"""
    logger.info("[STARTING] Testing Google Service Account Authentication...")
    
    api_manager = APIManager()
    
    try:
        # Initialize the API manager
        await api_manager.initialize()
        
        # Check if all Google services are initialized
        services_status = {
            "Google Drive": api_manager.google_drive_service is not None,
            "Google Sheets": api_manager.google_sheets_service is not None,
            "Google Docs": api_manager.google_docs_service is not None,
            "Google Calendar": api_manager.google_calendar_service is not None
        }
        
        logger.info("Service Account Authentication Results:")
        for service, status in services_status.items():
            status_text = "[READY]" if status else "[NOT INITIALIZED]"
            logger.info(f"  {status_text} {service}")
        
        # Verify all services are working
        all_services_ready = all(services_status.values())
        
        if all_services_ready:
            logger.info("[SUCCESS] All Google services initialized with service account!")
            return True
        else:
            logger.error("[FAILURE] Some Google services failed to initialize")
            return False
            
    except Exception as e:
        logger.error(f"[FAILURE] Service account authentication failed: {e}")
        logger.error(f"Error details: {traceback.format_exc()}")
        return False
    finally:
        if api_manager:
            await api_manager.close()

async def test_google_drive_operations():
    """Test basic Google Drive operations with service account"""
    logger.info("[STARTING] Testing Google Drive Operations...")
    
    api_manager = APIManager()
    
    try:
        await api_manager.initialize()
        
        if not api_manager.google_drive_service:
            logger.error("[FAILURE] Google Drive service not available")
            return False
        
        # Test: List files in Drive (just a few to verify access)
        try:
            result = await api_manager.google_drive_operation(
                operation="list",
                parameters={"page_size": 5}
            )
            
            file_count = len(result.get("files", []))
            logger.info(f"[SUCCESS] Successfully accessed Google Drive - Found {file_count} files")
            return True
            
        except Exception as e:
            logger.error(f"[FAILURE] Google Drive operation failed: {e}")
            return False
            
    except Exception as e:
        logger.error(f"[FAILURE] Google Drive test failed: {e}")
        return False
    finally:
        if api_manager:
            await api_manager.close()

async def test_api_health_check():
    """Test API health check with all services"""
    logger.info("[STARTING] Testing API Health Check...")
    
    api_manager = APIManager()
    
    try:
        await api_manager.initialize()
        
        health_status = await api_manager.health_check()
        
        logger.info("API Health Check Results:")
        for api_name, status in health_status["apis"].items():
            status_text = "[READY]" if status["status"] == "ready" else "[NOT CONFIGURED]"
            logger.info(f"  {status_text} {api_name.upper()}")
        
        # Check if Google services are healthy
        google_status = health_status["apis"].get("google", {})
        google_ready = google_status.get("status") == "ready"
        
        if google_ready:
            logger.info("[SUCCESS] All Google services are healthy!")
            return True
        else:
            logger.warning("[WARNING] Google services not fully ready")
            return False
            
    except Exception as e:
        logger.error(f"[FAILURE] Health check failed: {e}")
        return False
    finally:
        if api_manager:
            await api_manager.close()

async def main():
    """Run all service account tests"""
    logger.info("=" * 60)
    logger.info("[SESSION 7] GOOGLE SERVICE ACCOUNT INTEGRATION TEST")
    logger.info("=" * 60)
    
    test_results = []
    
    # Test 1: Service Account Authentication
    logger.info("\n[TEST 1] Service Account Authentication")
    result1 = await test_service_account_authentication()
    test_results.append(("Service Account Auth", result1))
    
    # Test 2: Google Drive Operations
    logger.info("\n[TEST 2] Google Drive Operations")
    result2 = await test_google_drive_operations()
    test_results.append(("Google Drive Ops", result2))
    
    # Test 3: API Health Check
    logger.info("\n[TEST 3] API Health Check")
    result3 = await test_api_health_check()
    test_results.append(("API Health Check", result3))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("[SUMMARY] TEST RESULTS")
    logger.info("=" * 60)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        logger.info(f"{status} - {test_name}")
        if result:
            passed_tests += 1
    
    logger.info("-" * 60)
    logger.info(f"TOTAL: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("[SUCCESS] All service account tests passed!")
        logger.info("[READY] Google Service Account integration is working perfectly!")
        return 0
    else:
        logger.error("[FAILURE] Some service account tests failed!")
        logger.error("[ACTION] Service account integration needs attention!")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        logger.error(f"Error details: {traceback.format_exc()}")
        sys.exit(1)
