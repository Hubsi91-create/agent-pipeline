# Music Agents v2 - Setup Guide

Complete guide for setting up, testing, and deploying the Music Agents v2 application to Google Cloud Run.

---

## Table of Contents

1. [Google Cloud Infrastructure Setup](#1-google-cloud-infrastructure-setup)
2. [Local Development & Testing](#2-local-development--testing)
3. [Production Deployment to Cloud Run](#3-production-deployment-to-cloud-run)
4. [Troubleshooting](#4-troubleshooting)

---

## 1. Google Cloud Infrastructure Setup

Before running the application, you need to configure your Google Cloud environment.

### 1.1. Create Google Spreadsheet (Database)

1. **Create a new Google Spreadsheet**
   - Go to [Google Sheets](https://sheets.google.com)
   - Create a new blank spreadsheet
   - Name it: `Music Agents v2 - DB`

2. **Copy the Sheet ID**
   - From the URL: `https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit`
   - Save this ID - you'll need it later

### 1.2. Enable Google Cloud APIs

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select project: `music-agents-prod`
3. Navigate to **APIs & Services > Library**
4. Enable the following APIs:
   - **Google Sheets API**
   - **Vertex AI API**

### 1.3. Create Service Account

1. Go to **IAM & Admin > Service Accounts**
2. Click **Create Service Account**
   - Name: `sa-music-agents-v2`
   - Description: `Service account for Music Agents v2`
3. Click **Create and Continue**
4. Grant the following roles:
   - **Vertex AI User** (for Gemini access)
5. Click **Done**
6. **Note the service account email** (e.g., `sa-music-agents-v2@music-agents-prod.iam.gserviceaccount.com`)

### 1.4. Grant Spreadsheet Access (CRITICAL)

1. Open your Google Spreadsheet from step 1.1
2. Click **Share** button (top right)
3. Add the service account email from step 1.3
4. Grant **Editor** permissions
5. Click **Send**

**Without this step, the application cannot access the spreadsheet!**

---

## 2. Local Development & Testing

### 2.1. Download Service Account Key (Local Testing Only)

1. Go to **IAM & Admin > Service Accounts**
2. Click on your service account (`sa-music-agents-v2`)
3. Go to **Keys** tab
4. Click **Add Key > Create new key**
5. Select **JSON** format
6. Download the key file
7. **Keep this file secure - it contains credentials!**

### 2.2. Setup Local Environment

```bash
# Navigate to backend directory
cd backend/

# Optional: Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from template
cp .env.example .env
```

### 2.3. Configure Environment Variables

Edit the `.env` file:

```bash
# Google Cloud Configuration
GOOGLE_PROJECT_ID=music-agents-prod
GOOGLE_SHEET_ID=your_sheet_id_from_step_1_1

# Service Account JSON (entire JSON as single line)
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"music-agents-prod",...}

# Vertex AI Configuration
VERTEX_AI_LOCATION=europe-west3
GEMINI_MODEL=gemini-1.5-pro-002

# Application Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
```

**Important:** For `GOOGLE_SERVICE_ACCOUNT_JSON`, copy the **entire content** of your downloaded JSON key file as a single line.

### 2.4. Start the Application

```bash
# Make sure you're in the backend/ directory
cd backend/

# Start with auto-reload (development mode)
uvicorn main:app --reload --port 8080
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8080
INFO:     Application startup complete.
```

### 2.5. Test the Application

#### Option 1: Interactive API Documentation (Swagger UI)

1. Open browser: http://localhost:8080/docs
2. You'll see the FastAPI interactive documentation
3. Test endpoints:
   - **GET** `/health` - Health check
   - **POST** `/api/v1/orchestration/run-phase-a` - Run Phase A pipeline

#### Option 2: cURL Commands

```bash
# Health check
curl http://localhost:8080/health

# Run Phase A
curl -X POST http://localhost:8080/api/v1/orchestration/run-phase-a \
  -H "Content-Type: application/json" \
  -d '{"context": "music production and marketing"}'
```

#### Expected Behavior

When you run Phase A, the application will:

1. **Create worksheets** in your Google Spreadsheet (if they don't exist):
   - `A1_Trends_DB`
   - `A2_GeneratedPrompts_DB`
   - `QC_Results_DB`
   - `ApprovedBestPractices`

2. **Analyze trends** using Gemini AI

3. **Generate creative prompts** for each trend

4. **Perform quality control** on prompts

5. **Store results** in the spreadsheet

Check your Google Spreadsheet - it should now contain data!

---

## 3. Production Deployment to Cloud Run

### 3.1. Prerequisites

1. Install [Google Cloud SDK (gcloud)](https://cloud.google.com/sdk/docs/install)
2. Authenticate:
   ```bash
   gcloud auth login
   gcloud config set project music-agents-prod
   ```

### 3.2. Deploy to Cloud Run

From the project root directory:

```bash
# Make deploy script executable (if not already)
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

The script will:
- Build the Docker image using Cloud Build
- Push to Google Container Registry
- Deploy to Cloud Run
- Output the service URL

### 3.3. Configure Environment Variables in Cloud Run

After deployment, set the required environment variables:

```bash
gcloud run services update music-agents-v2-backend \
  --region europe-west3 \
  --set-env-vars GOOGLE_SHEET_ID=your_sheet_id_here,GOOGLE_PROJECT_ID=music-agents-prod,VERTEX_AI_LOCATION=europe-west3,GEMINI_MODEL=gemini-1.5-pro-002
```

**Note:** For production, the service account authentication is handled automatically by Cloud Run's runtime service account. You don't need to set `GOOGLE_SERVICE_ACCOUNT_JSON` in production.

### 3.4. Grant Runtime Service Account Permissions

1. Go to **Cloud Run > music-agents-v2-backend > Edit & Deploy New Revision**
2. Go to **Security** tab
3. Note the **Service Account** (usually `PROJECT_NUMBER-compute@developer.gserviceaccount.com`)
4. Grant this service account:
   - **Vertex AI User** role (if not already granted)
   - **Editor** access to your Google Spreadsheet (same as step 1.4)

### 3.5. Test Production Deployment

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe music-agents-v2-backend --region europe-west3 --format 'value(status.url)')

# Health check
curl $SERVICE_URL/health

# Run Phase A
curl -X POST $SERVICE_URL/api/v1/orchestration/run-phase-a \
  -H "Content-Type: application/json" \
  -d '{"context": "music production and marketing"}'
```

---

## 4. Troubleshooting

### Common Issues

#### 1. "Failed to connect to Google Sheets"

**Cause:** Service account doesn't have access to the spreadsheet.

**Solution:**
- Make sure you shared the spreadsheet with the service account email (step 1.4)
- Grant **Editor** permissions

#### 2. "Vertex AI API not enabled"

**Cause:** Vertex AI API is not enabled for the project.

**Solution:**
```bash
gcloud services enable aiplatform.googleapis.com --project=music-agents-prod
```

#### 3. "Invalid service account JSON"

**Cause:** The JSON is not properly formatted as a single line.

**Solution:**
- Copy the entire JSON content
- Ensure it's a single line (no newlines)
- Must start with `{` and end with `}`

#### 4. Cloud Run deployment fails

**Cause:** Various reasons (permissions, quota, etc.)

**Solution:**
- Check Cloud Build logs: `gcloud builds list --limit=5`
- View logs: `gcloud builds log BUILD_ID`
- Ensure billing is enabled
- Check IAM permissions

#### 5. "Module not found" errors locally

**Cause:** Dependencies not installed or wrong Python version.

**Solution:**
```bash
# Ensure Python 3.11+
python --version

# Reinstall dependencies
pip install -r requirements.txt
```

### Viewing Logs

**Local:**
- Logs appear in terminal where uvicorn is running

**Production (Cloud Run):**
```bash
# View recent logs
gcloud run services logs read music-agents-v2-backend --region europe-west3 --limit=50

# Tail logs (live)
gcloud run services logs tail music-agents-v2-backend --region europe-west3
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Music Agents v2                        │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   FastAPI    │──────│ Orchestrator │──────│  Vertex AI   │
│   Backend    │      │   Service    │      │  (Gemini)    │
└──────┬───────┘      └──────┬───────┘      └──────────────┘
       │                     │
       │                     │
       ▼                     ▼
┌──────────────────────────────────────┐
│        Google Sheets Service         │
│  (Database - Spreadsheet Storage)    │
└──────────────────────────────────────┘

Phase A Pipeline:
  A1: Trend Analysis (Gemini)
    ▼
  A2: Prompt Generation (Gemini)
    ▼
  QC: Quality Control (Gemini)
    ▼
  Store: Approved Best Practices (Sheets)
```

---

## Next Steps

1. **Extend Phase B:** Implement Phase B pipeline for advanced operations
2. **Add Authentication:** Implement API key or OAuth authentication
3. **Monitoring:** Set up Cloud Monitoring and alerting
4. **CI/CD:** Automate deployment with GitHub Actions or Cloud Build triggers
5. **Scaling:** Adjust Cloud Run settings based on usage patterns

---

## Support

For issues or questions:
- Check logs (local or Cloud Run)
- Review error messages
- Verify all configuration steps are completed
- Ensure APIs are enabled and service account has proper permissions

---

**Happy Building! 🎵🤖**
