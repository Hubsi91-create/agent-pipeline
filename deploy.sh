#!/bin/bash

###############################################################################
# Music Video Production System - Google Cloud Run Deployment Script
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-music-video-production}"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
MIN_INSTANCES="${MIN_INSTANCES:-0}"
MAX_INSTANCES="${MAX_INSTANCES:-10}"
MEMORY="${MEMORY:-1Gi}"
CPU="${CPU:-2}"
TIMEOUT="${TIMEOUT:-300}"
PORT="${PORT:-8080}"

# Environment Variables for Cloud Run
ENV_VARS="ENVIRONMENT=production"

###############################################################################
# Helper Functions
###############################################################################

print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_requirements() {
    print_header "Checking Requirements"

    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI is not installed"
        echo "Install from: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    print_success "gcloud CLI found"

    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        echo "Install from: https://docs.docker.com/get-docker/"
        exit 1
    fi
    print_success "Docker found"

    # Check if backend directory exists
    if [ ! -d "backend" ]; then
        print_error "backend/ directory not found"
        exit 1
    fi
    print_success "backend/ directory found"

    # Check if Dockerfile exists
    if [ ! -f "backend/Dockerfile" ]; then
        print_error "backend/Dockerfile not found"
        exit 1
    fi
    print_success "Dockerfile found"
}

check_gcloud_auth() {
    print_header "Checking GCP Authentication"

    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
        print_warning "Not authenticated with gcloud"
        print_info "Running: gcloud auth login"
        gcloud auth login
    fi

    ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
    print_success "Authenticated as: $ACTIVE_ACCOUNT"
}

set_gcp_project() {
    print_header "Setting GCP Project"

    # Check if PROJECT_ID is set
    if [ "$PROJECT_ID" == "your-project-id" ]; then
        print_error "GCP_PROJECT_ID not set"
        echo ""
        echo "Set your project ID:"
        echo "  export GCP_PROJECT_ID=your-actual-project-id"
        echo "Or run:"
        echo "  ./deploy.sh --project YOUR_PROJECT_ID"
        exit 1
    fi

    print_info "Setting project to: $PROJECT_ID"
    gcloud config set project "$PROJECT_ID"
    print_success "Project set to: $PROJECT_ID"
}

enable_apis() {
    print_header "Enabling Required APIs"

    print_info "Enabling Cloud Run API..."
    gcloud services enable run.googleapis.com --project="$PROJECT_ID" 2>/dev/null || true

    print_info "Enabling Container Registry API..."
    gcloud services enable containerregistry.googleapis.com --project="$PROJECT_ID" 2>/dev/null || true

    print_info "Enabling Cloud Build API..."
    gcloud services enable cloudbuild.googleapis.com --project="$PROJECT_ID" 2>/dev/null || true

    print_success "APIs enabled"
}

build_docker_image() {
    print_header "Building Docker Image"

    print_info "Building image: $IMAGE_NAME"
    print_info "Using backend/Dockerfile"

    docker build -t "$IMAGE_NAME" -f backend/Dockerfile backend/

    print_success "Docker image built successfully"
}

configure_docker_auth() {
    print_header "Configuring Docker Authentication"

    print_info "Configuring Docker to use gcloud credentials"
    gcloud auth configure-docker --quiet

    print_success "Docker authentication configured"
}

push_docker_image() {
    print_header "Pushing Docker Image to GCR"

    print_info "Pushing image: $IMAGE_NAME"
    docker push "$IMAGE_NAME"

    print_success "Docker image pushed to GCR"
}

check_secrets() {
    print_header "Checking Secrets Configuration"

    print_warning "IMPORTANT: Make sure to configure secrets in Cloud Console:"
    echo ""
    echo "Required Secrets:"
    echo "  1. GEMINI_API_KEY - Your Google Gemini API key"
    echo "  2. GOOGLE_SHEET_ID - Your Google Spreadsheet ID"
    echo "  3. GOOGLE_APPLICATION_CREDENTIALS - Service account JSON (as secret)"
    echo ""
    echo "To add secrets:"
    echo "  1. Go to Cloud Console > Secret Manager"
    echo "  2. Create secrets with the names above"
    echo "  3. Grant Cloud Run service account access to secrets"
    echo ""

    read -p "Have you configured the secrets? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Please configure secrets before deploying"
        print_info "Continuing anyway... (you can configure later)"
    fi
}

deploy_to_cloud_run() {
    print_header "Deploying to Cloud Run"

    print_info "Deploying service: $SERVICE_NAME"
    print_info "Region: $REGION"
    print_info "Image: $IMAGE_NAME"
    print_info "Min instances: $MIN_INSTANCES"
    print_info "Max instances: $MAX_INSTANCES"
    print_info "Memory: $MEMORY"
    print_info "CPU: $CPU"
    print_info "Timeout: ${TIMEOUT}s"
    print_info "Port: $PORT (Streamlit frontend)"

    gcloud run deploy "$SERVICE_NAME" \
        --image="$IMAGE_NAME" \
        --platform=managed \
        --region="$REGION" \
        --allow-unauthenticated \
        --min-instances="$MIN_INSTANCES" \
        --max-instances="$MAX_INSTANCES" \
        --memory="$MEMORY" \
        --cpu="$CPU" \
        --timeout="$TIMEOUT" \
        --port="$PORT" \
        --set-env-vars="$ENV_VARS" \
        --project="$PROJECT_ID"

    print_success "Deployment completed!"
}

