# 11-Agent Music Video Production System - Backend (Phase A)

Cloud-native AI pipeline for automated music video production using Google Cloud and Gemini AI.

## 🎯 Phase A Components

### Agent 1: Trend Detective
Identifies current viral music trends using Gemini AI.
- **Input**: Trend count
- **Output**: Trend reports stored in `A1_Trends_DB` (Google Sheets)
- **Features**: Analyzes viral music trends, genres, and production styles

### Agent 2: Suno Prompt Generator
Generates optimized Suno v5 prompts based on trends.
- **Input**: NEW trend reports
- **Output**: Suno prompts stored in `A2_GeneratedPrompts_DB`
- **Features**: Few-Shot Learning from approved prompts

### QC Processor
Quality control with automated feedback loop.
- **Input**: PENDING_QC prompts
- **Output**: QC results + Best practices for Few-Shot Learning
- **Features**: Evaluates prompts, scores 1-10, adds high-scoring prompts to best practices

## 🏗️ Architecture

```
backend/
├── app/
│   ├── agents/               # Agent services
│   │   ├── agent_1_trend_detective/
│   │   ├── agent_2_suno_generator/
│   │   └── qc_processor/
│   ├── api/                  # API endpoints
│   │   └── v1/
│   ├── core/                 # Configuration
│   ├── infrastructure/       # External services
│   │   ├── database/        # Google Sheets
│   │   └── llm/             # Gemini AI
│   └── models/              # Pydantic models
├── main.py                   # FastAPI application
└── requirements.txt          # Dependencies
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Google Cloud Project with:
  - Vertex AI API enabled
  - Google Sheets API enabled
  - Service Account with appropriate permissions
- Google Sheet created for database

### Local Development

1. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Set up Google Cloud authentication:**
```bash
# Option 1: Use Application Default Credentials
gcloud auth application-default login

# Option 2: Use Service Account JSON (add to .env)
# GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
```

4. **Create Google Sheets database:**
- Create a new Google Sheet
- Copy the Sheet ID from the URL
- Add to `.env`: `GOOGLE_SHEET_ID=your_sheet_id`
- The system will auto-create these worksheets:
  - `A1_Trends_DB`
  - `A2_GeneratedPrompts_DB`
  - `QC_Results_DB`
  - `ApprovedBestPractices`

5. **Run the application:**
```bash
python main.py
```

6. **Access the API:**
- API Docs: http://localhost:8080/docs
- API: http://localhost:8080/api/v1/

## 📡 API Endpoints

### System
- `GET /health` - Health check
- `GET /` - API information

### Agent 1: Trend Detective
- `POST /api/v1/agent1/run` - Generate trend reports (sync)
- `POST /api/v1/agent1/run-async` - Generate trend reports (async)

### Agent 2: Suno Generator
- `POST /api/v1/agent2/run` - Generate Suno prompts (sync)
- `POST /api/v1/agent2/run-async` - Generate prompts (async)

### QC Processor
- `POST /api/v1/qc/run` - Run quality control (sync)
- `POST /api/v1/qc/run-async` - Run QC (async)

### Orchestration
- `POST /api/v1/orchestration/run-phase-a` - Run complete pipeline (sync)
- `POST /api/v1/orchestration/run-phase-a-async` - Run pipeline (async)

## 🔄 Workflow

**Complete Phase A Pipeline:**

```
1. Agent 1 → Generate Trends
   └─> Stores in A1_Trends_DB (status: NEW)

2. Agent 2 → Process NEW Trends
   ├─> Loads best practices for Few-Shot Learning
   ├─> Generates prompts (70-100 words each)
   ├─> Stores in A2_GeneratedPrompts_DB (status: PENDING_QC)
   └─> Updates trends (status: PROCESSED)

3. QC Processor → Evaluate PENDING_QC Prompts
   ├─> Evaluates each prompt (score 1-10)
   ├─> Stores results in QC_Results_DB
   ├─> If score >= 7: Adds to ApprovedBestPractices
   └─> Updates prompts (status: REVIEWED)

4. Loop → Agent 2 uses ApprovedBestPractices for Few-Shot Learning
```

## 🧪 Example API Usage

### Run Complete Pipeline
```bash
curl -X POST http://localhost:8080/api/v1/orchestration/run-phase-a
```

### Run Individual Agents
```bash
# Agent 1: Generate 10 trends
curl -X POST http://localhost:8080/api/v1/agent1/run \
  -H "Content-Type: application/json" \
  -d '{"count": 10}'

# Agent 2: Generate 15 prompts per trend
curl -X POST http://localhost:8080/api/v1/agent2/run \
  -H "Content-Type: application/json" \
  -d '{"count": 15}'

# QC: Process queue
curl -X POST http://localhost:8080/api/v1/qc/run
```

## 🌩️ Google Cloud Run Deployment

### Build and Deploy
```bash
# Build container
gcloud builds submit --tag gcr.io/music-agents-prod/music-agents-v2

# Deploy to Cloud Run
gcloud run deploy music-agents-v2 \
  --image gcr.io/music-agents-prod/music-agents-v2 \
  --platform managed \
  --region europe-west3 \
  --set-env-vars GOOGLE_SHEET_ID=your_sheet_id \
  --allow-unauthenticated
```

### Service Account Permissions
Ensure the Cloud Run service account has:
- `roles/aiplatform.user` (Vertex AI)
- Google Sheets access via service account

## 🔒 Environment Variables

See `.env.example` for all available configuration options.

**Critical Variables:**
- `GOOGLE_PROJECT_ID` - GCP Project ID
- `GOOGLE_SHEET_ID` - Google Sheet database ID
- `GOOGLE_REGION` - GCP region (default: global)

## 📊 Data Models

### TrendReport (A1_Trends_DB)
```json
{
  "id": "uuid",
  "timestamp": "2025-11-16T12:00:00",
  "genre": "Afrobeat",
  "details": "Description...",
  "viral_potential": 8,
  "status": "NEW|PROCESSED"
}
```

### SunoPrompt (A2_GeneratedPrompts_DB)
```json
{
  "id": "uuid",
  "trend_id": "uuid",
  "timestamp": "2025-11-16T12:00:00",
  "prompt_text": "Create an Afrobeat track...",
  "status": "PENDING_QC|REVIEWED|FAILED"
}
```

### QCResult (QC_Results_DB)
```json
{
  "id": "uuid",
  "prompt_id": "uuid",
  "timestamp": "2025-11-16T12:00:00",
  "score": 9,
  "feedback": "Excellent quality..."
}
```

### ApprovedPrompt (ApprovedBestPractices)
```json
{
  "id": "uuid",
  "prompt_text": "Create an Afrobeat track...",
  "score": 9,
  "source": "Generated|Community",
  "timestamp": "2025-11-16T12:00:00"
}
```

## 🛠️ Development

### Run Tests (Coming Soon)
```bash
pytest
```

### Code Formatting
```bash
black .
```

### Type Checking
```bash
mypy app/
```

## 📈 Monitoring

- Logs are output to stdout (compatible with Cloud Logging)
- Check logs for agent progress and errors
- Use Google Sheets for visual monitoring of data

## 🔮 Future Phases

**Phase B:** Audio-Visual Transformation (Agents 3-8)
**Phase C:** Post-Production & Orchestration (Agents 9-11)

## 📝 License

Proprietary - Music Agents Production System

## 🤝 Support

For issues and questions, check the logs and API documentation at `/docs`.
