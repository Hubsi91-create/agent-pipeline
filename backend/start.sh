#!/bin/bash

echo "🚀 Starting Music Video Agent System..."

# 1. Starte FastAPI im Hintergrund (Port 8000)
# Wichtig: --host 0.0.0.0 damit es im Container erreichbar ist
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# 2. Starte Streamlit im Vordergrund
# WICHTIG: Streamlit MUSS auf dem von Cloud Run bereitgestellten $PORT hören (meist 8080)
echo "🚀 Starting Streamlit on port $PORT..."
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
