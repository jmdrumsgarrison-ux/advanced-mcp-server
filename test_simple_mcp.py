#!/usr/bin/env python3
"""
Simple MCP Server Test - Minimal implementation to test tool registration
"""

import asyncio
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the server instance
server = Server("test-mcp-server")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="get_server_status",
            description="Get server status and health information",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        Tool(
            name="test_huggingface",
            description="Test HuggingFace API connection",
            inputSchema={
                "type": "object", 
                "properties": {},
                "additionalProperties": False
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls"""
    
    if name == "get_server_status":
        status = {
            "server": "Test MCP Server",
            "status": "healthy", 
            "timestamp": datetime.now().isoformat(),
            "message": "Simple test server is working!"
        }
        return [types.TextContent(
            type="text",
            text=json.dumps(status, indent=2)
        )]
    
    elif name == "test_huggingface":
        # Import here to avoid import errors if not available
        try:
            import os
            hf_token = os.getenv('HUGGINGFACE_TOKEN')
            if hf_token:
                result = {
                    "status": "success",
                    "message": "HuggingFace token found",
                    "token_preview": f"{hf_token[:8]}..."
                }
            else:
                result = {
                    "status": "error", 
                    "message": "HuggingFace token not found"
                }
        except Exception as e:
            result = {
                "status": "error",
                "message": f"Error testing HuggingFace: {str(e)}"
            }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Main entry point"""
    logger.info("Starting Test MCP Server...")
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, 
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
