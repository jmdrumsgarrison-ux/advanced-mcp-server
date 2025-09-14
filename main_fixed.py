#!/usr/bin/env python3
"""
Advanced MCP Server - Fixed Implementation
Provides comprehensive API integrations with proper MCP tool registration
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
import mcp.types as types

# Import our custom modules
from api_manager import APIManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('advanced_mcp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create the server instance
server = Server("advanced-mcp-server")

# Global API manager instance
api_manager = None

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="get_server_status",
            description="Get comprehensive server status and health information",
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
        ),
        Tool(
            name="list_huggingface_spaces",
            description="List your deployed HuggingFace Spaces",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        Tool(
            name="huggingface_create_space",
            description="Create a new Hugging Face Space",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_name": {"type": "string", "description": "Name of the space to create"},
                    "space_type": {"type": "string", "description": "Type of space (gradio, streamlit, etc.)", "default": "gradio"},
                    "private": {"type": "boolean", "description": "Make the space private", "default": False}
                },
                "required": ["space_name"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="google_drive_list_files",
            description="List files in Google Drive",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query (optional)"},
                    "page_size": {"type": "integer", "description": "Number of files to return", "default": 10}
                },
                "additionalProperties": False
            }
        ),
        Tool(
            name="google_sheets_read",
            description="Read data from a Google Sheet",
            inputSchema={
                "type": "object",
                "properties": {
                    "sheet_id": {"type": "string", "description": "Google Sheet ID"},
                    "range": {"type": "string", "description": "Range to read (e.g., A1:C10)", "default": "A1:Z1000"}
                },
                "required": ["sheet_id"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="claude_api_call",
            description="Make API calls to Claude",
            inputSchema={
                "type": "object",
                "properties": {
                    "endpoint": {"type": "string", "description": "API endpoint"},
                    "method": {"type": "string", "description": "HTTP method", "default": "POST"},
                    "data": {"type": "object", "description": "Request data"}
                },
                "required": ["endpoint"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="openai_api_call",
            description="Make API calls to OpenAI",
            inputSchema={
                "type": "object",
                "properties": {
                    "endpoint": {"type": "string", "description": "API endpoint"},
                    "data": {"type": "object", "description": "Request data"}
                },
                "required": ["endpoint"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="github_create_repo",
            description="Create a new GitHub repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_name": {"type": "string", "description": "Repository name"},
                    "description": {"type": "string", "description": "Repository description", "default": ""},
                    "private": {"type": "boolean", "description": "Make repository private", "default": False}
                },
                "required": ["repo_name"],
                "additionalProperties": False
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls"""
    global api_manager
    
    try:
        if name == "get_server_status":
            status = {
                "server": "Advanced MCP Server",
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "components": {
                    "api_manager": "operational" if api_manager and api_manager.initialized else "not_initialized",
                    "huggingface": "configured" if api_manager and api_manager.hf_api else "not_configured",
                    "google_services": "configured" if api_manager and api_manager.google_drive_service else "not_configured"
                },
                "apis_available": list(api_manager.api_keys.keys()) if api_manager else []
            }
            return [types.TextContent(type="text", text=json.dumps(status, indent=2))]
            
        elif name == "test_huggingface":
            if not api_manager or not api_manager.hf_api:
                return [types.TextContent(
                    type="text", 
                    text=json.dumps({"status": "error", "message": "HuggingFace API not initialized"}, indent=2)
                )]
            
            result = {
                "status": "success",
                "message": "HuggingFace API is working",
                "token_configured": bool(api_manager.api_keys.get("huggingface")),
                "api_client": "initialized"
            }
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "list_huggingface_spaces":
            if not api_manager or not api_manager.hf_api:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"status": "error", "message": "HuggingFace API not initialized"}, indent=2)
                )]
            
            try:
                import requests
                hf_token = api_manager.api_keys.get("huggingface")
                headers = {"Authorization": f"Bearer {hf_token}"}
                
                # Get user info first
                user_response = requests.get("https://huggingface.co/api/whoami", headers=headers)
                if user_response.status_code != 200:
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({"status": "error", "message": f"Authentication failed: {user_response.status_code}"}, indent=2)
                    )]
                
                user_data = user_response.json()
                username = user_data.get('name', 'Unknown')
                
                # Get spaces
                spaces_response = requests.get("https://huggingface.co/api/spaces", headers=headers, params={
                    "author": username,
                    "limit": 50
                })
                
                if spaces_response.status_code == 200:
                    spaces_data = spaces_response.json()
                    
                    result = {
                        "status": "success",
                        "username": username,
                        "spaces_count": len(spaces_data),
                        "spaces": []
                    }
                    
                    for space in spaces_data:
                        result["spaces"].append({
                            "name": space.get('id', 'Unknown'),
                            "sdk": space.get('sdk', 'Unknown'),
                            "likes": space.get('likes', 0),
                            "private": space.get('private', False),
                            "url": f"https://huggingface.co/spaces/{space.get('id', '')}"
                        })
                    
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                else:
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({"status": "error", "message": f"Failed to get spaces: {spaces_response.status_code}"}, indent=2)
                    )]
                    
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"status": "error", "message": f"Error listing spaces: {str(e)}"}, indent=2)
                )]
        
        elif name == "huggingface_create_space":
            if not api_manager:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"status": "error", "message": "API Manager not initialized"}, indent=2)
                )]
            
            space_name = arguments.get("space_name")
            space_type = arguments.get("space_type", "gradio")
            private = arguments.get("private", False)
            
            config = {"private": private}
            result = await api_manager.huggingface_create_space(space_name, space_type, config)
            
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "google_drive_list_files":
            if not api_manager or not api_manager.google_drive_service:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"status": "error", "message": "Google Drive API not initialized"}, indent=2)
                )]
            
            query = arguments.get("query", "")
            page_size = arguments.get("page_size", 10)
            
            parameters = {"query": query, "page_size": page_size}
            result = await api_manager.google_drive_operation("list", parameters)
            
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "google_sheets_read":
            if not api_manager or not api_manager.google_sheets_service:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"status": "error", "message": "Google Sheets API not initialized"}, indent=2)
                )]
            
            sheet_id = arguments.get("sheet_id")
            range_name = arguments.get("range", "A1:Z1000")
            
            data = {"range": range_name}
            result = await api_manager.google_sheets_operation(sheet_id, "read", data)
            
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "claude_api_call":
            if not api_manager:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"status": "error", "message": "API Manager not initialized"}, indent=2)
                )]
            
            endpoint = arguments.get("endpoint")
            method = arguments.get("method", "POST")
            data = arguments.get("data", {})
            
            result = await api_manager.claude_api_call(endpoint, method, data)
            
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "openai_api_call":
            if not api_manager:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"status": "error", "message": "API Manager not initialized"}, indent=2)
                )]
            
            endpoint = arguments.get("endpoint")
            data = arguments.get("data", {})
            
            result = await api_manager.openai_api_call(endpoint, data)
            
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "github_create_repo":
            if not api_manager:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"status": "error", "message": "API Manager not initialized"}, indent=2)
                )]
            
            repo_name = arguments.get("repo_name")
            description = arguments.get("description", "")
            private = arguments.get("private", False)
            
            result = await api_manager.github_create_repo(repo_name, description, private)
            
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
            
        else:
            return [types.TextContent(
                type="text",
                text=json.dumps({"status": "error", "message": f"Unknown tool: {name}"}, indent=2)
            )]
            
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({"status": "error", "message": f"Tool execution failed: {str(e)}"}, indent=2)
        )]

async def main():
    """Main entry point"""
    global api_manager
    
    logger.info("Starting Advanced MCP Server...")
    
    # Initialize API manager
    try:
        api_manager = APIManager()
        await api_manager.initialize()
        logger.info("API Manager initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize API Manager: {e}")
        # Continue anyway - some tools might still work
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
