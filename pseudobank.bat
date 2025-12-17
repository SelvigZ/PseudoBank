@echo off
REM ============================================================================
REM  PseudoBank Launcher
REM  This batch file runs the PseudoBank data sanitization tool.
REM
REM  Usage: pseudobank.bat "path\to\your\file.xlsx"
REM     Or: pseudobank.bat (will prompt for file path)
REM ============================================================================

setlocal enabledelayedexpansion

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in your PATH.
    echo.
    echo Please install Python 3.x or contact IT for assistance.
    echo.
    pause
    exit /b 1
)

REM Check if dependencies are installed by trying to import pandas
python -c "import pandas" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Dependencies not found. Installing required packages...
    echo.
    pip install -r "%SCRIPT_DIR%requirements.txt"
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies.
        echo Try running: pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
    echo.
    echo Dependencies installed successfully.
    echo.
)

REM Check if a file argument was provided
if "%~1"=="" (
    echo.
    echo ============================================
    echo   PseudoBank - Data Sanitization Tool
    echo ============================================
    echo.
    set /p "INPUT_FILE=Enter the path to your file: "
) else (
    set "INPUT_FILE=%~1"
)

REM Run the Python script
echo.
python "%SCRIPT_DIR%src\pseudonymize.py" --input "%INPUT_FILE%"

echo.
pause
