# Storyboard Integration - Quick Start Guide

## 🚀 Setup in 5 Minuten

### 1. Install Dependencies

```bash
cd dashboard/backend
pip install -r requirements-storyboard.txt
```

### 2. Set Environment Variable (WICHTIG!)

```bash
# Linux/Mac
export API_KEY_ENCRYPTION_KEY="your-super-secret-key-min-32-chars"

# Windows (PowerShell)
$env:API_KEY_ENCRYPTION_KEY="your-super-secret-key-min-32-chars"

# Windows (CMD)
set API_KEY_ENCRYPTION_KEY=your-super-secret-key-min-32-chars
```

**⚠️ WICHTIG:** Nutze einen sicheren Key (min. 32 Zeichen) für Production!

### 3. Start Backend

```bash
python app.py
```

Output:
```
============================================================
🚀 Music Agents Dashboard Backend Starting...
============================================================
📍 Server: http://localhost:5000
🔧 CORS: Enabled
📊 Database: Initialized
🎯 Endpoints: 26 API routes
✅ Data Provider initialized: LocalDataProvider
✅ Storyboard routes registered at /api/storyboard
============================================================
```

### 4. Verify Installation

```bash
# Health Check
curl http://localhost:5000/api/storyboard/health

# Expected Response:
{
  "status": "operational",
  "service": "Storyboard API",
  "version": "1.0.0",
  "endpoints": {
    "drive": 3,
    "video": 4,
    "metadata": 3,
    "thumbnails": 3,
    "api_keys": 5
  }
}
```

---

## 📚 Usage Examples

### 1. Save API Key (Encrypted)

```bash
curl -X POST http://localhost:5000/api/storyboard/api-keys \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "service": "runway",
    "api_key": "sk-runway-your-api-key-here"
  }'
```

### 2. Generate YouTube Metadata

```bash
curl -X POST http://localhost:5000/api/storyboard/metadata/generate \
  -H "Content-Type: application/json" \
  -d '{
    "song_title": "Summer Vibes",
    "genre": "electronic",
    "mood": "happy"
  }'
```

Response:
```json
{
  "youtube_title": "🎵 Summer Vibes | Electronic Mix 2025",
  "youtube_description": "Experience this happy electronic track...",
  "youtube_tags": "summer vibes, electronic, happy, edm, dance, ...",
  "youtube_hashtags": "#music #electronic #happy #musicvideo ...",
  "trending_score": 85
}
```

### 3. Calculate Video Generation Cost

```bash
curl -X POST http://localhost:5000/api/storyboard/video/calculate-cost \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 60,
    "engine": "runway_standard"
  }'
```

Response:
```json
{
  "duration": 60,
  "engine": "runway_standard",
  "cost_per_10s": 1.20,
  "total_cost": 7.20,
  "total_credits": 72,
  "currency": "USD"
}
```

### 4. Generate Thumbnail Variants

```bash
curl -X POST http://localhost:5000/api/storyboard/thumbnails/generate \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://example.com/video.mp4",
    "context": {
      "song_title": "Summer Vibes",
      "genre": "electronic",
      "mood": "happy"
    },
    "variants": ["bold", "vibrant"]
  }'
```

---

## 🧪 Run Tests

```bash
# Test API Key Manager
python test_api_key_manager.py

# Expected Output:
================================================================================
API KEY MANAGER - TEST SUITE
================================================================================
✅ Encryption Key: Set (35 chars)

============================================================
TEST 1: Save and Retrieve API Keys
============================================================
📝 Saving API keys...
  ✅ runway: created
  ✅ google_drive: created
  ✅ dadan: created
  ✅ recraft: created

🔍 Retrieving API keys...
  runway: sk-runway-test-abc12... ✅ MATCH
  google_drive: ya29.a0AfB_test_tok... ✅ MATCH
  ...

============================================================
✅ ALL TESTS COMPLETED
============================================================
```

---

## 📦 File Structure

```
dashboard/backend/
├── app.py                               # ✅ UPDATED (Blueprint registered)
├── database.py                          # ✅ UPDATED (3 new tables)
├── requirements-storyboard.txt          # ✅ NEW (Dependencies)
│
├── services/
│   ├── google_drive_service.py          # ✅ NEW (OAuth2, Files, Download)
│   ├── runway_service.py                # ✅ NEW (Video Gen, 5 Engines)
│   ├── dadan_service.py                 # ✅ NEW (YouTube Metadata)
│   ├── recraft_service.py               # ✅ NEW (Thumbnails, 5 Variants)
│   └── api_key_manager.py               # ✅ NEW (AES-256 Encryption)
│
├── routes/
│   └── storyboard_routes.py             # ✅ NEW (18 Endpoints)
│
├── test_api_key_manager.py              # ✅ NEW (Test Suite)
├── API_KEY_MANAGEMENT.md                # ✅ NEW (Key Management Docs)
├── STORYBOARD_INTEGRATION.md            # ✅ NEW (Complete Documentation)
└── STORYBOARD_QUICK_START.md            # ✅ NEW (This file)
```

