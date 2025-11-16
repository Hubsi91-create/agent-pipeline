# Storyboard Backend Integration

## 🎯 Overview

Die Storyboard Backend Integration erweitert das Flask Backend mit **18 neuen API Endpoints** für die komplette Music Video Production Workflow inkl. verschlüsselter API Key Verwaltung.

**Version:** 1.0.0
**Status:** Production Ready ✅

---

## 📦 Neue Komponenten

### Services (4 Dateien)

1. **`services/google_drive_service.py`**
   - OAuth2 Integration (Manual Token Input)
   - Folder/File Browsing
   - File Metadata Extraction
   - Download URL Generation
   - Exponential Backoff Error Handling

2. **`services/runway_service.py`**
   - Runway Gen-4 Video Generation
   - 5 Engine Support (Veo 3.1, Runway Standard/Turbo/Unlimited)
   - Cost Calculation
   - Task Management & Polling
   - Retry Logic

3. **`services/dadan_service.py`**
   - YouTube Metadata Generation
   - SEO-Optimized Titles/Descriptions
   - Tag & Hashtag Generation
   - Trending Score Calculation
   - 30-Day Caching (In-Memory)

4. **`services/recraft_service.py`**
   - Thumbnail Generation (5 Variants)
   - Click Prediction Scoring
   - Frame Extraction
   - A/B Testing Support
   - Performance Analysis

### Routes

**`routes/storyboard_routes.py`** - 18 API Endpoints:

#### Google Drive (3 Endpoints)
- `GET /api/storyboard/drive/folders` - List folders
- `GET /api/storyboard/drive/files/:folder_id` - List files
- `GET /api/storyboard/drive/file/:file_id/metadata` - File metadata

#### Runway Video (4 Endpoints)
- `POST /api/storyboard/video/generate` - Start generation
- `GET /api/storyboard/video/:task_id/status` - Poll status
- `GET /api/storyboard/video/engines` - Available engines
- `POST /api/storyboard/video/calculate-cost` - Cost calculator

#### Dadan Metadata (3 Endpoints)
- `POST /api/storyboard/metadata/generate` - Generate metadata
- `GET /api/storyboard/metadata/genres` - Supported genres
- `GET /api/storyboard/metadata/moods` - Supported moods

#### Recraft Thumbnails (3 Endpoints)
- `POST /api/storyboard/thumbnails/generate` - Generate variants
- `GET /api/storyboard/thumbnails/variants` - Available variants
- `POST /api/storyboard/thumbnails/extract-frame` - Extract frame

#### API Key Management (5 Endpoints)
- `POST /api/storyboard/api-keys` - Save encrypted API key
- `GET /api/storyboard/api-keys/:user_id` - List user's API keys
- `DELETE /api/storyboard/api-keys/:user_id/:service` - Delete API key
- `GET /api/storyboard/api-keys/:user_id/:service/validate` - Validate key
- `GET /api/storyboard/api-keys/services` - Get supported services

---

## 🗄️ Database Schema Updates

### Neue Tabellen

**`api_keys`** - Encrypted API Key Storage
```sql
CREATE TABLE api_keys (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    service TEXT NOT NULL,
    encrypted_key TEXT NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(user_id, service)
);
```

**`storyboard_videos`** - Video Generation Tasks
```sql
CREATE TABLE storyboard_videos (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    project_name TEXT,
    song_title TEXT,
    music_file TEXT,
    genre TEXT,
    bpm INTEGER,
    engine TEXT,
    prompt TEXT,
    video_url TEXT,
    status TEXT,
    youtube_title TEXT,
    youtube_description TEXT,
    youtube_tags TEXT,
    cost REAL,
    credits_used INTEGER,
    duration INTEGER,
    created_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);
```

**`storyboard_thumbnails`** - Thumbnail Variants
```sql
CREATE TABLE storyboard_thumbnails (
    id TEXT PRIMARY KEY,
    video_id TEXT,
    variant TEXT,
    image_url TEXT,
    click_prediction REAL,
    is_selected BOOLEAN,
    created_at TIMESTAMP,
    FOREIGN KEY (video_id) REFERENCES storyboard_videos(id)
);
```

---

## 🚀 Usage Examples

### 1. Google Drive Integration

```python
# List folders in root directory
response = requests.get(
    'http://localhost:5000/api/storyboard/drive/folders',
    params={'access_token': 'YOUR_OAUTH_TOKEN'}
)
folders = response.json()['folders']

# List audio files in folder
response = requests.get(
    f'http://localhost:5000/api/storyboard/drive/files/{folder_id}',
    params={
        'access_token': 'YOUR_OAUTH_TOKEN',
        'file_type': 'audio'
    }
)
files = response.json()['files']
```

