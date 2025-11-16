# API Key Management - Verschlüsselte Speicherung

## 🔐 Overview

Das API Key Management System ermöglicht die **sichere, verschlüsselte Speicherung** von API Keys für externe Services (Google Drive, Runway, Dadan, Recraft).

**Features:**
- ✅ AES-256 Verschlüsselung
- ✅ PBKDF2 Key Derivation
- ✅ Keine Plaintext-Speicherung
- ✅ Per-User API Keys
- ✅ Key Rotation Support
- ✅ Validation & Expiry Handling

---

## 🏗️ Architektur

### Encryption Flow

```
Plain API Key
    ↓
[PBKDF2 Key Derivation]
    ↓
[AES-256 Encryption via Fernet]
    ↓
Encrypted API Key (Base64)
    ↓
[SQLite Database Storage]
```

### Decryption Flow

```
[Database Query]
    ↓
Encrypted API Key (Base64)
    ↓
[AES-256 Decryption via Fernet]
    ↓
[PBKDF2 Key Derivation]
    ↓
Plain API Key
```

---

## 🔑 Environment Setup

### 1. Set Encryption Key

**WICHTIG:** Setze einen sicheren Encryption Key als Environment Variable:

```bash
# Linux/Mac
export API_KEY_ENCRYPTION_KEY="your-super-secret-key-min-32-chars"

# Windows
set API_KEY_ENCRYPTION_KEY=your-super-secret-key-min-32-chars
```

**Production Best Practices:**
- Mindestens 32 Zeichen
- Kombiniere Buchstaben, Zahlen, Sonderzeichen
- Nutze einen Password Manager zur Generierung
- **NIE** im Code committed!

### 2. Default Key (Development Only)

Wenn keine Environment Variable gesetzt ist, wird ein Default Key verwendet:
```
⚠️  No encryption key found! Using default (NOT SECURE FOR PRODUCTION)
```

**Dieser Key ist NUR für lokale Development!**

---

## 📡 API Endpoints

### 1. Save API Key

**Endpoint:** `POST /api/storyboard/api-keys`

**Request:**
```json
{
  "user_id": "user_123",
  "service": "runway",
  "api_key": "sk-runway-abc123xyz..."
}
```

**Response (Created):**
```json
{
  "success": true,
  "action": "created",
  "user_id": "user_123",
  "service": "runway",
  "timestamp": "2025-11-14T10:30:00Z"
}
```

**Response (Updated):**
```json
{
  "success": true,
  "action": "updated",
  "user_id": "user_123",
  "service": "runway",
  "timestamp": "2025-11-14T10:30:00Z"
}
```

---

### 2. List API Keys

**Endpoint:** `GET /api/storyboard/api-keys/:user_id`

**Response:**
```json
{
  "user_id": "user_123",
  "services": [
    {
      "service": "google_drive",
      "created_at": "2025-11-14T09:00:00",
      "updated_at": "2025-11-14T09:00:00",
      "has_key": true
    },
    {
      "service": "runway",
      "created_at": "2025-11-14T10:30:00",
      "updated_at": "2025-11-14T10:30:00",
      "has_key": true
    }
  ],
  "count": 2
}
```

**Hinweis:** Keys werden NIE im Klartext zurückgegeben!

---

### 3. Delete API Key

**Endpoint:** `DELETE /api/storyboard/api-keys/:user_id/:service`

**Response:**
```json
{
  "success": true,
  "deleted": true,
  "user_id": "user_123",
  "service": "runway"
}
```

---

### 4. Validate API Key

**Endpoint:** `GET /api/storyboard/api-keys/:user_id/:service/validate`

**Response:**
```json
{
  "user_id": "user_123",
  "service": "runway",
  "has_key": true,
  "valid": true,
  "timestamp": "2025-11-14T10:30:00Z"
}
```

---

### 5. Get Supported Services

**Endpoint:** `GET /api/storyboard/api-keys/services`

**Response:**
```json
{
  "services": {
    "google_drive": {
      "name": "Google Drive",
      "description": "OAuth2 access token for Google Drive API",
      "required": true
    },
    "runway": {
      "name": "Runway ML",
      "description": "API key for Runway Gen-4 video generation",
      "required": true
    },
    "dadan": {
      "name": "Dadan AI",
      "description": "API key for YouTube metadata generation",
      "required": false
    },
    "recraft": {
      "name": "Recraft AI",
      "description": "API key for thumbnail generation",
      "required": false
    }
  },
  "count": 4,
  "timestamp": "2025-11-14T10:30:00Z"
}
```

---

## 💻 Python Usage

### Save API Key

```python
from services.api_key_manager import save_api_key

result = save_api_key(
    user_id="user_123",
    service="runway",
    api_key="sk-runway-abc123xyz..."
)

if result.get('success'):
    print(f"✅ API Key {result['action']}")
else:
    print(f"❌ Error: {result['message']}")
```

### Get API Key

```python
from services.api_key_manager import get_api_key

api_key = get_api_key(user_id="user_123", service="runway")

if api_key:
    print(f"✅ Retrieved key: {api_key[:10]}...")
else:
    print("❌ No API key found")
```

### Validate API Key

```python
from services.api_key_manager import validate_api_key

is_valid = validate_api_key(user_id="user_123", service="runway")

if is_valid:
    print("✅ API Key exists and is valid")
else:
    print("❌ No valid API Key found")
```

### Delete API Key

