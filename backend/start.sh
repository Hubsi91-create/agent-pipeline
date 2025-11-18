#!/bin/bash

# Music Video Agent System - Robust Dual Service Startup Script
# Prevents race conditions with active health checking

set -e

echo "🚀 Starting Music Video Agent System..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ================================
# 1. START FASTAPI BACKEND (Port 8000) - IN BACKGROUND
# ================================
echo "📡 Starting FastAPI backend on port 8000..."
cd /app
uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info &

# Store the PID of uvicorn
UVICORN_PID=$!
echo "✅ FastAPI started (PID: $UVICORN_PID)"

# ================================
# 2. WAIT FOR BACKEND TO BE READY (Health Check)
# ================================
echo "⏳ Waiting for Backend to be ready..."
BACKEND_READY=false

for i in {1..30}; do
    if curl -s http://127.0.0.1:8000/docs > /dev/null 2>&1; then
        echo "✅ Backend is UP and responding!"
        BACKEND_READY=true
        break
    fi
    echo "Waiting for backend... ($i/30)"
    sleep 1
done

if [ "$BACKEND_READY" = false ]; then
    echo "❌ ERROR: Backend failed to start within 30 seconds"
    kill $UVICORN_PID 2>/dev/null || true
    exit 1
fi

# ================================
# 3. START STREAMLIT FRONTEND (Cloud Run Port) - IN FOREGROUND
# ================================
# Use Cloud Run's $PORT variable or fallback to 8080
FRONTEND_PORT=${PORT:-8080}

echo "🎬 Starting Streamlit frontend on port $FRONTEND_PORT..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Streamlit configuration for Cloud Run
export STREAMLIT_SERVER_PORT=$FRONTEND_PORT
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export STREAMLIT_SERVER_ENABLE_CORS=true
export STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

# Start Streamlit in foreground (keeps container alive)
streamlit run app.py \
    --server.port=$FRONTEND_PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false \
    --server.enableCORS=true \
    --server.enableXsrfProtection=false

# If Streamlit exits, kill uvicorn too
echo "⚠️ Streamlit stopped, shutting down..."
kill $UVICORN_PID 2>/dev/null || true