### 2. Runway Video Generation

```python
# Start video generation
response = requests.post(
    'http://localhost:5000/api/storyboard/video/generate',
    json={
        'prompt': 'Epic cinematic music video with dramatic lighting',
        'duration': 60,
        'style': 'cinematic',
        'engine': 'runway_standard',
        'music_file': 'https://drive.google.com/...'
    }
)
task = response.json()

# Poll status
response = requests.get(
    f'http://localhost:5000/api/storyboard/video/{task["task_id"]}/status'
)
status = response.json()
```

### 3. Dadan Metadata Generation

```python
# Generate YouTube metadata
response = requests.post(
    'http://localhost:5000/api/storyboard/metadata/generate',
    json={
        'song_title': 'Summer Vibes',
        'genre': 'electronic',
        'mood': 'happy'
    }
)
metadata = response.json()

print(metadata['youtube_title'])
print(metadata['youtube_description'])
print(metadata['youtube_tags'])
print(metadata['trending_score'])
```

### 4. Recraft Thumbnail Generation

```python
# Generate thumbnail variants
response = requests.post(
    'http://localhost:5000/api/storyboard/thumbnails/generate',
    json={
        'video_url': 'https://runway.ml/...',
        'context': {
            'song_title': 'Summer Vibes',
            'genre': 'electronic',
            'mood': 'happy'
        },
        'variants': ['bold', 'vibrant', 'minimal']
    }
)
thumbnails = response.json()['thumbnails']

# Best thumbnail (sorted by click_prediction)
best = thumbnails[0]
print(f"Best: {best['variant']} - {best['click_prediction']*100}% CTR")
```

---

## 🔐 API Key Management

### Encrypted Storage

API Keys werden **verschlüsselt** mit AES-256 in der `api_keys` Tabelle gespeichert.

**Features:**
- ✅ AES-256 Encryption via Fernet
- ✅ PBKDF2 Key Derivation
- ✅ No Plaintext Storage
- ✅ Per-User API Keys
- ✅ Key Rotation Support

**Implementation:**

```python
from services.api_key_manager import save_api_key, get_api_key

# Save API key (encrypted)
result = save_api_key(
    user_id="user_123",
    service="runway",
    api_key="sk-runway-abc123xyz..."
)

# Get API key (decrypted)
api_key = get_api_key(user_id="user_123", service="runway")
```

**Supported Services:**
- `google_drive` - OAuth2 token
- `runway` - Runway ML API key
- `dadan` - Dadan AI API key
- `recraft` - Recraft AI API key

**📚 Siehe:** [API_KEY_MANAGEMENT.md](API_KEY_MANAGEMENT.md) für Details

---

## 💰 Pricing Information

### Runway Engines

| Engine | Cost per 10s | Credits per 10s | Speed |
|--------|--------------|-----------------|-------|
| Veo 3.1 Standard | $7.50 | - | 45s |
| Veo 3.1 Fast | Manual Pricing | - | 20s |
| Runway Standard | $1.20 | 12 | 60s |
| Runway Turbo | $0.50 | 5 | 30s |
| Runway Unlimited | FREE | 0 | 90s |

### Cost Calculation Example

```python
# Calculate cost for 60-second video
response = requests.post(
    'http://localhost:5000/api/storyboard/video/calculate-cost',
    json={
        'duration': 60,
        'engine': 'runway_standard'
    }
)

cost = response.json()
# {
#   "duration": 60,
#   "engine": "runway_standard",
#   "cost_per_10s": 1.20,
#   "total_cost": 7.20,
#   "total_credits": 72,
#   "currency": "USD"
# }
```

---

## 📊 Error Handling

