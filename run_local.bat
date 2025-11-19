@echo off
echo 🚀 Starting Music Video Agent System...

cd backend

REM Check if .env exists, if not copy from example
if not exist .env (
    echo Creating .env file from example...
    copy .env.example .env
    echo ⚠️  PLEASE EDIT backend/.env WITH YOUR API KEYS!
)

echo Starting Backend (FastAPI) in a new window...
start "FastAPI Backend" cmd /k "uvicorn app.main:app --reload --port 8000"

echo Waiting for backend to initialize...
timeout /t 5

echo Starting Frontend (Streamlit)...
streamlit run app.py
