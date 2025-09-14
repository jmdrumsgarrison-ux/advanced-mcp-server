#!/usr/bin/env python3
"""
Production APIManager test for Session 7
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
        
        # Test specific API functionality (Claude API)
        if api_manager.api_keys["anthropic"]:
            try:
                # Simple test call to Claude API
                test_data = {
                    "model": "claude-3-sonnet-20240229",
                    "max_tokens": 50,
                    "messages": [{"role": "user", "content": "Hello, respond with 'PRODUCTION_TEST_SUCCESS'"}]
                }
                
                response = await api_manager.claude_api_call("messages", data=test_data)
                
                if "content" in response and len(response["content"]) > 0:
                    response_text = response["content"][0].get("text", "")
                    if "PRODUCTION_TEST_SUCCESS" in response_text:
                        logger.info("[SUCCESS] Live Claude API test passed")
                    else:
                        logger.warning(f"[WARNING] Unexpected Claude response: {response_text}")
                else:
                    logger.warning("[WARNING] Claude API returned unexpected format")
                    
            except Exception as e:
                logger.error(f"[FAILURE] Claude API test failed: {e}")
        
        # Validate Google services specifically
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
        
        if all_google_ready:
            logger.info("[SUCCESS] All Google services are ready")
        else:
            logger.error("[FAILURE] Some Google services are not ready")
            return False
        
        # Summary
        total_apis = len(status)
        configured_apis = len(connected_apis)
        
        logger.info(f"\nAPIManager Summary:")
        logger.info(f"Total APIs: {total_apis}")
        logger.info(f"Configured: {configured_apis}")
        logger.info(f"Google Services: {'ALL READY' if all_google_ready else 'SOME MISSING'}")
        
        if configured_apis >= 6:  # Should have at least 6 APIs configured
            logger.info("[SUCCESS] Production APIManager test passed")
            return True
        else:
            logger.error("[FAILURE] Insufficient APIs configured")
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
    logger.info("[SESSION 7] PRODUCTION APIMANAGER TEST")
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
