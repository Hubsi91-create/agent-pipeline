#!/bin/bash

# CRITICAL: Exit immediately if any command fails
set -e

# CRITICAL: Exit on undefined variables
set -u

# CRITICAL: Fail on pipe errors
set -o pipefail

echo "=========================================="
echo "🚀 MUSIC VIDEO AGENT SYSTEM - STARTUP"
echo "=========================================="
echo "PORT: ${PORT:-8080}"
echo "BACKEND_PORT: 8000"
echo "=========================================="

# STEP 1: Start FastAPI in background
echo "📡 Starting FastAPI backend on port 8000..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
FASTAPI_PID=$!

echo "⏳ Waiting for FastAPI to be ready..."

# STEP 2: Health check loop with timeout
MAX_WAIT=30
WAIT_COUNT=0

while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    if curl -f http://127.0.0.1:8000/api/v1/health > /dev/null 2>&1; then
        echo "✅ FastAPI is healthy!"
        break
    fi

    # Check if FastAPI process is still alive
    if ! kill -0 $FASTAPI_PID 2>/dev/null; then
        echo "❌ FastAPI process died during startup!"
        exit 1
    fi

    echo "⏳ Waiting for FastAPI... ($WAIT_COUNT/$MAX_WAIT)"
    sleep 1
    WAIT_COUNT=$((WAIT_COUNT + 1))
done

if [ $WAIT_COUNT -eq $MAX_WAIT ]; then
    echo "❌ FastAPI failed to start within ${MAX_WAIT}s"
    kill $FASTAPI_PID 2>/dev/null || true
    exit 1
fi

# STEP 3: Start Streamlit in foreground
echo "🎨 Starting Streamlit frontend on port ${PORT}..."
streamlit run app.py \
    --server.port=${PORT} \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false

# If we reach here, Streamlit has exited
echo "⚠️ Streamlit exited"
exit 0
