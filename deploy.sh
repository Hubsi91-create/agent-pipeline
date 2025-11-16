#!/bin/bash

# Music Agents v2 - Cloud Run Deployment Script
# This script builds and deploys the application to Google Cloud Run

set -e  # Exit immediately if a command exits with a non-zero status

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="music-agents-prod"
REGION="europe-west3"
SERVICE_NAME="music-agents-v2-backend"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Music Agents v2 - Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Verify we're in the right directory
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}Error: Dockerfile not found. Please run this script from the project root.${NC}"
    exit 1
fi

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed.${NC}"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Verify project ID
echo -e "${YELLOW}Verifying Google Cloud project...${NC}"
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ "$CURRENT_PROJECT" != "$PROJECT_ID" ]; then
    echo -e "${YELLOW}Switching to project: $PROJECT_ID${NC}"
    gcloud config set project $PROJECT_ID
fi

echo -e "${GREEN}✓ Project ID: $PROJECT_ID${NC}"
echo ""

# Build and push with Cloud Build
echo -e "${YELLOW}Building and pushing Docker image...${NC}"
echo "Image: $IMAGE_NAME"
echo ""

gcloud builds submit --tag $IMAGE_NAME .

echo -e "${GREEN}✓ Image built and pushed successfully${NC}"
echo ""

# Deploy to Cloud Run
echo -e "${YELLOW}Deploying to Cloud Run...${NC}"
echo "Service: $SERVICE_NAME"
echo "Region: $REGION"
echo ""

gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --project $PROJECT_ID \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')

echo -e "${GREEN}Service URL: $SERVICE_URL${NC}"
echo ""
echo -e "${YELLOW}Important: Configure environment variables${NC}"
echo "You need to set the following environment variables in Cloud Run:"
echo "1. GOOGLE_SHEET_ID - Your Google Sheet ID"
echo "2. GOOGLE_SERVICE_ACCOUNT_JSON - Service account credentials (optional, uses runtime SA by default)"
echo ""
echo "To set environment variables, run:"
echo "  gcloud run services update $SERVICE_NAME \\"
echo "    --region $REGION \\"
echo "    --set-env-vars GOOGLE_SHEET_ID=your_sheet_id_here"
echo ""
echo -e "${YELLOW}Test your deployment:${NC}"
echo "  curl $SERVICE_URL/health"
echo "  curl -X POST $SERVICE_URL/api/v1/orchestration/run-phase-a"
echo ""