get_service_url() {
    print_header "Service Information"

    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
        --platform=managed \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --format="value(status.url)")

    echo ""
    print_success "Service deployed successfully!"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}Service URL:${NC} $SERVICE_URL"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🎬 Streamlit Frontend (Main UI):"
    echo "  Web Interface: $SERVICE_URL"
    echo ""
    echo "📡 FastAPI Backend (Port 8000 internal):"
    echo "  Health Check:  $SERVICE_URL/api/v1/health"
    echo "  API Docs:      $SERVICE_URL/docs"
    echo "  OpenAPI:       $SERVICE_URL/openapi.json"
    echo ""
    echo "Test the deployment:"
    echo "  # Open in browser:"
    echo "  open $SERVICE_URL"
    echo ""
    echo "  # Test backend health:"
    echo "  curl $SERVICE_URL/api/v1/health"
    echo ""
}

show_next_steps() {
    print_header "Next Steps"

    echo "1. Configure Secrets (if not done):"
    echo "   - Go to Cloud Console > Secret Manager"
    echo "   - Add: GEMINI_API_KEY, GOOGLE_SHEET_ID"
    echo "   - Update Cloud Run service to use secrets"
    echo ""
    echo "2. Test the API:"
    echo "   curl $SERVICE_URL/api/v1/health"
    echo ""
    echo "3. Create a project:"
    echo "   curl -X POST $SERVICE_URL/api/v1/projects \\"
    echo "     -H 'Content-Type: application/json' \\"
    echo "     -d '{\"name\":\"Test\",\"artist\":\"Artist\",\"song_title\":\"Song\"}'"
    echo ""
    echo "4. Monitor logs:"
    echo "   gcloud run logs tail $SERVICE_NAME --region=$REGION"
    echo ""
    echo "5. View in Cloud Console:"
    echo "   https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME"
    echo ""
}

cleanup_local_images() {
    print_header "Cleanup (Optional)"

    read -p "Remove local Docker image to save space? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Removing local image: $IMAGE_NAME"
        docker rmi "$IMAGE_NAME" 2>/dev/null || true
        print_success "Local image removed"
    fi
}

###############################################################################
# Parse Command Line Arguments
###############################################################################

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --project)
                PROJECT_ID="$2"
                shift 2
                ;;
            --region)
                REGION="$2"
                shift 2
                ;;
            --service-name)
                SERVICE_NAME="$2"
                shift 2
                ;;
            --memory)
                MEMORY="$2"
                shift 2
                ;;
            --cpu)
                CPU="$2"
                shift 2
                ;;
            --min-instances)
                MIN_INSTANCES="$2"
                shift 2
                ;;
            --max-instances)
                MAX_INSTANCES="$2"
                shift 2
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

show_help() {
    cat << EOF
Music Video Production System - Cloud Run Deployment

Usage: ./deploy.sh [OPTIONS]

Options:
  --project PROJECT_ID        GCP Project ID (required)
  --region REGION            GCP Region (default: us-central1)
  --service-name NAME        Service name (default: music-video-production)
  --memory MEMORY            Memory allocation (default: 1Gi - dual service needs more RAM)
  --cpu CPU                  CPU allocation (default: 2 - runs FastAPI + Streamlit)
  --min-instances NUM        Minimum instances (default: 0)
  --max-instances NUM        Maximum instances (default: 10)
  --help                     Show this help message

Environment Variables:
  GCP_PROJECT_ID            Alternative to --project
  GCP_REGION                Alternative to --region
  SERVICE_NAME              Alternative to --service-name

Examples:
  # Basic deployment
  ./deploy.sh --project my-project-id

  # Custom configuration
  ./deploy.sh --project my-project --region europe-west1 --memory 1Gi --cpu 2

  # Using environment variables
  export GCP_PROJECT_ID=my-project
  ./deploy.sh

EOF
}

###############################################################################
# Main Execution
###############################################################################

main() {
    clear

    echo -e "${BLUE}"
    cat << "EOF"
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║       Music Video Production System                          ║
    ║       Google Cloud Run Deployment                            ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"

    # Parse arguments
    parse_args "$@"

    # Run deployment steps
    check_requirements
    check_gcloud_auth
    set_gcp_project
    enable_apis
    configure_docker_auth
    build_docker_image
    push_docker_image
    check_secrets
    deploy_to_cloud_run
    get_service_url
    show_next_steps
    cleanup_local_images

    echo ""
    print_success "🎬 Deployment Complete!"
    echo ""
}

# Run main function
main "$@"
