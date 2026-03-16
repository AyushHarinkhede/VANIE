@echo off
title VANIE Backend Server
echo.
echo ========================================
echo    VANIE - Virtual Assistant Backend
echo ========================================
echo.
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

echo Python found! Checking dependencies...
echo.

REM Check if virtual environment exists and create if not
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo Starting VANIE Backend Server...
echo ========================================
echo.
echo Server will start at: http://127.0.0.1:5000
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python VANIE.py

echo.
echo Server stopped.
pause
