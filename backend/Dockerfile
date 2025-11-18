# Dockerfile for Music Video Production System

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (including ffmpeg for audio processing and curl for health checks)
RUN apt-get update && apt-get install -y \
    gcc \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/
COPY app.py .
COPY start.sh .

# Make start script executable
RUN chmod +x start.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

# Expose ports (8000 for FastAPI, 8080 for Streamlit)
EXPOSE 8000 8080

# Run dual-service startup script
CMD ["./start.sh"]
