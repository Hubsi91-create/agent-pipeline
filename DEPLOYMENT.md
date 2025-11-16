# Deployment Guide - Music Video Production System

Complete guide for deploying the Music Video Production System to Google Cloud Run.

## 📋 Prerequisites

### Required Tools
- **gcloud CLI** - [Install Guide](https://cloud.google.com/sdk/docs/install)
- **Docker** - [Install Guide](https://docs.docker.com/get-docker/)
- **Google Cloud Project** with billing enabled

### Required GCP APIs
- Cloud Run API
- Container Registry API
- Cloud Build API
- Secret Manager API (for credentials)

## 🚀 Quick Deployment

### 1. Set Your Project ID
```bash
export GCP_PROJECT_ID=your-actual-project-id
```

### 2. Run Deployment Script
```bash
./deploy.sh --project $GCP_PROJECT_ID
```

That's it! The script will:
- ✅ Check prerequisites
- ✅ Authenticate with GCP
- ✅ Enable required APIs
- ✅ Build Docker image
- ✅ Push to Container Registry
- ✅ Deploy to Cloud Run
- ✅ Display service URL

## 🔧 Advanced Deployment

### Custom Configuration
```bash
./deploy.sh \
  --project my-project-id \
  --region europe-west1 \
  --service-name my-video-service \
  --memory 1Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 20
```

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `--project` | (required) | GCP Project ID |
| `--region` | `us-central1` | GCP Region |
| `--service-name` | `music-video-production` | Cloud Run service name |
| `--memory` | `512Mi` | Memory allocation |
| `--cpu` | `1` | CPU allocation |
| `--min-instances` | `0` | Minimum instances (0 = scale to zero) |
| `--max-instances` | `10` | Maximum instances |

### Environment Variables
You can also use environment variables:
```bash
export GCP_PROJECT_ID=my-project
export GCP_REGION=us-central1
export SERVICE_NAME=my-service
./deploy.sh
```

## 🔐 Secrets Configuration

### Required Secrets

The system needs these secrets to function:

1. **GEMINI_API_KEY** - Google Gemini API key
2. **GOOGLE_SHEET_ID** - Google Spreadsheet ID
3. **GOOGLE_APPLICATION_CREDENTIALS** - Service account JSON

### Create Secrets in Secret Manager

#### 1. Enable Secret Manager API
```bash
gcloud services enable secretmanager.googleapis.com
```

#### 2. Create Secrets
```bash
# Gemini API Key
echo -n "your-gemini-api-key" | \
  gcloud secrets create GEMINI_API_KEY \
  --data-file=- \
  --replication-policy=automatic

# Google Sheet ID
echo -n "your-spreadsheet-id" | \
  gcloud secrets create GOOGLE_SHEET_ID \
  --data-file=- \
  --replication-policy=automatic

# Service Account Credentials
gcloud secrets create GOOGLE_APPLICATION_CREDENTIALS \
  --data-file=path/to/service-account.json \
  --replication-policy=automatic
```

#### 3. Grant Cloud Run Access to Secrets
```bash
# Get the Cloud Run service account
SERVICE_ACCOUNT=$(gcloud run services describe music-video-production \
  --region=us-central1 \
  --format='value(spec.template.spec.serviceAccountName)')

# Grant access to each secret
for SECRET in GEMINI_API_KEY GOOGLE_SHEET_ID GOOGLE_APPLICATION_CREDENTIALS; do
  gcloud secrets add-iam-policy-binding $SECRET \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor"
done
```

#### 4. Update Cloud Run to Use Secrets
```bash
gcloud run services update music-video-production \
  --region=us-central1 \
  --update-secrets=GEMINI_API_KEY=GEMINI_API_KEY:latest \
  --update-secrets=GOOGLE_SHEET_ID=GOOGLE_SHEET_ID:latest \
  --update-secrets=GOOGLE_APPLICATION_CREDENTIALS=GOOGLE_APPLICATION_CREDENTIALS:latest
```

## 📊 Google Sheets Setup

### 1. Create Google Spreadsheet
1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet
3. Copy the Spreadsheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/edit
   ```

### 2. Create Service Account
```bash
# Create service account
gcloud iam service-accounts create music-video-sa \
  --display-name="Music Video Production Service Account"

# Download key
gcloud iam service-accounts keys create service-account-key.json \
  --iam-account=music-video-sa@${GCP_PROJECT_ID}.iam.gserviceaccount.com
```

### 3. Share Spreadsheet
1. Open your Google Spreadsheet
2. Click "Share"
3. Add the service account email:
   ```
   music-video-sa@YOUR-PROJECT-ID.iam.gserviceaccount.com
   ```
4. Give it "Editor" access

## 🧪 Testing the Deployment

### 1. Health Check
```bash
SERVICE_URL=$(gcloud run services describe music-video-production \
  --region=us-central1 \
  --format='value(status.url)')

curl $SERVICE_URL/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Music Video Production System",
  "version": "1.0.0"
}
```

### 2. Create a Test Project
```bash
curl -X POST $SERVICE_URL/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Project",
    "artist": "Test Artist",
    "song_title": "Test Song"
  }'
