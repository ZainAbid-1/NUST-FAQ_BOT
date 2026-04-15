@echo off
echo ==============================================
echo   NUST FAQ Bot - Phase 1: Environment Setup
echo ==============================================

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ from python.org
    pause
    exit /b 1
)

:: Create Virtual Environment
if not exist venv (
    echo Creating Virtual Environment (venv)...
    python -m venv venv
) else (
    echo Virtual Environment already exists. Skipping creation...
)

:: Activate and install dependencies
echo Installing/Updating requirements...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ==============================================
echo   SETUP COMPLETE! 
echo   You can now run the bot using run.bat
echo ==============================================
pause
