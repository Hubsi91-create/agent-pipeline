"""
Music Video Production System - Main FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import router as api_router
from app.utils.logger import setup_logger
import os

logger = setup_logger("Main")

# Create FastAPI app
app = FastAPI(
    title="Music Video Production System",
    description="AI-powered music video production with 8-agent pipeline",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1", tags=["api"])


@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info("=" * 60)
    logger.info("Music Video Production System Starting")
    logger.info("=" * 60)
    logger.info("Environment: %s", os.getenv("ENVIRONMENT", "development"))
    logger.info("Agents: 8 (Project Manager, QC, Audio, Scenes, Style, Veo, Runway, Refiner)")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    logger.info("Music Video Production System Shutting Down")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Music Video Production System",
        "version": "1.0.0",
        "status": "operational",
        "agents": [
            "Agent 1: Project Manager",
            "Agent 2: QC Agent",
            "Agent 3: Audio Analyzer",
            "Agent 4: Scene Breakdown",
            "Agent 5: Style Anchors",
            "Agent 6: Veo Prompter",
            "Agent 7: Runway Prompter",
            "Agent 8: Prompt Refiner"
        ],
        "endpoints": {
            "health": "/api/v1/health",
            "create_project": "POST /api/v1/projects",
            "upload_audio": "POST /api/v1/agent3/upload",
            "plan_video": "POST /api/v1/orchestration/plan-video",
            "get_storyboard": "GET /api/v1/storyboard/{project_id}",
            "qc_review": "POST /api/v1/qc/review"
        }
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