```

### 3. View API Documentation
Visit: `$SERVICE_URL/docs`

## 📈 Monitoring & Logs

### View Logs
```bash
# Tail logs
gcloud run logs tail music-video-production --region=us-central1

# View recent logs
gcloud run logs read music-video-production \
  --region=us-central1 \
  --limit=50
```

### View Metrics
```bash
# Open Cloud Console
gcloud run services describe music-video-production \
  --region=us-central1 \
  --format='value(status.url)'
```

Then visit Cloud Console:
```
https://console.cloud.google.com/run/detail/us-central1/music-video-production
```

## 🔄 Updating the Service

### Redeploy After Code Changes
```bash
# Simply run the deploy script again
./deploy.sh --project $GCP_PROJECT_ID
```

The script will:
1. Rebuild the Docker image
2. Push new version to GCR
3. Update Cloud Run service

### Update Environment Variables
```bash
gcloud run services update music-video-production \
  --region=us-central1 \
  --set-env-vars="ENVIRONMENT=production,LOG_LEVEL=INFO"
```

### Update Resource Allocation
```bash
gcloud run services update music-video-production \
  --region=us-central1 \
  --memory=1Gi \
  --cpu=2
```

## 🔒 Security Best Practices

### 1. Use Secrets for Sensitive Data
- ✅ NEVER commit API keys to Git
- ✅ Always use Secret Manager
- ✅ Rotate secrets regularly

### 2. Restrict Access
```bash
# Make service require authentication
gcloud run services update music-video-production \
  --region=us-central1 \
  --no-allow-unauthenticated
```

### 3. Set Up VPC Connector (Optional)
For private Google Sheets access:
```bash
gcloud compute networks vpc-access connectors create music-video-connector \
  --region=us-central1 \
  --range=10.8.0.0/28

gcloud run services update music-video-production \
  --region=us-central1 \
  --vpc-connector=music-video-connector
```

## 💰 Cost Optimization

### Scale to Zero
```bash
# Set min instances to 0 (default)
gcloud run services update music-video-production \
  --region=us-central1 \
  --min-instances=0
```

### Set Request Limits
```bash
# Limit concurrent requests per instance
gcloud run services update music-video-production \
  --region=us-central1 \
  --concurrency=80
```

### Set Budget Alerts
```bash
# Create budget in Cloud Console
# Billing > Budgets & alerts
```

## 🐛 Troubleshooting

### Deployment Fails
```bash
# Check service status
gcloud run services describe music-video-production \
  --region=us-central1

# Check recent logs
gcloud run logs read music-video-production \
  --region=us-central1 \
  --limit=100
```

### Secrets Not Working
```bash
# Verify secrets exist
gcloud secrets list

# Check IAM permissions
gcloud secrets get-iam-policy GEMINI_API_KEY
```

### Container Won't Start
```bash
# Test Docker image locally
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=your-key \
  -e GOOGLE_SHEET_ID=your-sheet-id \
  gcr.io/YOUR-PROJECT/music-video-production
```

## 📞 Support

- **Cloud Run Docs**: https://cloud.google.com/run/docs
- **gcloud CLI Reference**: https://cloud.google.com/sdk/gcloud/reference/run
- **Secret Manager Docs**: https://cloud.google.com/secret-manager/docs

## ✅ Deployment Checklist

- [ ] GCP Project created with billing enabled
- [ ] gcloud CLI installed and authenticated
- [ ] Docker installed
- [ ] Service account created
- [ ] Google Spreadsheet created and shared
- [ ] Secrets created in Secret Manager
- [ ] `GCP_PROJECT_ID` environment variable set
- [ ] Deployment script executed successfully
- [ ] Health check passes
- [ ] API documentation accessible
- [ ] Test project creation works

---

**🎬 Happy Deploying!**
