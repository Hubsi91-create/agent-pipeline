@echo off
REM ================================================
REM PROJECT PHOENIX - ONE-CLICK DESKTOP LAUNCHER
REM ================================================

echo.
echo ================================
echo   PROJECT PHOENIX LAUNCHER
echo   Native Desktop Edition
echo ================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Define log file
set LOGFILE=startup_log.txt
echo [START] Launcher started at %DATE% %TIME% > %LOGFILE%

REM Check if virtual environment exists
if not exist "venv\" (
    echo [SETUP] Virtual environment not found. Creating...
    echo [SETUP] Virtual environment not found. Creating... >> %LOGFILE%
    python -m venv venv >> %LOGFILE% 2>&1
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        echo [ERROR] Failed to create virtual environment. >> %LOGFILE%
        echo [INFO] Please ensure Python 3.8+ is installed and in PATH.
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created.
    echo [SUCCESS] Virtual environment created. >> %LOGFILE%
    echo.
)

REM Check if dependencies are installed
echo [CHECK] Verifying dependencies...
echo [CHECK] Verifying dependencies... >> %LOGFILE%
venv\Scripts\python -c "import customtkinter" >> %LOGFILE% 2>&1
if errorlevel 1 (
    echo [SETUP] Installing dependencies...
    echo [SETUP] Installing dependencies... >> %LOGFILE%
    venv\Scripts\pip install -r backend\requirements.txt >> %LOGFILE% 2>&1
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies.
        echo [ERROR] Failed to install dependencies. >> %LOGFILE%
        type %LOGFILE%
        pause
        exit /b 1
    )
    echo [SUCCESS] Dependencies installed.
    echo [SUCCESS] Dependencies installed. >> %LOGFILE%
    echo.
)

REM Launch desktop app using explicit python path
echo ================================
echo   LAUNCHING PROJECT PHOENIX
echo ================================
echo.
echo [START] Starting desktop application...
echo [START] Starting desktop application... >> %LOGFILE%
echo.

venv\Scripts\python backend\desktop_app.py >> %LOGFILE% 2>&1

REM Check exit code
if errorlevel 1 (
    echo.
    echo [ERROR] Application exited with error code %errorlevel%
    echo [ERROR] Application exited with error code %errorlevel% >> %LOGFILE%
    echo [INFO] Check %LOGFILE% for details.
    type %LOGFILE%
    pause
    exit /b %errorlevel%
)

echo.
echo [EXIT] Application closed successfully.
echo [EXIT] Application closed successfully. >> %LOGFILE%
pause
