@echo off
title VANIE AI Backend Server
color 0A
echo.
echo ========================================
echo    VANIE AI Backend Server Startup
echo ========================================
echo.

echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
) else (
    echo ✓ Python is installed
)

echo.
echo [2/4] Installing required packages...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Installing Flask...
    pip install flask
) else (
    echo ✓ Flask is already installed
)

pip show flask-cors >nul 2>&1
if errorlevel 1 (
    echo Installing Flask-CORS...
    pip install flask-cors
) else (
    echo ✓ Flask-CORS is already installed
)

echo.
echo [3/4] Checking if port 5000 is available...
netstat -an | findstr ":5000" >nul 2>&1
if not errorlevel 1 (
    echo WARNING: Port 5000 is already in use!
    echo Trying to stop any existing process...
    taskkill /f /im python.exe >nul 2>&1
    timeout /t 2 >nul
)

echo.
echo [4/4] Starting VANIE AI Backend Server...
echo.
echo Server will start at: http://localhost:5000
echo API Endpoint: http://localhost:5000/api/chat
echo Health Check: http://localhost:5000/health
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python VANIE.py

if errorlevel 1 (
    echo.
    echo ERROR: Server failed to start!
    echo.
    echo Troubleshooting steps:
    echo 1. Make sure Python is installed correctly
    echo 2. Check if all required packages are installed
    echo 3. Verify VANIE.py file is not corrupted
    echo 4. Try running: python -m flask run --host=0.0.0.0 --port=5000
    echo.
)

pause
