#!/usr/bin/env python3
"""
Test script to verify MCP server can start up and initialize properly
"""

import asyncio
import logging
import sys
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_server_startup():
    """Test that the server can initialize all components"""
    try:
        logger.info("=== Advanced MCP Server Startup Test ===")
        
        # Import our main server class
        from main import AdvancedMCPServer
        
        logger.info("✅ Main server class imported successfully")
        
        # Create server instance
        server = AdvancedMCPServer()
        logger.info("✅ Server instance created successfully")
        
        # Test component initialization
        logger.info("🔧 Testing component initialization...")
        
        # Initialize components manually (without running the full server)
        await server.api_manager.initialize()
        logger.info("✅ API Manager initialized")
        
        await server.rules_engine.initialize()
        logger.info("✅ Rules Engine initialized")
        
        await server.session_manager.initialize()
        logger.info("✅ Session Manager initialized")
        
        await server.file_ops.initialize()
        logger.info("✅ File Operations initialized")
        
        await server.auth_manager.initialize()
        logger.info("✅ Auth Manager initialized")
        
        # Test chat manager initialization
        logger.info("📞 Testing Chat Manager...")
        chat_stats = await server.chat_manager.get_chat_statistics()
        logger.info(f"✅ Chat Manager working - Stats: {chat_stats}")
        
        logger.info("\n🎉 SERVER STARTUP TEST: SUCCESS")
        logger.info("All components initialized successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ SERVER STARTUP TEST: FAILED")
        logger.error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_server_startup())
    sys.exit(0 if result else 1)
