@echo off
echo Starting Advanced MCP Server...
cd /d "G:\projects\advanced-mcp-server"
"C:\Users\j\AppData\Local\Programs\Python\Launcher\py.exe" main.py > mcp_server_startup.log 2>&1
echo MCP Server started. Check mcp_server_startup.log for details.
