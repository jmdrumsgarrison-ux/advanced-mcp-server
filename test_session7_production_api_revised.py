#!/usr/bin/env python3
"""
Production APIManager test for Session 7 (Revised)
Tests that the production API manager works with service account integration
"""

import asyncio
import logging
import os
import sys
import traceback

# Add project directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from api_manager import APIManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_production_api_manager():
    """Test production API manager initialization and functionality"""
    logger.info("[STARTING] Production APIManager test")
    
    api_manager = APIManager()
    
    try:
        # Test initialization
        await api_manager.initialize()
        logger.info("[SUCCESS] APIManager initialized successfully")
        
        # Test connection status
        status = await api_manager.get_connection_status()
        logger.info("Connection Status:")
        
        connected_apis = []
        failed_apis = []
        
        for api_name, api_status in status.items():
            if api_status == "connected":
                connected_apis.append(api_name)
                logger.info(f"  [CONNECTED] {api_name.upper()}")
            else:
                failed_apis.append(api_name)
                logger.info(f"  [NOT CONFIGURED] {api_name.upper()}")
        
        # Test health check
        health = await api_manager.health_check()
        logger.info(f"Health check timestamp: {health['timestamp']}")
        
        # Validate Google services specifically (this is what we really care about)
        google_services = {
            "Drive": api_manager.google_drive_service is not None,
            "Sheets": api_manager.google_sheets_service is not None,
            "Docs": api_manager.google_docs_service is not None,
            "Calendar": api_manager.google_calendar_service is not None
        }
        
        logger.info("Google Services Status:")
        all_google_ready = True
        for service, ready in google_services.items():
            status_text = "[READY]" if ready else "[NOT READY]"
            logger.info(f"  {status_text} Google {service}")
            if not ready:
                all_google_ready = False
        
        # Check API key availability (what we can verify without making calls)
        api_keys_available = {
            "anthropic": bool(api_manager.api_keys["anthropic"]),
            "openai": bool(api_manager.api_keys["openai"]),
            "github": bool(api_manager.api_keys["github"]),
            "huggingface": bool(api_manager.api_keys["huggingface"]),
            "together": bool(api_manager.api_keys["together"]),
            "google": bool(api_manager.api_keys["google"])
        }
        
        logger.info("API Keys Status:")
        configured_count = 0
        for api_name, has_key in api_keys_available.items():
            status_text = "[CONFIGURED]" if has_key else "[NOT CONFIGURED]"
            logger.info(f"  {status_text} {api_name.upper()}")
            if has_key:
                configured_count += 1
        
        # Summary
        logger.info(f"\nAPIManager Summary:")
        logger.info(f"Connected APIs: {len(connected_apis)}")
        logger.info(f"API Keys Configured: {configured_count}")
        logger.info(f"Google Services: {'ALL READY' if all_google_ready else 'SOME MISSING'}")
        
        # Success criteria (more realistic):
        # 1. Google services must all be ready (this is what we implemented)
        # 2. At least 4 API connections should be working
        # 3. APIManager should initialize without errors
        
        if all_google_ready and len(connected_apis) >= 4:
            logger.info("[SUCCESS] Production APIManager test passed")
            return True
        else:
            logger.error(f"[FAILURE] Requirements not met - Google ready: {all_google_ready}, Connected APIs: {len(connected_apis)}")
            return False
        
    except Exception as e:
        logger.error(f"[FAILURE] Production APIManager test failed: {e}")
        logger.error(f"Error details: {traceback.format_exc()}")
        return False
    finally:
        if api_manager:
            await api_manager.close()

async def main():
    """Run production APIManager test"""
    logger.info("=" * 60)
    logger.info("[SESSION 7] PRODUCTION APIMANAGER TEST (REVISED)")
    logger.info("=" * 60)
    
    success = await test_production_api_manager()
    
    if success:
        logger.info("[SUCCESS] Production APIManager test completed successfully")
        return 0
    else:
        logger.error("[FAILURE] Production APIManager test failed")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        sys.exit(1)
