@echo off
cd /d "G:\projects\advanced-mcp-server"
python.exe test_production_fixes.py > production_validation_result.txt 2>&1
echo Python test exit code: %ERRORLEVEL% >> production_validation_result.txt
exit /b 0
