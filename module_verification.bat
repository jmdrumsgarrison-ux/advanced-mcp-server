@echo off
cd /d "G:\projects\advanced-mcp-server"
echo === COMPREHENSIVE MODULE TEST === > module_verification.txt
echo %date% %time% - Module verification initiated >> module_verification.txt

echo Testing core Python modules... >> module_verification.txt
"C:\Users\j\AppData\Local\Programs\Python\Python312\python.exe" -c "
import sys
print('Python version:', sys.version)
print('Python executable:', sys.executable)

modules_test = {
    'mcp': 'MCP Framework',
    'aiohttp': 'Async HTTP Client',
    'aiofiles': 'Async File Operations',
    'openai': 'OpenAI API Client',
    'requests': 'HTTP Requests Library',
    'cryptography': 'Cryptography Library',
    'json': 'JSON Processing',
    'asyncio': 'Async I/O Support',
    'logging': 'Logging Framework'
}

success_count = 0
total_count = len(modules_test)

for module, description in modules_test.items():
    try:
        imported = __import__(module)
        version = getattr(imported, '__version__', 'No version info')
        print(f'SUCCESS: {module} ({description}) - Version: {version}')
        success_count += 1
    except Exception as e:
        print(f'ERROR: {module} ({description}) - {str(e)}')

print(f'Module test results: {success_count}/{total_count} modules imported successfully')
print('Overall status:', 'PASS' if success_count == total_count else 'PARTIAL')
" >> module_verification.txt 2>&1
echo Module verification exit code: %ERRORLEVEL% >> module_verification.txt

echo === MODULE TEST COMPLETE === >> module_verification.txt
exit /b 0
