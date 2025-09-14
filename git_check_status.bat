@echo off
cd /d "G:\projects\advanced-mcp-server"
echo === Git Status Check === > git_status_result.txt 2>&1
"C:\Program Files\Git\bin\git.exe" status >> git_status_result.txt 2>&1
echo. >> git_status_result.txt 2>&1
echo === Recent Changes === >> git_status_result.txt 2>&1
"C:\Program Files\Git\bin\git.exe" log --oneline -3 >> git_status_result.txt 2>&1
echo Git status exit code: %ERRORLEVEL% >> git_status_result.txt
exit /b 0
