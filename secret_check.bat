@echo off
cd /d "G:\projects\advanced-mcp-server"
echo === Checking for Secrets === > secret_check_result.txt 2>&1
echo Checking main.py for secrets... >> secret_check_result.txt 2>&1
findstr /i "api_key token password secret" main.py >> secret_check_result.txt 2>&1
echo. >> secret_check_result.txt 2>&1
echo Checking chat_manager.py for secrets... >> secret_check_result.txt 2>&1
findstr /i "api_key token password secret" chat_manager.py >> secret_check_result.txt 2>&1
echo. >> secret_check_result.txt 2>&1
echo Checking api_manager.py for secrets... >> secret_check_result.txt 2>&1
findstr /i "api_key token password secret" api_manager.py >> secret_check_result.txt 2>&1
echo Secret check complete >> secret_check_result.txt 2>&1
exit /b 0
