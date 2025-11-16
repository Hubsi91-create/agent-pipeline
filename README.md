# Music Agents v2

AI-powered music production and marketing agent pipeline built with FastAPI, Google Sheets, and Vertex AI (Gemini).

## Overview

Music Agents v2 is an intelligent multi-phase pipeline that analyzes trends, generates creative prompts, performs quality control, and stores approved best practices for music production and marketing.

### Features

- **Trend Analysis (Phase A1):** Analyzes current trends using Gemini AI
- **Prompt Generation (Phase A2):** Generates creative prompts for music videos, social media, and marketing
- **Quality Control (QC):** Automated quality assessment and prompt improvement
- **Best Practices Database:** Stores approved prompts in Google Sheets
- **Cloud-Native:** Deployed on Google Cloud Run with auto-scaling
- **FastAPI Backend:** Modern, fast API with automatic documentation

## Quick Start

See [SETUP.md](SETUP.md) for detailed setup instructions.

### Local Development

```bash
# Install dependencies
cd backend/
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Google Cloud credentials

# Run the server
uvicorn main:app --reload --port 8080

# Open browser
# http://localhost:8080/docs
```

### Deploy to Cloud Run

```bash
# From project root
./deploy.sh
```

## Architecture

```
FastAPI Backend → Orchestrator → Vertex AI (Gemini)
                       ↓
               Google Sheets (Database)
```

## API Endpoints

- `GET /health` - Health check
- `POST /api/v1/orchestration/run-phase-a` - Execute Phase A pipeline
- `GET /docs` - Interactive API documentation (Swagger UI)

## Tech Stack

- **Backend:** FastAPI, Python 3.11
- **AI:** Google Vertex AI (Gemini 1.5 Pro)
- **Database:** Google Sheets
- **Deployment:** Google Cloud Run, Docker
- **Tools:** gspread, Pydantic, Uvicorn, Gunicorn

## Documentation

- [SETUP.md](SETUP.md) - Complete setup and deployment guide

## License

MIT