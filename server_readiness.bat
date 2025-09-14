@echo off
cd /d "G:\projects\advanced-mcp-server"
echo === BASIC SERVER READINESS === > server_readiness.txt
echo %date% %time% - Server readiness check >> server_readiness.txt

echo Testing basic server import... >> server_readiness.txt
"C:\Users\j\AppData\Local\Programs\Python\Python312\python.exe" -c "
try:
    import main
    print('SUCCESS: main module imported')
except Exception as e:
    print('ERROR: main import failed -', str(e))
" >> server_readiness.txt 2>&1

echo Testing API manager... >> server_readiness.txt
"C:\Users\j\AppData\Local\Programs\Python\Python312\python.exe" -c "
try:
    import api_manager
    print('SUCCESS: api_manager imported')
except Exception as e:
    print('ERROR: api_manager failed -', str(e))
" >> server_readiness.txt 2>&1

echo Testing auth manager... >> server_readiness.txt
"C:\Users\j\AppData\Local\Programs\Python\Python312\python.exe" -c "
try:
    import auth_manager
    print('SUCCESS: auth_manager imported')
except Exception as e:
    print('ERROR: auth_manager failed -', str(e))
" >> server_readiness.txt 2>&1

echo === READINESS CHECK COMPLETE === >> server_readiness.txt
exit /b 0
