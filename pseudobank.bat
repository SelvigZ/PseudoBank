@echo off
REM ============================================================================
REM  PseudoBank Launcher
REM  This batch file runs the PseudoBank data sanitization tool.
REM
REM  Usage: pseudobank.bat "path\to\your\file.xlsx"
REM     Or: pseudobank.bat (will prompt for file path)
REM
REM  No pip install needed - dependencies are bundled in the lib folder.
REM  Uses conda's numpy if available (do NOT bundle numpy separately).
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
    echo Please ensure Python 3.x is installed.
    echo.
    pause
    exit /b 1
)

REM Check if a file argument was provided
if "%~1"=="" (
    echo.
    echo ============================================
    echo   PseudoBank - Data Sanitization Tool
    echo ============================================
    echo.
    echo   No pip install needed - just run this!
    echo.
    echo   IMPORTANT: Do NOT type quotes around the path.
    echo   Just paste or type the path directly.
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
