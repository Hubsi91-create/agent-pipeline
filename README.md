# Music Video Production System

AI-powered music video production pipeline with 8 specialized agents and Google Sheets integration.

## 🎬 System Overview

This system automates the entire music video pre-production workflow using 8 specialized AI agents:

### Agent Pipeline

1. **Agent 1: Project Manager** - Creates and tracks video projects
2. **Agent 2: QC Agent** - Quality control for all outputs
3. **Agent 3: Audio Analyzer** - Analyzes music structure, BPM, key, energy
4. **Agent 4: Scene Breakdown** - Creates scene-by-scene breakdown
5. **Agent 5: Style Anchors** - Defines visual style for consistency
6. **Agent 6: Veo Prompter** - Generates prompts for Google Veo
7. **Agent 7: Runway Prompter** - Generates prompts for Runway Gen-3
8. **Agent 8: Prompt Refiner** - Refines prompts based on QC feedback

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Google Cloud Project (for Gemini API & Sheets)
- Google Sheets API credentials

### Installation

1. **Clone and navigate:**
```bash
cd agent-pipeline/backend
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:
```env
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
GOOGLE_SHEET_ID=your-spreadsheet-id
GEMINI_API_KEY=your-gemini-api-key
ENVIRONMENT=development
API_PORT=8000
```

4. **Run the application:**
```bash
python -m app.main
```

or with uvicorn:
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Key Endpoints

#### Create Project
```bash
POST /api/v1/projects
{
  "name": "My Music Video",
  "artist": "Artist Name",
  "song_title": "Song Title"
}
```

#### Upload Audio
```bash
POST /api/v1/agent3/upload
{
  "project_id": "project-uuid",
  "filename": "song.mp3"
}
```

#### Plan Video (Orchestration)
```bash
POST /api/v1/orchestration/plan-video
{
  "project_id": "project-uuid",
  "generate_for_veo": true,
  "generate_for_runway": true
}
```

#### Get Storyboard
```bash
GET /api/v1/storyboard/{project_id}
```

Returns complete storyboard with:
- Project details
- Audio analysis
- Scene breakdown
- Style anchors
- Video prompts (Veo & Runway)
- QC feedback

## 🏗️ Architecture

```
backend/
├── app/
│   ├── agents/                      # Agent services
│   │   ├── agent_1_project_manager/
│   │   ├── agent_2_qc/
│   │   ├── agent_3_audio_analyzer/
│   │   ├── agent_4_scene_breakdown/
│   │   ├── agent_5_style_anchors/
│   │   ├── agent_6_veo_prompter/
│   │   ├── agent_7_runway_prompter/
│   │   └── agent_8_refiner/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints.py         # FastAPI routes
│   ├── infrastructure/
│   │   ├── database/
│   │   │   └── google_sheet_service.py
│   │   └── external_services/
│   │       └── gemini_service.py    # Google Gemini AI
│   ├── models/
│   │   └── data_models.py           # Pydantic models
│   ├── utils/
│   │   └── logger.py
│   └── main.py                      # FastAPI app
├── requirements.txt
└── .env.example
```

## 📊 Google Sheets Integration

The system uses Google Sheets as a database. Required sheets:

1. **A1_Projects_DB** - Project tracking
2. **A2_QC_Feedback_DB** - Quality control feedback
3. **A3_AudioAnalysis_DB** - Audio analysis results
4. **A4_Scenes_DB** - Scene breakdown
5. **A5_Styles_DB** - Style anchors
6. **A6_VeoPrompts_DB** - Veo video prompts
7. **A7_RunwayPrompts_DB** - Runway video prompts
8. **A8_Refinements_DB** - Prompt refinements

These sheets will be auto-created if they don't exist.

## 🎯 Workflow Example

1. **Create Project:**
```python
POST /api/v1/projects
{
  "name": "Summer Vibes",
  "artist": "The Artists",
  "song_title": "Sunset Dreams"
}
# Returns: { "data": { "id": "proj-123", ... } }
```

2. **Upload Audio:**
```python
POST /api/v1/agent3/upload
{
  "project_id": "proj-123",
  "filename": "sunset-dreams.mp3"
}
# Agent 3 analyzes: BPM, key, structure, energy
```

3. **Plan Video:**
```python
POST /api/v1/orchestration/plan-video
{
  "project_id": "proj-123",
  "generate_for_veo": true,
  "generate_for_runway": true
}
# Triggers: Agent 4 → 5 → 6/7 (background)
```

4. **Get Storyboard:**
```python
GET /api/v1/storyboard/proj-123
# Returns complete storyboard with all data
```

5. **QC Review (if needed):**
```python
POST /api/v1/qc/review
{
  "project_id": "proj-123",
  "target_id": "prompt-456",
  "target_type": "prompt",
  "content": "The generated prompt text..."
}
# Agent 2 reviews and provides feedback
```

## 🔧 Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black app/
isort app/
```

### Type Checking
```bash
mypy app/
```

## 🌐 Deployment (Cloud Run)

### Build Docker Image
```bash
docker build -t music-video-production .
```

### Deploy to Cloud Run
```bash
gcloud run deploy music-video-production \
  --image gcr.io/PROJECT_ID/music-video-production \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 📝 Data Models

### Project
- id, name, artist, song_title
- audio_file_path
- status (INIT, ANALYZING, PLANNING, GENERATING, QC, COMPLETE)
- progress_percentage

### Scene
- scene_number, start_time, end_time, duration
- music_section (Intro, Verse, Chorus, etc.)
- description, mood, visual_style_ref
- key_elements, camera_movement

### VideoPrompt
- scene_id, generator (veo/runway)
- prompt_text, technical_params
- status (PENDING_QC, APPROVED, NEEDS_REVISION)
- iteration

## 🎨 Storyboard App Integration

The `/storyboard/{project_id}` endpoint returns ALL data needed for the frontend:

```javascript
{
  "project": { /* Project details */ },
  "audio_analysis": { /* BPM, key, structure */ },
  "scenes": [ /* Scene breakdown */ ],
  "style_anchors": [ /* Visual style guide */ ],
  "prompts": {
    "scene-id-1": [ /* Veo & Runway prompts */ ],
    "scene-id-2": [ /* ... */ ]
  },
  "qc_feedback": [ /* QC reviews */ ]
}
```

## 🔒 Security

- API keys stored in environment variables
- Service account credentials for Google APIs
- CORS configured for production
- Request validation with Pydantic

## 🐛 Troubleshooting

### Google Sheets not connecting
- Check `GOOGLE_APPLICATION_CREDENTIALS` path
- Verify service account has Sheets API access
- Ensure spreadsheet is shared with service account email

### Gemini API errors
- Verify `GEMINI_API_KEY` is correct
- Check API quota in Google Cloud Console
- System falls back to mock responses if API unavailable

## 📄 License

MIT License

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

**Built with:** FastAPI, Google Gemini, Google Sheets API, Pydantic

**Made for:** Music video creators, directors, and production teams
