@echo off
REM VANIE - Virtual Assistant of Neural Integrated Engine
REM Startup Script for Windows

echo.
echo ============================================================
echo    VANIE - Virtual Assistant of Neural Integrated Engine
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.7+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Checking Python installation...
python --version
echo.

echo [2/4] Installing required packages...
echo.
pip install flask==2.3.3 flask-cors==4.0.0 psutil==5.9.5 requests==2.31.0 -q

if %errorlevel% neq 0 (
    echo ERROR: Failed to install required packages!
    echo Run this command manually to see the error:
    echo pip install flask==2.3.3 flask-cors==4.0.0 psutil==5.9.5 requests==2.31.0
    pause
    exit /b 1
)

echo [✓] All packages installed successfully!
echo.

echo [3/4] Starting VANIE Backend Server...
echo.
echo ============================================================
echo VANIE is starting...
echo Open your browser and go to: http://localhost:5000
echo ============================================================
echo.

REM Start the Flask server
python VANIE_FIXED.py

if %errorlevel% neq 0 (
    echo ERROR: Failed to start VANIE!
    echo Make sure VANIE_FIXED.py exists in the current directory.
    pause
    exit /b 1
)

pause
