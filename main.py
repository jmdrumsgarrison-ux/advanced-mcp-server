#!/usr/bin/env python3
"""
Advanced MCP Server - Comprehensive Automation and Rules Engine
Provides session management, external API integrations, and local file operations
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from mcp import server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource

# Import our custom modules
from api_manager import APIManager
from rules_engine import RulesEngine
from session_manager import SessionManager
from file_operations import FileOperations
from auth_manager import AuthManager

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

class AdvancedMCPServer:
    """Main MCP Server class with comprehensive capabilities"""
    
    def __init__(self):
        self.server = server.Server("advanced-mcp-server")
        self.api_manager = APIManager()
        self.rules_engine = RulesEngine()
        self.session_manager = SessionManager()
        self.file_ops = FileOperations()
        self.auth_manager = AuthManager()
        
        # Initialize server capabilities
        self._register_tools()
        self._register_resources()
        
    def _register_tools(self):
        """Register all available tools"""
        
        # Register tool schemas
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List all available tools with their schemas"""
            return [
                Tool(
                    name="list_huggingface_spaces",
                    description="List HuggingFace Spaces with optional filters",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filter": {
                                "type": "string",
                                "description": "Filter string for spaces"
                            },
                            "author": {
                                "type": "string",
                                "description": "Author username to filter by"
                            },
                            "search": {
                                "type": "string",
                                "description": "Search term to filter spaces"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 10
                            }
                        },
                        "additionalProperties": False
                    }
                ),
                Tool(
                    name="test_huggingface_debug",
                    description="Debug HuggingFace authentication within server context",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False
                    }
                ),
                Tool(
                    name="huggingface_create_space",
                    description="Create a new HuggingFace Space",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "space_name": {
                                "type": "string",
                                "description": "Name of the space to create"
                            },
                            "space_type": {
                                "type": "string",
                                "description": "Type of space (gradio, streamlit, etc.)",
                                "default": "gradio"
                            },
                            "private": {
                                "type": "boolean",
                                "description": "Whether the space should be private",
                                "default": False
                            }
                        },
                        "required": ["space_name"],
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
                    name="get_server_status",
                    description="Get comprehensive server status and health",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False
                    }
                )
            ]
        
        # === SESSION MANAGEMENT TOOLS ===
        
        @self.server.call_tool()
        async def test_huggingface_debug(arguments: dict) -> list[TextContent]:
            """Debug HuggingFace authentication within server context"""
            try:
                result = await self.api_manager.test_huggingface_debug()
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(type="text", text=f"Debug Error: {str(e)}")]

        @self.server.call_tool()
        async def start_session(arguments: dict) -> list[TextContent]:
            """Start a new session with specified type and configuration"""
            try:
                session_type = arguments.get("session_type", "default")
                config = arguments.get("config", {})
                
                session_id = await self.session_manager.start_session(session_type, config)
                
                return [TextContent(
                    type="text",
                    text=f"Session {session_id} started successfully with type: {session_type}"
                )]
            except Exception as e:
                logger.error(f"Error starting session: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.call_tool()
        async def get_session_status(arguments: dict) -> list[TextContent]:
            """Get current session status and metrics"""
            try:
                session_id = arguments.get("session_id")
                status = await self.session_manager.get_session_status(session_id)
                
                return [TextContent(
                    type="text",
                    text=json.dumps(status, indent=2)
                )]
            except Exception as e:
                logger.error(f"Error getting session status: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.call_tool()
        async def execute_rule(arguments: dict) -> list[TextContent]:
            """Execute a specific rule or rule set"""
            try:
                rule_name = arguments.get("rule_name")
                parameters = arguments.get("parameters", {})
                
                result = await self.rules_engine.execute_rule(rule_name, parameters)
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                logger.error(f"Error executing rule: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        # === CLAUDE API TOOLS ===
        
        @self.server.call_tool()
        async def claude_api_call(arguments: dict) -> list[TextContent]:
            """Make API calls to Claude"""
            try:
                endpoint = arguments.get("endpoint")
                method = arguments.get("method", "POST")
                data = arguments.get("data", {})
                
                result = await self.api_manager.claude_api_call(endpoint, method, data)
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                logger.error(f"Error calling Claude API: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.call_tool()
        async def export_claude_chats(arguments: dict) -> list[TextContent]:
            """Export Claude chat conversations"""
            try:
                chat_filter = arguments.get("filter", {})
                output_path = arguments.get("output_path", "claude_chats_export.json")
                
                result = await self.api_manager.export_claude_chats(chat_filter, output_path)
                
                return [TextContent(
                    type="text",
                    text=f"Chats exported successfully to {output_path}. {result['count']} chats exported."
                )]
            except Exception as e:
                logger.error(f"Error exporting Claude chats: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        # === OPENAI API TOOLS ===
        
        @self.server.call_tool()
        async def openai_api_call(arguments: dict) -> list[TextContent]:
            """Make API calls to OpenAI"""
            try:
                endpoint = arguments.get("endpoint")
                data = arguments.get("data", {})
                
                result = await self.api_manager.openai_api_call(endpoint, data)
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                logger.error(f"Error calling OpenAI API: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        # === HUGGING FACE API TOOLS ===
        
        # Space Management Tools
        
        @self.server.call_tool()
        async def list_huggingface_spaces(arguments: dict) -> list[TextContent]:
            """List HuggingFace Spaces with optional filters"""
            try:
                filter_val = arguments.get("filter")
                author = arguments.get("author")
                search = arguments.get("search")
                limit = arguments.get("limit", 10)
                
                result = await self.api_manager.huggingface_list_spaces(
                    filter=filter_val,
                    author=author,
                    search=search,
                    limit=limit
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                logger.error(f"Error listing HuggingFace spaces: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.call_tool()
        async def get_huggingface_space_info(arguments: dict) -> list[TextContent]:
            """Get detailed information about a specific HuggingFace Space"""
            try:
                repo_id = arguments.get("repo_id")
                if not repo_id:
                    raise ValueError("repo_id is required")
                
                revision = arguments.get("revision")
                files_metadata = arguments.get("files_metadata", False)
                
                result = await self.api_manager.huggingface_space_info(
                    repo_id=repo_id,
                    revision=revision,
                    files_metadata=files_metadata
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                logger.error(f"Error getting HuggingFace space info: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.call_tool()
        async def duplicate_huggingface_space(arguments: dict) -> list[TextContent]:
            """Duplicate a HuggingFace Space"""
            try:
                from_id = arguments.get("from_id")
                if not from_id:
                    raise ValueError("from_id is required")
                
                to_id = arguments.get("to_id")
                private = arguments.get("private")
                hardware = arguments.get("hardware")
                secrets = arguments.get("secrets")
                
                result = await self.api_manager.huggingface_duplicate_space(
                    from_id=from_id,
                    to_id=to_id,
                    private=private,
                    hardware=hardware,
                    secrets=secrets
                )
                
                return [TextContent(
                    type="text",
                    text=f"Space duplicated successfully: {result['url']}"
                )]
            except Exception as e:
                logger.error(f"Error duplicating HuggingFace space: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.call_tool()
        async def pause_huggingface_space(arguments: dict) -> list[TextContent]:
            """Pause a HuggingFace Space"""
            try:
                repo_id = arguments.get("repo_id")
                if not repo_id:
                    raise ValueError("repo_id is required")
                
                result = await self.api_manager.huggingface_pause_space(repo_id=repo_id)
                
                return [TextContent(
                    type="text",
                    text=f"Space '{repo_id}' paused successfully"
                )]
            except Exception as e:
                logger.error(f"Error pausing HuggingFace space: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.call_tool()
        async def restart_huggingface_space(arguments: dict) -> list[TextContent]:
            """Restart a HuggingFace Space"""
            try:
                repo_id = arguments.get("repo_id")
                if not repo_id:
                    raise ValueError("repo_id is required")
                
                factory_reboot = arguments.get("factory_reboot", False)
                
                result = await self.api_manager.huggingface_restart_space(
                    repo_id=repo_id,
                    factory_reboot=factory_reboot
                )
                
                return [TextContent(
                    type="text",
                    text=f"Space '{repo_id}' restarted successfully (factory_reboot: {factory_reboot})"
                )]
            except Exception as e:
                logger.error(f"Error restarting HuggingFace space: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        # File Operations Tools
        
        @self.server.call_tool()
        async def upload_file_to_huggingface(arguments: dict) -> list[TextContent]:
            """Upload a file to a HuggingFace repository"""
            try:
                path_or_fileobj = arguments.get("path_or_fileobj")
                path_in_repo = arguments.get("path_in_repo")
                repo_id = arguments.get("repo_id")
                
                if not all([path_or_fileobj, path_in_repo, repo_id]):
                    raise ValueError("path_or_fileobj, path_in_repo, and repo_id are required")
                
                repo_type = arguments.get("repo_type", "model")
                commit_message = arguments.get("commit_message")
                
                result = await self.api_manager.huggingface_upload_file(
                    path_or_fileobj=path_or_fileobj,
                    path_in_repo=path_in_repo,
                    repo_id=repo_id,
                    repo_type=repo_type,
                    commit_message=commit_message
                )
                
                return [TextContent(
                    type="text",
                    text=f"File uploaded successfully: {result['path_in_repo']} to {result['repo_id']}"
                )]
            except Exception as e:
                logger.error(f"Error uploading file to HuggingFace: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.call_tool()
        async def upload_folder_to_huggingface(arguments: dict) -> list[TextContent]:
            """Upload a folder to a HuggingFace repository"""
            try:
                repo_id = arguments.get("repo_id")
                folder_path = arguments.get("folder_path")
                
                if not all([repo_id, folder_path]):
                    raise ValueError("repo_id and folder_path are required")
                
                path_in_repo = arguments.get("path_in_repo")
                repo_type = arguments.get("repo_type", "model")
                commit_message = arguments.get("commit_message")
                
                result = await self.api_manager.huggingface_upload_folder(
                    repo_id=repo_id,
                    folder_path=folder_path,
                    path_in_repo=path_in_repo,
                    repo_type=repo_type,
                    commit_message=commit_message
                )
                
                return [TextContent(
                    type="text",
                    text=f"Folder uploaded successfully: {result['folder_path']} to {result['repo_id']}"
                )]
            except Exception as e:
                logger.error(f"Error uploading folder to HuggingFace: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.call_tool()
        async def download_file_from_huggingface(arguments: dict) -> list[TextContent]:
            """Download a file from a HuggingFace repository"""
            try:
                repo_id = arguments.get("repo_id")
                filename = arguments.get("filename")
                
                if not all([repo_id, filename]):
                    raise ValueError("repo_id and filename are required")
                
                subfolder = arguments.get("subfolder")
                repo_type = arguments.get("repo_type", "model")
                revision = arguments.get("revision")
                cache_dir = arguments.get("cache_dir")
                
                result = await self.api_manager.huggingface_download_file(
                    repo_id=repo_id,
                    filename=filename,
                    subfolder=subfolder,
                    repo_type=repo_type,
                    revision=revision,
                    cache_dir=cache_dir
                )
                
                return [TextContent(
                    type="text",
                    text=f"File downloaded successfully: {result['filename']} from {result['repo_id']} to {result['local_path']}"
                )]
            except Exception as e:
                logger.error(f"Error downloading file from HuggingFace: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.call_tool()
        async def delete_file_from_huggingface(arguments: dict) -> list[TextContent]:
            """Delete a file from a HuggingFace repository"""
            try:
                path_in_repo = arguments.get("path_in_repo")
                repo_id = arguments.get("repo_id")
                
                if not all([path_in_repo, repo_id]):
                    raise ValueError("path_in_repo and repo_id are required")
                
                repo_type = arguments.get("repo_type", "model")
                revision = arguments.get("revision")
                commit_message = arguments.get("commit_message")
                
                result = await self.api_manager.huggingface_delete_file(
                    path_in_repo=path_in_repo,
                    repo_id=repo_id,
                    repo_type=repo_type,
                    revision=revision,
                    commit_message=commit_message
                )
                
                return [TextContent(
                    type="text",
                    text=f"File deleted successfully: {result['path_in_repo']} from {result['repo_id']}"
                )]
            except Exception as e:
                logger.error(f"Error deleting file from HuggingFace: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.call_tool()
        async def check_file_exists_huggingface(arguments: dict) -> list[TextContent]:
            """Check if a file exists in a HuggingFace repository"""
            try:
                repo_id = arguments.get("repo_id")
                filename = arguments.get("filename")
                
                if not all([repo_id, filename]):
                    raise ValueError("repo_id and filename are required")
                
                repo_type = arguments.get("repo_type", "model")
                revision = arguments.get("revision")
                
                result = await self.api_manager.huggingface_file_exists(
                    repo_id=repo_id,
                    filename=filename,
                    repo_type=repo_type,
                    revision=revision
                )
                
                exists_text = "exists" if result['exists'] else "does not exist"
                return [TextContent(
                    type="text",
                    text=f"File {result['filename']} {exists_text} in {result['repo_id']}"
                )]
            except Exception as e:
                logger.error(f"Error checking file existence in HuggingFace: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        # Search & Discovery Tools
        
        @self.server.call_tool()
        async def list_huggingface_models(arguments: dict) -> list[TextContent]:
            """List models on the Hugging Face Hub with optional filters"""
            try:
                filter_str = arguments.get("filter")
                author = arguments.get("author")
                search = arguments.get("search")
                library = arguments.get("library")
                task = arguments.get("task")
                sort = arguments.get("sort")
                limit = arguments.get("limit", 10)
                
                result = await self.api_manager.huggingface_list_models(
                    filter_str=filter_str,
                    author=author,
                    search=search,
                    library=library,
                    task=task,
                    sort=sort,
                    limit=limit
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                logger.error(f"Error listing HuggingFace models: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.call_tool()
        async def get_huggingface_model_info(arguments: dict) -> list[TextContent]:
            """Get detailed information about a specific HuggingFace model"""
            try:
                repo_id = arguments.get("repo_id")
                if not repo_id:
                    raise ValueError("repo_id is required")
                
                revision = arguments.get("revision")
                files_metadata = arguments.get("files_metadata", False)
                security_status = arguments.get("security_status")
                
                result = await self.api_manager.huggingface_model_info(
                    repo_id=repo_id,
                    revision=revision,
                    files_metadata=files_metadata,
                    security_status=security_status
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                logger.error(f"Error getting HuggingFace model info: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.call_tool()
        async def list_huggingface_datasets(arguments: dict) -> list[TextContent]:
            """List datasets on the Hugging Face Hub with optional filters"""
            try:
                filter_str = arguments.get("filter")
                author = arguments.get("author")
                search = arguments.get("search")
                task_categories = arguments.get("task_categories")
                sort = arguments.get("sort")
                limit = arguments.get("limit", 10)
                
                result = await self.api_manager.huggingface_list_datasets(
                    filter_str=filter_str,
                    author=author,
                    search=search,
                    task_categories=task_categories,
                    sort=sort,
                    limit=limit
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                logger.error(f"Error listing HuggingFace datasets: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.call_tool()
        async def get_huggingface_dataset_info(arguments: dict) -> list[TextContent]:
            """Get detailed information about a specific HuggingFace dataset"""
            try:
                repo_id = arguments.get("repo_id")
                if not repo_id:
                    raise ValueError("repo_id is required")
                
                revision = arguments.get("revision")
                files_metadata = arguments.get("files_metadata", False)
                
                result = await self.api_manager.huggingface_dataset_info(
                    repo_id=repo_id,
                    revision=revision,
                    files_metadata=files_metadata
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                logger.error(f"Error getting HuggingFace dataset info: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.call_tool()
        async def huggingface_whoami(arguments: dict) -> list[TextContent]:
            """Get information about the current authenticated HuggingFace user"""
            try:
                result = await self.api_manager.huggingface_whoami()
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                logger.error(f"Error getting HuggingFace whoami info: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        # Repository Management Tools
        
        @self.server.call_tool()
        async def get_huggingface_repo_info(arguments: dict) -> list[TextContent]:
            """Get detailed information about a HuggingFace repository"""
            try:
                repo_id = arguments.get("repo_id")
                if not repo_id:
                    raise ValueError("repo_id is required")
                
                repo_type = arguments.get("repo_type", "model")
                revision = arguments.get("revision")
                files_metadata = arguments.get("files_metadata", False)
                
                result = await self.api_manager.huggingface_repo_info(
                    repo_id=repo_id,
                    repo_type=repo_type,
                    revision=revision,
                    files_metadata=files_metadata
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                logger.error(f"Error getting HuggingFace repo info: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.call_tool()
        async def list_huggingface_repo_files(arguments: dict) -> list[TextContent]:
            """List all files in a HuggingFace repository"""
            try:
                repo_id = arguments.get("repo_id")
                if not repo_id:
                    raise ValueError("repo_id is required")
                
                repo_type = arguments.get("repo_type", "model")
                revision = arguments.get("revision")
                
                result = await self.api_manager.huggingface_list_repo_files(
                    repo_id=repo_id,
                    repo_type=repo_type,
                    revision=revision
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                logger.error(f"Error listing HuggingFace repo files: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.call_tool()
        async def delete_huggingface_repo(arguments: dict) -> list[TextContent]:
            """Delete a HuggingFace repository (CAUTION: Irreversible!)"""
            try:
                repo_id = arguments.get("repo_id")
                if not repo_id:
                    raise ValueError("repo_id is required")
                
                repo_type = arguments.get("repo_type", "model")
                missing_ok = arguments.get("missing_ok", False)
                
                # Safety confirmation
                confirm = arguments.get("confirm_delete", False)
                if not confirm:
                    return [TextContent(
                        type="text",
                        text="SAFETY WARNING: This will permanently delete the repository. Set 'confirm_delete': true to proceed."
                    )]
                
                result = await self.api_manager.huggingface_delete_repo(
                    repo_id=repo_id,
                    repo_type=repo_type,
                    missing_ok=missing_ok
                )
                
                return [TextContent(
                    type="text",
                    text=f"Repository '{repo_id}' deleted permanently. This action cannot be undone."
                )]
            except Exception as e:
                logger.error(f"Error deleting HuggingFace repo: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.call_tool()
        async def check_huggingface_repo_exists(arguments: dict) -> list[TextContent]:
            """Check if a HuggingFace repository exists"""
            try:
                repo_id = arguments.get("repo_id")
                if not repo_id:
                    raise ValueError("repo_id is required")
                
                repo_type = arguments.get("repo_type", "model")
                
                result = await self.api_manager.huggingface_repo_exists(
                    repo_id=repo_id,
                    repo_type=repo_type
                )
                
                exists_text = "exists" if result['exists'] else "does not exist"
                return [TextContent(
                    type="text",
                    text=f"Repository {result['repo_id']} ({result['repo_type']}) {exists_text}"
                )]
            except Exception as e:
                logger.error(f"Error checking HuggingFace repo existence: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.call_tool()
        async def list_huggingface_repo_commits(arguments: dict) -> list[TextContent]:
            """List commits in a HuggingFace repository"""
            try:
                repo_id = arguments.get("repo_id")
                if not repo_id:
                    raise ValueError("repo_id is required")
                
                repo_type = arguments.get("repo_type", "model")
                revision = arguments.get("revision")
                formatted = arguments.get("formatted", False)
                
                result = await self.api_manager.huggingface_list_repo_commits(
                    repo_id=repo_id,
                    repo_type=repo_type,
                    revision=revision,
                    formatted=formatted
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                logger.error(f"Error listing HuggingFace repo commits: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.call_tool()
        async def huggingface_create_space(arguments: dict) -> list[TextContent]:
            """Create a new Hugging Face Space"""
            try:
                space_name = arguments.get("space_name")
                space_type = arguments.get("space_type", "gradio")
                config = arguments.get("config", {})
                
                result = await self.api_manager.huggingface_create_space(space_name, space_type, config)
                
                return [TextContent(
                    type="text",
                    text=f"Space '{space_name}' created successfully: {result['url']}"
                )]
            except Exception as e:
                logger.error(f"Error creating HuggingFace space: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.call_tool()
        async def huggingface_upload_model(arguments: dict) -> list[TextContent]:
            """Upload a model to Hugging Face"""
            try:
                model_name = arguments.get("model_name")
                model_path = arguments.get("model_path")
                config = arguments.get("config", {})
                
                result = await self.api_manager.huggingface_upload_model(model_name, model_path, config)
                
                return [TextContent(
                    type="text",
                    text=f"Model '{model_name}' uploaded successfully"
                )]
            except Exception as e:
                logger.error(f"Error uploading model to HuggingFace: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        # === GIT API TOOLS ===
        
        @self.server.call_tool()
        async def git_commit_and_push(arguments: dict) -> list[TextContent]:
            """Commit and push changes to Git repository"""
            try:
                repo_path = arguments.get("repo_path")
                commit_message = arguments.get("commit_message")
                branch = arguments.get("branch", "main")
                
                result = await self.api_manager.git_commit_and_push(repo_path, commit_message, branch)
                
                return [TextContent(
                    type="text",
                    text=f"Successfully committed and pushed: {result['commit_hash']}"
                )]
            except Exception as e:
                logger.error(f"Error with git operations: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.call_tool()
        async def github_create_repo(arguments: dict) -> list[TextContent]:
            """Create a new GitHub repository"""
            try:
                repo_name = arguments.get("repo_name")
                description = arguments.get("description", "")
                private = arguments.get("private", False)
                
                result = await self.api_manager.github_create_repo(repo_name, description, private)
                
                return [TextContent(
                    type="text",
                    text=f"Repository '{repo_name}' created: {result['html_url']}"
                )]
            except Exception as e:
                logger.error(f"Error creating GitHub repo: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        # === GOOGLE CLOUD API TOOLS ===
        
        @self.server.call_tool()
        async def google_sheets_operation(arguments: dict) -> list[TextContent]:
            """Perform operations on Google Sheets"""
            try:
                sheet_id = arguments.get("sheet_id")
                operation = arguments.get("operation")
                data = arguments.get("data", {})
                
                result = await self.api_manager.google_sheets_operation(sheet_id, operation, data)
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                logger.error(f"Error with Google Sheets operation: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.call_tool()
        async def google_drive_operation(arguments: dict) -> list[TextContent]:
            """Perform operations on Google Drive"""
            try:
                operation = arguments.get("operation")
                parameters = arguments.get("parameters", {})
                
                result = await self.api_manager.google_drive_operation(operation, parameters)
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                logger.error(f"Error with Google Drive operation: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        # === LOCAL FILE SYSTEM TOOLS ===
        
        @self.server.call_tool()
        async def write_file_local(arguments: dict) -> list[TextContent]:
            """Write content to a local file"""
            try:
                file_path = arguments.get("file_path")
                content = arguments.get("content")
                encoding = arguments.get("encoding", "utf-8")
                
                result = await self.file_ops.write_file(file_path, content, encoding)
                
                return [TextContent(
                    type="text",
                    text=f"File written successfully: {file_path}"
                )]
            except Exception as e:
                logger.error(f"Error writing file: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.call_tool()
        async def read_file_local(arguments: dict) -> list[TextContent]:
            """Read content from a local file"""
            try:
                file_path = arguments.get("file_path")
                encoding = arguments.get("encoding", "utf-8")
                
                content = await self.file_ops.read_file(file_path, encoding)
                
                return [TextContent(
                    type="text",
                    text=content
                )]
            except Exception as e:
                logger.error(f"Error reading file: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.call_tool()
        async def batch_file_operations(arguments: dict) -> list[TextContent]:
            """Perform batch operations on multiple files"""
            try:
                operations = arguments.get("operations", [])
                
                results = await self.file_ops.batch_operations(operations)
                
                return [TextContent(
                    type="text",
                    text=json.dumps(results, indent=2)
                )]
            except Exception as e:
                logger.error(f"Error with batch file operations: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        # === AUTHENTICATION AND CONFIGURATION ===
        
        @self.server.call_tool()
        async def manage_credentials(arguments: dict) -> list[TextContent]:
            """Manage API credentials securely"""
            try:
                action = arguments.get("action")  # set, get, delete, list
                service = arguments.get("service")
                credentials = arguments.get("credentials", {})
                
                result = await self.auth_manager.manage_credentials(action, service, credentials)
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                logger.error(f"Error managing credentials: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.call_tool()
        async def get_server_status(arguments: dict) -> list[TextContent]:
            """Get comprehensive server status and health"""
            try:
                status = {
                    "server": "Advanced MCP Server",
                    "status": "healthy",
                    "uptime": datetime.now().isoformat(),
                    "components": {
                        "api_manager": await self.api_manager.health_check(),
                        "rules_engine": await self.rules_engine.health_check(),
                        "session_manager": await self.session_manager.health_check(),
                        "file_operations": await self.file_ops.health_check(),
                        "auth_manager": await self.auth_manager.health_check()
                    },
                    "active_sessions": await self.session_manager.get_active_sessions_count(),
                    "api_connections": await self.api_manager.get_connection_status()
                }
                
                return [TextContent(
                    type="text",
                    text=json.dumps(status, indent=2)
                )]
            except Exception as e:
                logger.error(f"Error getting server status: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    def _register_resources(self):
        """Register available resources"""
        
        @self.server.list_resources()
        async def list_resources() -> list[Resource]:
            """List all available resources"""
            return [
                Resource(
                    uri="advanced-mcp://config",
                    name="Server Configuration",
                    description="Current server configuration and settings",
                    mimeType="application/json"
                ),
                Resource(
                    uri="advanced-mcp://logs",
                    name="Server Logs",
                    description="Recent server logs and activity",
                    mimeType="text/plain"
                ),
                Resource(
                    uri="advanced-mcp://sessions",
                    name="Active Sessions",
                    description="Information about active sessions",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read a specific resource"""
            if uri == "advanced-mcp://config":
                config = await self._get_server_config()
                return json.dumps(config, indent=2)
            elif uri == "advanced-mcp://logs":
                return await self._get_recent_logs()
            elif uri == "advanced-mcp://sessions":
                sessions = await self.session_manager.get_all_sessions()
                return json.dumps(sessions, indent=2)
            else:
                raise ValueError(f"Unknown resource: {uri}")
    
    async def _get_server_config(self) -> dict:
        """Get current server configuration"""
        return {
            "server_name": "Advanced MCP Server",
            "version": "1.0.0",
            "capabilities": [
                "session_management",
                "api_integrations",
                "file_operations",
                "authentication",
                "rules_engine"
            ],
            "supported_apis": [
                "claude",
                "openai",
                "huggingface",
                "github",
                "google_cloud",
                "google_drive",
                "google_sheets"
            ]
        }
    
    async def _get_recent_logs(self) -> str:
        """Get recent log entries"""
        try:
            with open("advanced_mcp.log", "r") as f:
                lines = f.readlines()
                return "".join(lines[-50:])  # Last 50 lines
        except FileNotFoundError:
            return "No log file found"
    
    async def run(self):
        """Run the MCP server"""
        logger.info("Starting Advanced MCP Server...")
        
        # Initialize all components
        await self.api_manager.initialize()
        await self.rules_engine.initialize()
        await self.session_manager.initialize()
        await self.file_ops.initialize()
        await self.auth_manager.initialize()
        
        logger.info("All components initialized successfully")
        
        # Start the server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="advanced-mcp-server",
                    server_version="1.0.0",
                    capabilities={
                        "tools": {},
                        "resources": {},
                        "logging": {}
                    }
                )
            )

async def main():
    """Main entry point"""
    server = AdvancedMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
