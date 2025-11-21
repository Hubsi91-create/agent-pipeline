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

REM Check if virtual environment exists
if not exist "venv\" (
    echo [SETUP] Virtual environment not found. Creating...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        echo [INFO] Please ensure Python 3.8+ is installed and in PATH.
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created.
    echo.
)

REM Activate virtual environment
echo [INIT] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

REM Check if dependencies are installed
echo [CHECK] Verifying dependencies...
python -c "import customtkinter" 2>nul
if errorlevel 1 (
    echo [SETUP] Installing dependencies...
    pip install -r backend\requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
    echo [SUCCESS] Dependencies installed.
    echo.
)

REM Check environment variables
echo [CHECK] Verifying environment configuration...
if not defined GEMINI_API_KEY (
    echo [WARNING] GEMINI_API_KEY not set in environment.
    echo [INFO] AI features may be limited.
    echo.
)

if not defined GOOGLE_SHEET_ID (
    echo [WARNING] GOOGLE_SHEET_ID not set in environment.
    echo [INFO] Data persistence will use in-memory storage.
    echo.
)

REM Check Google Cloud authentication
echo [CHECK] Checking Google Cloud authentication...
gcloud auth application-default print-access-token >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Google Cloud Application Default Credentials not configured.
    echo [INFO] Run 'gcloud auth application-default login' to enable Google Sheets access.
    echo [INFO] You can also set GOOGLE_APPLICATION_CREDENTIALS to a service account key file.
    echo.
) else (
    echo [SUCCESS] Google Cloud ADC configured.
    echo.
)

REM Launch desktop app
echo ================================
echo   LAUNCHING PROJECT PHOENIX
echo ================================
echo.
echo [START] Starting desktop application...
echo.

python backend\desktop_app.py

REM Check exit code
if errorlevel 1 (
    echo.
    echo [ERROR] Application exited with error code %errorlevel%
    echo [INFO] Check logs for details.
    pause
    exit /b %errorlevel%
)

echo.
echo [EXIT] Application closed successfully.
pause
