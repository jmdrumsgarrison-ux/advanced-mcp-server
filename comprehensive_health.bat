@echo off
cd /d "G:\projects\advanced-mcp-server"
echo === COMPREHENSIVE SERVER HEALTH CHECK === > comprehensive_health.txt
echo %date% %time% - Comprehensive health check started >> comprehensive_health.txt

echo STEP 1: Testing core dependencies... >> comprehensive_health.txt
"C:\Users\j\AppData\Local\Programs\Python\Python312\python.exe" -c "
print('=== CORE DEPENDENCIES TEST ===')
core_modules = ['asyncio', 'json', 'logging', 'os', 'sys', 'datetime', 'pathlib']
success = 0
for module in core_modules:
    try:
        __import__(module)
        print(f'PASS: {module}')
        success += 1
    except Exception as e:
        print(f'FAIL: {module} - {str(e)}')
print(f'Core modules: {success}/{len(core_modules)} working')
" >> comprehensive_health.txt 2>&1

echo STEP 2: Testing external dependencies... >> comprehensive_health.txt
"C:\Users\j\AppData\Local\Programs\Python\Python312\python.exe" -c "
print('=== EXTERNAL DEPENDENCIES TEST ===')
ext_modules = ['mcp', 'aiohttp', 'openai', 'requests']
success = 0
for module in ext_modules:
    try:
        __import__(module)
        print(f'PASS: {module}')
        success += 1
    except Exception as e:
        print(f'FAIL: {module} - {str(e)}')
print(f'External modules: {success}/{len(ext_modules)} working')
" >> comprehensive_health.txt 2>&1

echo STEP 3: Testing environment configuration... >> comprehensive_health.txt
"C:\Users\j\AppData\Local\Programs\Python\Python312\python.exe" -c "
print('=== ENVIRONMENT CONFIGURATION TEST ===')
import os
key_files = ['.env', 'config.json', 'main.py', 'api_manager.py', 'auth_manager.py']
for file in key_files:
    if os.path.exists(file):
        size = os.path.getsize(file)
        print(f'PASS: {file} ({size} bytes)')
    else:
        print(f'FAIL: {file} missing')

# Test environment variables
env_vars = ['ANTHROPIC_API_KEY', 'OPENAI_API_KEY', 'HUGGINGFACE_TOKEN', 'GITHUB_TOKEN']
configured = 0
for var in env_vars:
    value = os.getenv(var)
    if value and len(value) > 10:
        print(f'PASS: {var} configured ({len(value)} chars)')
        configured += 1
    else:
        print(f'FAIL: {var} not configured')
print(f'API keys: {configured}/{len(env_vars)} configured')
" >> comprehensive_health.txt 2>&1

echo === COMPREHENSIVE HEALTH CHECK COMPLETE === >> comprehensive_health.txt
exit /b 0
