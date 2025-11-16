# Production Logging - Quick Start Guide

## 🚀 Getting Started in 30 Seconds

### 1. Start the Server
```bash
cd dashboard/backend
python app.py
```

### 2. Make Some API Calls
```bash
curl http://localhost:5000/api/dashboard/overview
curl http://localhost:5000/api/agents/status
```

### 3. View the Logs
```bash
# Human-readable logs
tail -f logs/api.log

# JSON structured logs
tail -f logs/api_structured.jsonl | jq
```

**That's it!** All API calls are automatically logged.

---

## 📊 What Gets Logged

Every API request automatically includes:

✅ **Request ID** - Unique UUID for tracing
✅ **Timestamp** - ISO 8601 format
✅ **Method & Path** - GET /api/dashboard/overview
✅ **Response Time** - Milliseconds
✅ **Status Code** - 200, 404, 500, etc.
✅ **Query Params** - All query parameters
✅ **Remote IP** - Client IP address
✅ **User Agent** - Browser/client info

---

## 🎯 Quick Examples

### Example 1: Successful Request
```
[2025-01-14 10:30:15] INFO [api] API Request: GET /api/dashboard/overview
[2025-01-14 10:30:15] INFO [api] API Response: GET /api/dashboard/overview - 200
```

### Example 2: Slow Request (Warning)
```
[2025-01-14 10:30:16] WARNING [api] Slow API Request: GET /api/metrics/trends - 1250ms
```

### Example 3: Error
```
[2025-01-14 10:30:17] ERROR [api] API Error: POST /api/video/generate - 500
```

### Example 4: JSON Log Entry
```json
{
  "timestamp": "2025-01-14T10:30:15Z",
  "level": "INFO",
  "message": "API Response: GET /api/dashboard/overview - 200",
  "request_id": "abc-123-def",
  "method": "GET",
  "path": "/api/dashboard/overview",
  "status_code": 200,
  "response_time_ms": 45.23
}
```

---

## 🔧 Configuration (Optional)

Create `.env` file:

```bash
# Production Settings
LOG_LEVEL=INFO
SLOW_REQUEST_THRESHOLD_MS=500
LOG_REQUEST_BODY=false
LOG_RESPONSE_BODY=false

# Development Settings
# LOG_LEVEL=DEBUG
# SLOW_REQUEST_THRESHOLD_MS=100
# LOG_REQUEST_BODY=true
```

---

## 📁 Log Files

```
logs/
├── api.log                  # Human-readable (10MB max, 10 backups)
└── api_structured.jsonl     # JSON logs (daily rotation, 30 days)
```

---

## 🔍 Quick Analysis Commands

```bash
# Watch logs in real-time
tail -f logs/api.log

# Find errors
grep "ERROR" logs/api.log

# Find slow requests
jq 'select(.response_time_ms > 1000)' logs/api_structured.jsonl

# Count requests by endpoint
jq -r '.endpoint' logs/api_structured.jsonl | sort | uniq -c | sort -rn

# Average response time
jq -s 'map(.response_time_ms) | add / length' logs/api_structured.jsonl
```

---

## 🧪 Testing

```bash
# Run comprehensive tests
python test_api_logging.py
```

Tests verify:
- ✅ Request/response logging
- ✅ Performance metrics
- ✅ Error logging
- ✅ Request ID tracking
- ✅ Sensitive data sanitization

---

## 📚 More Information

- **Complete Guide**: [PRODUCTION_LOGGING.md](PRODUCTION_LOGGING.md)
- **Implementation Details**: [API_LOGGING_COMPLETE.md](API_LOGGING_COMPLETE.md)
- **Code**: [api_logger.py](api_logger.py)

---

## 💡 Key Features

✅ **Zero Config Required** - Works out of the box
✅ **Automatic** - No code changes needed
✅ **Request Tracking** - Unique IDs in `X-Request-ID` header
✅ **Performance Monitoring** - Response time tracking
✅ **Secure** - Sensitive data automatically sanitized
✅ **Production-Ready** - Log rotation, multiple formats

---

**That's all you need to know to get started!**

For advanced usage, see [PRODUCTION_LOGGING.md](PRODUCTION_LOGGING.md).