```python
from services.api_key_manager import delete_api_key

result = delete_api_key(user_id="user_123", service="runway")

if result.get('deleted'):
    print("✅ API Key deleted")
else:
    print("❌ API Key not found")
```

---

## 🧪 Testing

### 1. Save Test Key

```bash
curl -X POST http://localhost:5000/api/storyboard/api-keys \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "service": "runway",
    "api_key": "sk-test-123456"
  }'
```

### 2. List Keys

```bash
curl http://localhost:5000/api/storyboard/api-keys/test_user
```

### 3. Validate Key

```bash
curl http://localhost:5000/api/storyboard/api-keys/test_user/runway/validate
```

### 4. Delete Key

```bash
curl -X DELETE http://localhost:5000/api/storyboard/api-keys/test_user/runway
```

---

## 🔄 Key Rotation

### Warum Key Rotation?

- Sicherheitsvorfall (Encryption Key kompromittiert)
- Regelmäßige Rotation (Best Practice)
- Migration zu neuem Encryption Algorithmus

### Rotation Durchführen

```python
from services.api_key_manager import get_api_key_manager

manager = get_api_key_manager()

result = manager.rotate_encryption_key(
    old_encryption_key="old-key-123",
    new_encryption_key="new-key-456"
)

print(f"Rotated {result['rotated_count']} keys")
```

**WICHTIG:** Nach Rotation muss die neue Key in Environment Variable gesetzt werden!

---

## 🛡️ Security Best Practices

### ✅ DO

- **Nutze Environment Variables** für Encryption Key
- **Setze starke Keys** (min. 32 Zeichen)
- **Rotiere Keys regelmäßig** (z.B. alle 6 Monate)
- **Logge API Key Access** (wer, wann, welcher Service)
- **Nutze HTTPS** in Production
- **Implementiere Rate Limiting** für Key-Endpoints

### ❌ DON'T

- **NIE** Encryption Key im Code
- **NIE** API Keys in Logs
- **NIE** Default Key in Production
- **NIE** Keys per E-Mail versenden
- **NIE** Keys in Git committed

---

## 🗄️ Database Schema

```sql
CREATE TABLE api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    service TEXT NOT NULL,
    encrypted_key TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, service)
);

CREATE INDEX idx_api_keys_user ON api_keys(user_id);
```

---

## 📊 Monitoring & Logging

### Logged Events

```python
# API Key gespeichert
logger.info(f"Saved new API key for {service} (user: {user_id})")

# API Key abgerufen
logger.info(f"Retrieved API key for {service} (user: {user_id})")

# API Key gelöscht
logger.info(f"Deleted API key for {service} (user: {user_id})")

# Fehler
logger.error(f"Failed to decrypt API key: {error}")
logger.warning(f"No API key found for {service} (user: {user_id})")
```

### Monitoring Metrics

- API Key Saves per Hour
- API Key Retrievals per Hour
- Failed Decryptions (potentielle Angriffe)
- Missing Keys (Services ohne API Key)

---

## 🚀 Integration in Services

### Beispiel: Runway Service

```python
# In routes/storyboard_routes.py
from services.api_key_manager import get_api_key as get_encrypted_api_key

def get_api_key(user_id: str, service: str) -> str:
    """Get API key from encrypted storage"""
    try:
        api_key = get_encrypted_api_key(user_id, service)
        return api_key or ""
    except Exception as e:
        logger.error(f"Failed to retrieve API key: {str(e)}")
        return ""

# In endpoint
@storyboard_bp.route('/video/generate', methods=['POST'])
def video_generate():
    # Get encrypted API key
    api_key = get_api_key('user_1', 'runway')

    # Create service with decrypted key
    runway_service = create_runway_service(api_key)

    # Use service
    result = runway_service.generate_video(...)
```

---

## 🔧 Troubleshooting

### Problem: "Failed to decrypt API key"

**Ursache:** Encryption Key hat sich geändert

**Lösung:**
1. Prüfe `API_KEY_ENCRYPTION_KEY` Environment Variable
2. Führe Key Rotation durch (falls Key absichtlich geändert)
3. Falls alter Key verloren: Lösche alte Keys und erstelle neu

### Problem: "No API key found"

**Ursache:** Key wurde nie gespeichert

**Lösung:**
1. Speichere Key via `POST /api/storyboard/api-keys`
2. Validiere mit `GET /api/storyboard/api-keys/:user_id/:service/validate`

### Problem: "⚠️ Using default encryption key"

**Ursache:** Keine Environment Variable gesetzt

**Lösung:**
```bash
export API_KEY_ENCRYPTION_KEY="your-secure-key"
```

---

## 📝 Next Steps

- [ ] Implementiere Key Expiry (automatisches Ablaufen nach X Tagen)
- [ ] Füge Audit Log hinzu (wer hat wann welchen Key abgerufen)
- [ ] Implementiere Multi-Factor Auth für Key-Änderungen
- [ ] Nutze Hardware Security Module (HSM) in Production
- [ ] Implementiere Key Backup/Recovery

---

## 📚 References

- [Cryptography Library Docs](https://cryptography.io/en/latest/)
- [PBKDF2 Key Derivation](https://en.wikipedia.org/wiki/PBKDF2)
- [Fernet Symmetric Encryption](https://cryptography.io/en/latest/fernet/)
- [OWASP Key Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Key_Management_Cheat_Sheet.html)

---

**Built with 🔐 by Music Video Production System**