### Standardized Error Response

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "retryable": true,
  "timestamp": "2025-11-14T10:30:00Z",
  "details": {
    "required": 12,
    "available": 5
  }
}
```

### Common Error Codes

#### Google Drive
- `TOKEN_REQUIRED` - OAuth token missing
- `TOKEN_EXPIRED` - Token needs refresh
- `NOT_FOUND` - File/folder not found
- `RATE_LIMIT` - API rate limit exceeded

#### Runway
- `API_KEY_REQUIRED` - API key missing
- `INSUFFICIENT_CREDITS` - Not enough credits
- `GENERATION_FAILED` - Generation error
- `TASK_NOT_FOUND` - Invalid task ID
- `MAX_RETRIES_EXCEEDED` - Too many retry attempts

#### General
- `ENDPOINT_ERROR` - Server error (retryable)
- `INVALID_REQUEST` - Malformed request
- `MISSING_FIELDS` - Required fields missing

---

## 🧪 Testing

### Health Check

```bash
curl http://localhost:5000/api/storyboard/health
```

Response:
```json
{
  "status": "operational",
  "service": "Storyboard API",
  "version": "1.0.0",
  "timestamp": "2025-11-14T10:30:00Z",
  "endpoints": {
    "drive": 3,
    "video": 4,
    "metadata": 3,
    "thumbnails": 3
  }
}
```

### Root API Info

```bash
curl http://localhost:5000/
```

Response now includes:
```json
{
  "service": "Music Agents Dashboard API",
  "version": "1.0.0",
  "status": "operational",
  "endpoints_available": 26,
  "storyboard_endpoints_available": 13,
  "total_endpoints": 39,
  "storyboard_health": "/api/storyboard/health"
}
```

---

## 🎨 Frontend Integration

### TypeScript Types

```typescript
import {
  ApiResponse,
  isApiError,
  VideoGenerationRequest,
  VideoGenerationTask,
  YouTubeMetadata,
  Thumbnail,
  StoryboardEndpoints,
  fetchStoryboardApi
} from '@/types/storyboard-api';

// Example: Generate video
const request: VideoGenerationRequest = {
  prompt: 'Epic cinematic music video',
  duration: 60,
  engine: 'runway_standard'
};

const response = await fetchStoryboardApi<VideoGenerationTask>(
  StoryboardEndpoints.VIDEO_GENERATE,
  {
    method: 'POST',
    body: JSON.stringify(request)
  }
);

if (isApiError(response)) {
  console.error('Error:', response.message);
} else {
  console.log('Task ID:', response.task_id);
}
```

---

## 🔄 Integration Checklist

- [x] Google Drive Service erstellt
- [x] Runway Service erstellt
- [x] Dadan Service erstellt
- [x] Recraft Service erstellt
- [x] Storyboard Routes erstellt (18 Endpoints)
- [x] Database Schema erweitert (3 neue Tabellen)
- [x] app.py Blueprint registriert
- [x] TypeScript Types erstellt
- [x] **API Key Encryption implementiert** ✅
- [x] API Key Management Endpoints (5 neue) ✅
- [x] Test Script erstellt ✅
- [ ] Frontend UI Components erstellen
- [ ] End-to-End Tests schreiben

---

## 📝 Next Steps

### Backend
1. **~~API Key Encryption~~** ✅ DONE
   - ~~Implement `get_api_key()` in routes~~
   - ~~Use `cryptography` library for AES encryption~~
   - ~~Store encryption key in environment variable~~

2. **Database Methods**
   - Add storyboard-specific methods to `database.py`
   - `save_video_task()`, `get_video_tasks()`
   - `save_thumbnails()`, `get_thumbnails()`

3. **Logging**
   - Add detailed logging for all API calls
   - Store logs in `dashboard/backend/logs/storyboard/`

### Frontend
1. **React Components**
   - `<GoogleDriveBrowser />` - File picker
   - `<RunwayGenerator />` - Video generation UI
   - `<MetadataEditor />` - YouTube metadata form
   - `<ThumbnailPicker />` - Thumbnail A/B testing

2. **State Management**
   - Add Zustand store for storyboard state
   - Track video generation tasks
   - Cache API responses

3. **UI/UX**
   - Progress indicators for generation
   - Error toast notifications
   - Cost calculator widget

---

## 🤝 Contributing

When extending the Storyboard integration:

1. **Services**: Add new services to `dashboard/backend/services/`
2. **Routes**: Add endpoints to `routes/storyboard_routes.py`
3. **Types**: Update `frontend/src/types/storyboard-api.ts`
4. **Database**: Extend schema in `database.py`
5. **Documentation**: Update this README

---

## 📚 API Documentation

Full API documentation available at:
- Swagger UI: `http://localhost:5000/api/docs` (coming soon)
- Postman Collection: `docs/storyboard-api.postman_collection.json` (coming soon)

---

## ⚡ Performance

- **Caching**: Dadan metadata cached for 30 days
- **Async Operations**: Video generation runs asynchronously
- **Exponential Backoff**: Automatic retry on rate limits
- **Database Indexes**: Optimized for fast queries

---

## 🔒 Security

- **API Keys**: Encrypted at rest in database
- **OAuth2**: Secure Google Drive authentication
- **Rate Limiting**: Exponential backoff for API calls
- **Input Validation**: All endpoints validate input
- **CORS**: Configured in app.py

---

## 📞 Support

For issues or questions:
- GitHub Issues: [music-agents-repo/issues](https://github.com/...)
- Documentation: See `CLOUD_READY_ARCHITECTURE.md`

---

**Built with ❤️ by Music Video Production System**
