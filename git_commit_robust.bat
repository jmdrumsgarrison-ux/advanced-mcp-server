@echo off
cd /d "G:\projects\advanced-mcp-server"
echo Trying git commit... > git_commit_result.txt
if exist "C:\Program Files\Git\bin\git.exe" (
    echo Using C:\Program Files\Git\bin\git.exe >> git_commit_result.txt
    "C:\Program Files\Git\bin\git.exe" commit -m "Advanced MCP Server v1.1 - Modern Content Acquisition Complete" >> git_commit_result.txt 2>&1
) else if exist "C:\Program Files (x86)\Git\bin\git.exe" (
    echo Using C:\Program Files (x86)\Git\bin\git.exe >> git_commit_result.txt
    "C:\Program Files (x86)\Git\bin\git.exe" commit -m "Advanced MCP Server v1.1 - Modern Content Acquisition Complete" >> git_commit_result.txt 2>&1
) else if exist "C:\Git\bin\git.exe" (
    echo Using C:\Git\bin\git.exe >> git_commit_result.txt
    "C:\Git\bin\git.exe" commit -m "Advanced MCP Server v1.1 - Modern Content Acquisition Complete" >> git_commit_result.txt 2>&1
) else (
    echo Git executable not found in common locations >> git_commit_result.txt
    echo Trying git from PATH >> git_commit_result.txt
    git commit -m "Advanced MCP Server v1.1 - Modern Content Acquisition Complete" >> git_commit_result.txt 2>&1
)
echo Git commit exit code: %ERRORLEVEL% >> git_commit_result.txt
exit /b 0