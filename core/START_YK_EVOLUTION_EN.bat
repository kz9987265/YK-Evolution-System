@echo off
title YK Evolution System

echo.
echo ======================================
echo    YK Evolution System - Quick Start
echo ======================================
echo.

:: Check if .env.local exists
if not exist ".env.local" (
    echo WARNING: .env.local not found
    echo.
    echo Creating config template...
    (
        echo # YK Evolution System Configuration
        echo GEMINI_API_KEY=your_gemini_api_key_here
        echo.
        echo # Optional Settings
        echo # LOCAL_LLM_MODEL_PATH=
        echo # ENABLE_DEBUG=false
    ) > .env.local
    echo.
    echo Created .env.local template
    echo Please edit .env.local and add your Gemini API Key
    echo Get it from: https://aistudio.google.com/apikey
    echo.
    pause
    notepad .env.local
)

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

:: Install dependencies
echo.
echo Installing dependencies...
pip install -q google-generativeai python-dotenv transformers torch numpy
if errorlevel 1 (
    echo WARNING: Some packages may have failed to install
    echo The system will try to continue...
)

:: Create necessary folders
echo.
echo Creating folder structure...
if not exist "evolution_history" mkdir evolution_history
if not exist "memories" mkdir memories
if not exist "test_results" mkdir test_results

:: Display info
echo.
echo ======================================
echo    System Information
echo ======================================
python --version
echo Working Directory: %CD%
echo.

:: Start the system
echo ======================================
echo    Starting YK Evolution System
echo ======================================
echo.
echo Press Ctrl+C to stop the system
echo.

python main.py

:: Error handling
if errorlevel 1 (
    echo.
    echo ======================================
    echo ERROR: System execution failed
    echo ======================================
    echo.
    echo Please check:
    echo 1. GEMINI_API_KEY is set correctly in .env.local
    echo 2. All dependencies are installed
    echo 3. Python 3.8+ is installed
    echo.
)

pause
