@echo off
REM Advanced MCP Server - Windows Installation Script
REM This script automates the installation and setup process

echo.
echo =========================================
echo  Advanced MCP Server Installation
echo =========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✅ Python is installed
python --version

REM Check if pip is available
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip is not available
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo ✅ pip is available

REM Install required packages
echo.
echo Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    echo Please check the error messages above
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully

REM Create necessary directories
echo.
echo Creating necessary directories...
if not exist "backups" mkdir backups
if not exist "sessions" mkdir sessions
if not exist "logs" mkdir logs

echo ✅ Directories created

REM Copy environment template if .env doesn't exist
if not exist ".env" (
    echo.
    echo Creating environment configuration file...
    copy ".env.example" ".env"
    echo ✅ Created .env file from template
    echo.
    echo IMPORTANT: Please edit .env file and add your API keys:
    echo - ANTHROPIC_API_KEY=your_anthropic_key
    echo - OPENAI_API_KEY=your_openai_key  
    echo - HUGGINGFACE_TOKEN=your_hf_token
    echo - GITHUB_TOKEN=your_github_token
    echo.
) else (
    echo ✅ .env file already exists
)

REM Test the installation
echo.
echo Testing installation...
python -c "import json; print('✅ JSON module available')"
python -c "import asyncio; print('✅ Asyncio module available')"
python -c "import logging; print('✅ Logging module available')"

REM Try to import our custom modules
echo.
echo Testing custom modules...
python -c "import sys; sys.path.append('.'); from api_manager import APIManager; print('✅ API Manager imported')" 2>nul
if %errorlevel% neq 0 echo ⚠️  API Manager import failed - check MCP dependencies

python -c "import sys; sys.path.append('.'); from rules_engine import RulesEngine; print('✅ Rules Engine imported')" 2>nul
if %errorlevel% neq 0 echo ⚠️  Rules Engine import failed - check MCP dependencies

python -c "import sys; sys.path.append('.'); from session_manager import SessionManager; print('✅ Session Manager imported')" 2>nul
if %errorlevel% neq 0 echo ⚠️  Session Manager import failed - check MCP dependencies

REM Display next steps
echo.
echo =========================================
echo  Installation Complete!
echo =========================================
echo.
echo Next steps:
echo 1. Edit .env file with your API keys
echo 2. Configure Claude Desktop (see README.md)
echo 3. Test the server: python main.py
echo.
echo For Claude Desktop integration, add this to your config:
echo {
echo   "mcpServers": {
echo     "advanced-mcp-server": {
echo       "command": "python",
echo       "args": ["%CD%\main.py"]
echo     }
echo   }
echo }
echo.
echo Configuration file location:
echo Windows: %%APPDATA%%\Claude\claude_desktop_config.json
echo.
echo For detailed instructions, see README.md
echo.

pause
