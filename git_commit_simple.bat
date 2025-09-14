@echo off
cd /d "G:\projects\advanced-mcp-server"
git commit -m "Advanced MCP Server v1.1 - Modern Content Acquisition Complete - Fixed Crawl4AI API compatibility - Integrated 6 modern tools - 100% integration test pass" > git_commit_simple.txt 2>&1
echo Git commit exit code: %ERRORLEVEL% >> git_commit_simple.txt
exit /b 0