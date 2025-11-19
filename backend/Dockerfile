FROM python:3.11-slim

WORKDIR /app

# 1. System-Tools installieren (Wichtig: curl für Healthcheck, ffmpeg für Audio)
RUN apt-get update && apt-get install -y \
    gcc \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 2. Python-Pakete installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Code kopieren
COPY . .

# 4. Make start.sh executable (CRITICAL for Cloud Run)
RUN chmod +x start.sh

# 5. Umgebungsvariablen
ENV PORT=8080
# CRITICAL: API_BASE_URL should NOT include /api/v1 (added in app.py requests)
ENV API_BASE_URL="http://127.0.0.1:8000"

# 6. Port freigeben
EXPOSE 8080

# 7. Healthcheck (optional, Cloud Run may not use it but good practice)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/ || exit 1

# 8. Use robust startup script with health checks
CMD ["./start.sh"]