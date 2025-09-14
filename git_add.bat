@echo off
cd /d "G:\projects\advanced-mcp-server"
echo === Git Add Operation === > git_add_result.txt 2>&1
"C:\Program Files\Git\bin\git.exe" add . >> git_add_result.txt 2>&1
echo Git add exit code: %ERRORLEVEL% >> git_add_result.txt
exit /b 0
