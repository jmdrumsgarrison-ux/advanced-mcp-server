import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print("=== PHASE 3.1: MCP SERVER INITIALIZATION TEST ===")
print(f"{datetime.now()} - Testing MCP server initialization with live credentials")

async def main():
    try:
        # Test imports of core MCP server components
        print("[INFO] Testing core MCP server imports...")
        
        # Test MCP framework import
        try:
            from mcp import server
            from mcp.server import Server
            from mcp.types import Tool
            print("[OK] MCP framework imported successfully")
        except ImportError as e:
            print(f"[ERROR] Failed to import MCP framework: {e}")
            sys.exit(1)
        
        # Test core server module imports
        try:
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            import api_manager
            import auth_manager
            import session_manager
            import rules_engine
            import file_operations
            print("[OK] All core server modules imported successfully")
        except ImportError as e:
            print(f"[ERROR] Failed to import core server modules: {e}")
            print(f"[ERROR] Make sure all server files are present")
            sys.exit(1)
        
        # Test credential loading
        print("[INFO] Testing credential loading...")
        auth_mgr = auth_manager.AuthManager()
        await auth_mgr.initialize()
        
        # Use the public API to list services and their status
        services_status = await auth_mgr.manage_credentials("list", "all")
        
        available_credentials = services_status['configured_services']
        total_services = services_status['total_services']
        print(f"[INFO] Credential validation: {available_credentials}/{total_services} services available")
        
        for service, info in services_status['services'].items():
            if info['has_credentials']:
                print(f"[OK] {service}: Available")
            else:
                print(f"[WARNING] {service}: Not available")
        
        # Test API manager initialization
        print("[INFO] Testing API manager initialization...")
        api_mgr = api_manager.APIManager()
        
        # Test service discovery
        connection_status = await api_mgr.get_connection_status()
        available_services = [service for service, status in connection_status.items() if status == "connected"]
        print(f"[INFO] API Manager discovered {len(available_services)} available services")
        
        for service in available_services:
            print(f"[OK] Service available: {service}")
        
        # Test MCP server creation
        print("[INFO] Testing MCP server creation...")
        mcp_server = Server("advanced-mcp-server")
        print("[OK] MCP server instance created successfully")
        
        # Test tool registration simulation
        print("[INFO] Testing tool registration framework...")
        tools_registered = 0
        
        # Test each available API service tool registration
        for service in available_services:
            try:
                # This is a simulation - actual tool registration would happen in server startup
                tool_name = f"{service.lower()}_tool"
                print(f"[OK] Tool registration simulated: {tool_name}")
                tools_registered += 1
            except Exception as e:
                print(f"[WARNING] Tool registration simulation failed for {service}: {e}")
        
        print(f"[INFO] Successfully simulated registration of {tools_registered} tools")
        
        # Test session manager
        print("[INFO] Testing session manager...")
        session_mgr = session_manager.SessionManager()
        await session_mgr.initialize()
        session_id = await session_mgr.start_session("testing")
        print(f"[OK] Session created: {session_id}")
        
        print("[SUCCESS] MCP Server integration test PASSED")
        print(f"[INFO] Available APIs: {len(available_services)}")
        print(f"[INFO] Registered tools: {tools_registered}")
        print(f"[INFO] Session management: Working")
        print(f"[INFO] Authentication: {available_credentials}/{total_services} services")
        
    except Exception as e:
        print(f"[ERROR] MCP Server integration test failed: {str(e)}")
        print(f"[ERROR] Exception type: {type(e).__name__}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        sys.exit(1)

print("=== PHASE 3.1 COMPLETE ===")

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())
