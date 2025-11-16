"""
Main FastAPI Application for 11-Agent Music Video Production System
Phase A: Trend Detective, Suno Generator, QC Processor
Optimized for Google Cloud Run deployment
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.api.v1 import endpoints

# ============================================================
# LOGGING CONFIGURATION
# ============================================================

def setup_logging(log_level: str = "INFO"):
    """Configure logging for the application"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


# ============================================================
# APPLICATION LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    settings = get_settings()
    logger = logging.getLogger(__name__)

    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Google Project: {settings.GOOGLE_PROJECT_ID}")
    logger.info(f"Google Sheet ID: {settings.GOOGLE_SHEET_ID or 'NOT SET'}")

    # Validate critical configuration
    if not settings.GOOGLE_SHEET_ID:
        logger.warning("GOOGLE_SHEET_ID not set! Application may not function correctly.")

    yield

    # Shutdown
    logger.info("Shutting down application...")


# ============================================================
# CREATE FASTAPI APPLICATION
# ============================================================

settings = get_settings()
setup_logging(settings.LOG_LEVEL)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    # 11-Agent Music Video Production System (Phase A)

    Cloud-native AI pipeline for automated music video production.

    ## Phase A Components:
    - **Agent 1: Trend Detective** - Identifies viral music trends
    - **Agent 2: Suno Prompt Generator** - Creates optimized Suno prompts
    - **QC Processor** - Quality control with Few-Shot Learning feedback loop

    ## Architecture:
    - **Database**: Google Sheets
    - **LLM**: Google Gemini 2.5 Pro (Vertex AI)
    - **Deployment**: Google Cloud Run

    ## Workflow:
    1. Agent 1 generates trend reports → Stored in `A1_Trends_DB`
    2. Agent 2 processes NEW trends → Generates prompts → Stored in `A2_GeneratedPrompts_DB`
    3. QC evaluates PENDING_QC prompts → High scores added to `ApprovedBestPractices`
    4. Agent 2 uses best practices for Few-Shot Learning

    Use `/api/v1/orchestration/run-phase-a` to run the complete pipeline.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# ============================================================
# MIDDLEWARE
# ============================================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# INCLUDE ROUTERS
# ============================================================

app.include_router(
    endpoints.router,
    prefix=settings.API_V1_PREFIX,
)

# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "api": settings.API_V1_PREFIX,
        "phase": "A",
        "agents": [
            "Agent 1: Trend Detective",
            "Agent 2: Suno Prompt Generator",
            "QC Processor"
        ]
    }


# ============================================================
# ENTRY POINT FOR LOCAL DEVELOPMENT
# ============================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
