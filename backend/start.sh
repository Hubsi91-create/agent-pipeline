#!/bin/bash

# Music Video Agent System - Dual Service Startup Script
# Starts both FastAPI (backend) and Streamlit (frontend)

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

# Wait a moment for FastAPI to initialize
sleep 3

# ================================
# 2. START STREAMLIT FRONTEND (Port 8080) - IN FOREGROUND
# ================================
echo "🎬 Starting Streamlit frontend on port 8080..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Streamlit configuration
export STREAMLIT_SERVER_PORT=8080
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export STREAMLIT_SERVER_ENABLE_CORS=true
export STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

# Start Streamlit in foreground (keeps container alive)
streamlit run app.py \
    --server.port=8080 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false \
    --server.enableCORS=true \
    --server.enableXsrfProtection=false

# If Streamlit exits, kill uvicorn too
echo "⚠️ Streamlit stopped, shutting down..."
kill $UVICORN_PID 2>/dev/null || true
