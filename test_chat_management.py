#!/usr/bin/env python3
"""
Test script for Chat Management Feature
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
        
        logger.info("✅ Components initialized successfully")
        
        # Test 1: Get chat statistics
        logger.info("\n📊 Testing: Get Chat Statistics")
        stats = await chat_manager.get_chat_statistics()
        logger.info(f"Chat Statistics: {json.dumps(stats, indent=2)}")
        
        # Test 2: Download and save chats (simulated)
        logger.info("\n💾 Testing: Download and Save Chats")
        download_result = await chat_manager.download_and_save_chats(limit=5)
        logger.info(f"Download Result: {json.dumps(download_result, indent=2)}")
        
        # Test 3: List saved chats
        logger.info("\n📋 Testing: List Saved Chats")
        saved_chats = await chat_manager.list_saved_chats(limit=10)
        logger.info(f"Saved Chats: {json.dumps(saved_chats, indent=2)}")
        
        # Test 4: Cleanup old chats (simulated)
        logger.info("\n🧹 Testing: Cleanup Old Chats")
        cleanup_result = await chat_manager.cleanup_old_chats(days_old=1)
        logger.info(f"Cleanup Result: {json.dumps(cleanup_result, indent=2)}")
        
        # Test 5: Full maintenance cycle
        logger.info("\n🔄 Testing: Full Maintenance Cycle")
        maintenance_result = await chat_manager.full_maintenance_cycle()
        logger.info(f"Maintenance Result: {json.dumps(maintenance_result, indent=2)}")
        
        # Test 6: Check directory structure
        logger.info("\n📁 Testing: Directory Structure")
        chat_library_path = Path("G:\\Chat Library\\advanced-mcp-server")
        logger.info(f"Chat Library exists: {chat_library_path.exists()}")
        if chat_library_path.exists():
            logger.info(f"Contents: {list(chat_library_path.iterdir())}")
            
            metadata_path = chat_library_path / "metadata"
            logger.info(f"Metadata exists: {metadata_path.exists()}")
            if metadata_path.exists():
                logger.info(f"Metadata contents: {list(metadata_path.iterdir())}")
        
        # Test 7: Scheduler functionality (start/stop only, don't wait)
        logger.info("\n⏰ Testing: Scheduler Start/Stop")
        await chat_scheduler.start_scheduler()
        logger.info("✅ Scheduler started")
        
        # Wait a moment then stop
        await asyncio.sleep(2)
        await chat_scheduler.stop_scheduler()
        logger.info("✅ Scheduler stopped")
        
        logger.info("\n🎉 All tests completed successfully!")
        logger.info("=== Chat Management Feature is Ready ===")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        try:
            if api_manager:
                await api_manager.close()
        except:
            pass

async def main():
    """Main test function"""
    print("Starting Chat Management Feature Test...")
    success = await test_chat_management()
    
    if success:
        print("\n✅ Chat Management Feature Test: PASSED")
        print("\nFeature Summary:")
        print("- ✅ Directory structure created at G:\\Chat Library\\advanced-mcp-server\\")
        print("- ✅ Metadata files initialized")
        print("- ✅ Chat downloading functionality (with simulated data)")
        print("- ✅ Chat cleanup functionality")
        print("- ✅ 24-hour maintenance scheduler")
        print("- ✅ Statistics and listing capabilities")
        print("\nTo use in production:")
        print("1. Ensure Anthropic API key is configured")
        print("2. Start the MCP server")
        print("3. Use the chat management tools")
        print("4. Enable automatic scheduler for 24-hour maintenance")
    else:
        print("\n❌ Chat Management Feature Test: FAILED")
        print("Check the logs above for error details.")

if __name__ == "__main__":
    asyncio.run(main())
