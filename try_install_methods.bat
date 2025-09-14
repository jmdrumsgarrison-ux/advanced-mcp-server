@echo off
echo ===== ALTERNATIVE INSTALLATION METHODS =====
echo Testing different ways to install anthropic library
echo Timestamp: %date% %time%
echo.

cd /d "G:\projects\advanced-mcp-server"

echo [INFO] Method 1: Try ensurepip to bootstrap pip...
python.exe -m ensurepip --upgrade > install_methods_test.txt 2>&1
echo Ensurepip exit code: %ERRORLEVEL% >> install_methods_test.txt

echo [INFO] Method 2: Try installing anthropic with python -m pip...
python.exe -m pip install anthropic >> install_methods_test.txt 2>&1
echo Python -m pip install exit code: %ERRORLEVEL% >> install_methods_test.txt

echo [INFO] Method 3: Check if pip is now available...
python.exe -m pip --version >> install_methods_test.txt 2>&1
echo Pip version check exit code: %ERRORLEVEL% >> install_methods_test.txt

echo [INFO] Method 4: Try direct installation with easy_install...
python.exe -m easy_install anthropic >> install_methods_test.txt 2>&1
echo Easy_install exit code: %ERRORLEVEL% >> install_methods_test.txt

echo.
echo ===== INSTALLATION METHODS TEST COMPLETE =====
echo Results in install_methods_test.txt

exit /b 0