---

## 🎯 Available Endpoints (18)

### Google Drive (3)
- `GET /api/storyboard/drive/folders` - List folders
- `GET /api/storyboard/drive/files/:folder_id` - List files
- `GET /api/storyboard/drive/file/:file_id/metadata` - File metadata

### Runway Video (4)
- `POST /api/storyboard/video/generate` - Generate video
- `GET /api/storyboard/video/:task_id/status` - Poll status
- `GET /api/storyboard/video/engines` - Available engines
- `POST /api/storyboard/video/calculate-cost` - Calculate cost

### Dadan Metadata (3)
- `POST /api/storyboard/metadata/generate` - Generate metadata
- `GET /api/storyboard/metadata/genres` - Supported genres
- `GET /api/storyboard/metadata/moods` - Supported moods

### Recraft Thumbnails (3)
- `POST /api/storyboard/thumbnails/generate` - Generate variants
- `GET /api/storyboard/thumbnails/variants` - Available variants
- `POST /api/storyboard/thumbnails/extract-frame` - Extract frame

### API Key Management (5)
- `POST /api/storyboard/api-keys` - Save encrypted key
- `GET /api/storyboard/api-keys/:user_id` - List keys
- `DELETE /api/storyboard/api-keys/:user_id/:service` - Delete key
- `GET /api/storyboard/api-keys/:user_id/:service/validate` - Validate
- `GET /api/storyboard/api-keys/services` - Supported services

---

## 🔐 Security Features

✅ **AES-256 Encryption** - API Keys verschlüsselt gespeichert
✅ **PBKDF2 Key Derivation** - Sichere Schlüsselableitung
✅ **No Plaintext Storage** - Keine Klartext-Speicherung
✅ **Per-User Keys** - Isolierte API Keys pro User
✅ **Key Rotation** - Unterstützung für Key-Rotation
✅ **Exponential Backoff** - Rate Limiting für externe APIs
✅ **Input Validation** - Alle Endpoints validieren Input

---

## 💰 Pricing Overview

| Engine | Cost/10s | Credits/10s | Speed |
|--------|----------|-------------|-------|
| Veo 3.1 Standard | $7.50 | - | 45s |
| Runway Standard | $1.20 | 12 | 60s |
| Runway Turbo | $0.50 | 5 | 30s |
| Runway Unlimited | FREE | 0 | 90s |

**Example:** 60-second video mit Runway Standard = **$7.20** (72 credits)

---

## 📖 Documentation

- **[STORYBOARD_INTEGRATION.md](STORYBOARD_INTEGRATION.md)** - Complete Integration Guide
- **[API_KEY_MANAGEMENT.md](API_KEY_MANAGEMENT.md)** - API Key Security Guide
- **TypeScript Types:** `dashboard/frontend/src/types/storyboard-api.ts`

---

## 🐛 Troubleshooting

### Problem: `ModuleNotFoundError: No module named 'cryptography'`

**Lösung:**
```bash
pip install cryptography>=41.0.0
```

### Problem: "⚠️ Using default encryption key"

**Lösung:**
```bash
export API_KEY_ENCRYPTION_KEY="your-secure-key-here"
```

### Problem: "Failed to decrypt API key"

**Ursache:** Encryption Key wurde geändert

**Lösung:**
1. Prüfe Environment Variable
2. Falls Key verloren: Lösche alte Keys und erstelle neu

### Problem: "No API key found"

**Lösung:**
```bash
# Speichere Key zuerst
curl -X POST http://localhost:5000/api/storyboard/api-keys \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_123","service":"runway","api_key":"sk-..."}'
```

---

## ✅ Production Checklist

- [ ] Set strong `API_KEY_ENCRYPTION_KEY` (min. 32 chars)
- [ ] Never commit encryption key to Git
- [ ] Use HTTPS in production
- [ ] Implement rate limiting
- [ ] Set up logging/monitoring
- [ ] Configure backup for database
- [ ] Test all endpoints
- [ ] Document API for frontend team
- [ ] Set up CI/CD pipeline

---

## 🆘 Support

**Issues:** [GitHub Issues](https://github.com/...)
**Documentation:** See `STORYBOARD_INTEGRATION.md`
**Test Script:** `python test_api_key_manager.py`

---

**Ready to build amazing music videos! 🎵🎬**
