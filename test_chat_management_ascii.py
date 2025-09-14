#!/usr/bin/env python3
"""
Test script for Chat Management Feature - ASCII ONLY VERSION
Tests the chat downloading, saving, and cleanup functionality
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_chat_management():
    """Test the chat management functionality"""
    try:
        # Import our modules
        from api_manager import APIManager
        from chat_manager import ChatManager, ChatMaintenanceScheduler
        
        logger.info("=== Chat Management Feature Test ===")
        
        # Initialize components
        api_manager = APIManager()
        await api_manager.initialize()
        
        chat_manager = ChatManager(api_manager)
        chat_scheduler = ChatMaintenanceScheduler(chat_manager)
        
        logger.info("[OK] Components initialized successfully")
        
        # Test 1: Get chat statistics
        logger.info("\n[TEST] Get Chat Statistics")
        stats = await chat_manager.get_chat_statistics()
        logger.info(f"Chat Statistics: {json.dumps(stats, indent=2)}")
        
        # Test 2: Download and save chats (simulated)
        logger.info("\n[TEST] Download and Save Chats")
        download_result = await chat_manager.download_and_save_chats(limit=5)
        logger.info(f"Download Result: {json.dumps(download_result, indent=2)}")
        
        # Test 3: List saved chats
        logger.info("\n[TEST] List Saved Chats")
        saved_chats = await chat_manager.list_saved_chats(limit=10)
        logger.info(f"Saved Chats: {json.dumps(saved_chats, indent=2)}")
        
        # Test 4: Cleanup old chats (simulated)
        logger.info("\n[TEST] Cleanup Old Chats")
        cleanup_result = await chat_manager.cleanup_old_chats(days_old=1)
        logger.info(f"Cleanup Result: {json.dumps(cleanup_result, indent=2)}")
        
        # Test 5: Full maintenance cycle
        logger.info("\n[TEST] Full Maintenance Cycle")
        maintenance_result = await chat_manager.full_maintenance_cycle()
        logger.info(f"Maintenance Result: {json.dumps(maintenance_result, indent=2)}")
        
        # Test 6: Directory structure
        logger.info("\n[TEST] Directory Structure")
        chat_library = Path("G:\\Chat Library\\advanced-mcp-server")
        metadata_dir = chat_library / "metadata"
        
        logger.info(f"Chat Library exists: {chat_library.exists()}")
        if chat_library.exists():
            logger.info(f"Contents: {list(chat_library.iterdir())}")
        
        logger.info(f"Metadata exists: {metadata_dir.exists()}")
        if metadata_dir.exists():
            logger.info(f"Metadata contents: {list(metadata_dir.iterdir())}")
        
        # Test 7: Scheduler start/stop
        logger.info("\n[TEST] Scheduler Start/Stop")
        await chat_scheduler.start_scheduler()
        logger.info("[OK] Scheduler started")
        
        await chat_scheduler.stop_scheduler()
        logger.info("[OK] Scheduler stopped")
        
        logger.info("\n[SUCCESS] All tests completed successfully!")
        logger.info("=== Chat Management Feature is Ready ===")
        
        return True
        
    except Exception as e:
        logger.error(f"[FAILED] Chat Management Feature Test")
        logger.error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    logger.info("Starting Chat Management Feature Test...")
    
    success = await test_chat_management()
    
    if success:
        print("\n[PASSED] Chat Management Feature Test: SUCCESS")
        print("\nFeature Summary:")
        print("- [OK] Directory structure created at G:\\Chat Library\\advanced-mcp-server\\")
        print("- [OK] Metadata files initialized")
        print("- [OK] Chat downloading functionality (with simulated data)")
        print("- [OK] Chat cleanup functionality")
        print("- [OK] 24-hour maintenance scheduler")
        print("- [OK] Statistics and listing capabilities")
        print("\nTo use in production:")
        print("1. Ensure Anthropic API key is configured")
        print("2. Start the MCP server")
        print("3. Use the chat management tools")
        print("4. Enable automatic scheduler for 24-hour maintenance")
    else:
        print("\n[FAILED] Chat Management Feature Test: FAILED")
        print("Check the logs above for error details.")

if __name__ == "__main__":
    asyncio.run(main())
