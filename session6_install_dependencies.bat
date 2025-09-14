@echo off
echo Starting Session 6 Phase 2 Dependency Installation...
cd /d "G:\projects\advanced-mcp-server"

echo Installing dependencies from requirements.txt...
python.exe -m pip install -r requirements.txt --upgrade > session6_dependency_install_result.txt 2>&1
echo Dependency install exit code: %ERRORLEVEL% >> session6_dependency_install_result.txt

echo Verifying key dependencies...
python.exe -c "import mcp; print('MCP: OK')" >> session6_dependency_install_result.txt 2>&1
python.exe -c "import aiohttp; print('aiohttp: OK')" >> session6_dependency_install_result.txt 2>&1
python.exe -c "import aiofiles; print('aiofiles: OK')" >> session6_dependency_install_result.txt 2>&1
python.exe -c "import openai; print('openai: OK')" >> session6_dependency_install_result.txt 2>&1
python.exe -c "import huggingface_hub; print('huggingface_hub: OK')" >> session6_dependency_install_result.txt 2>&1
python.exe -c "from dotenv import load_dotenv; print('python-dotenv: OK')" >> session6_dependency_install_result.txt 2>&1

echo Session 6 dependency installation complete >> session6_dependency_install_result.txt
echo Timestamp: %DATE% %TIME% >> session6_dependency_install_result.txt
exit /b 0
