"""
FastAPI Endpoints for Music Video Production System
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
from app.models.data_models import (
    Project,
    ProjectCreate,
    StoryboardResponse,
    OrchestrationRequest,
    AudioUploadRequest,
    QCRequest,
    APIResponse,
    SunoPromptRequest,
    SunoPromptResponse,
    FewShotLearningStats
)
from app.agents.agent_1_project_manager.service import agent1_service
from app.agents.agent_2_qc.service import agent2_service
from app.agents.agent_3_audio_analyzer.service import agent3_service
from app.agents.agent_4_scene_breakdown.service import agent4_service
from app.agents.agent_5_style_anchors.service import agent5_service
from app.agents.agent_6_veo_prompter.service import agent6_service
from app.agents.agent_7_runway_prompter.service import agent7_service
from app.agents.agent_8_refiner.service import agent8_service
from app.agents.suno_prompt_generator.service import suno_generator_service
from app.utils.logger import setup_logger

logger = setup_logger("API")
router = APIRouter()


# ==================== Project Management ====================

@router.post("/projects", response_model=APIResponse)
async def create_project(project_data: ProjectCreate):
    """Create a new music video project"""
    try:
        project = await agent1_service.create_project(project_data)
        return APIResponse(
            success=True,
            message="Project created successfully",
            data=project.model_dump()
        )
    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}", response_model=APIResponse)
async def get_project(project_id: str):
    """Get project by ID"""
    project = await agent1_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return APIResponse(
        success=True,
        message="Project retrieved",
        data=project.model_dump()
    )


# ==================== Audio Analysis ====================

@router.post("/agent3/upload", response_model=APIResponse)
async def upload_audio(request: AudioUploadRequest):
    """
    Upload audio file for analysis (simulated)
    In production, this would handle actual file upload
    """
    try:
        # Analyze audio
        analysis = await agent3_service.analyze_audio(
            request.project_id,
            request.filename
        )

        # Update project status
        await agent1_service.update_project_status(
            request.project_id,
            "ANALYZING",
            "Agent 3",
            20.0
        )

        return APIResponse(
            success=True,
            message="Audio analyzed successfully",
            data=analysis.model_dump()
        )
    except Exception as e:
        logger.error(f"Audio analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Orchestration ====================

@router.post("/orchestration/plan-video", response_model=APIResponse)
async def plan_video(
    request: OrchestrationRequest,
    background_tasks: BackgroundTasks
):
    """
    Orchestrate the complete video planning pipeline
    Triggers: Agent 4 -> Agent 5 -> Agent 6/7
    """
    try:
        # Get project
        project = await agent1_service.get_project(request.project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Start orchestration in background
        background_tasks.add_task(
            run_orchestration,
            request.project_id,
            project.artist,
            project.song_title,
            request.generate_for_veo,
            request.generate_for_runway
        )

        return APIResponse(
            success=True,
            message="Video planning started",
            data={"project_id": request.project_id, "status": "PROCESSING"}
        )
    except Exception as e:
        logger.error(f"Orchestration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def run_orchestration(
    project_id: str,
    artist: str,
    song_title: str,
    generate_veo: bool,
    generate_runway: bool
):
    """Background task for video planning orchestration"""
    try:
        logger.info(f"Starting orchestration for project {project_id}")

        # Step 1: Get audio analysis
        await agent1_service.update_project_status(project_id, "PLANNING", "Agent 4", 30.0)
        audio_analysis = await agent3_service.get_analysis(project_id)
        if not audio_analysis:
            logger.error("No audio analysis found")
            return

        # Step 2: Create scene breakdown
        scenes = await agent4_service.create_scene_breakdown(project_id, audio_analysis)
        await agent1_service.update_project_status(project_id, "PLANNING", "Agent 5", 50.0)

        # Step 3: Create style anchors
        style_anchors = await agent5_service.create_style_anchors(
            project_id,
            scenes,
            artist,
            song_title
        )
        style_anchor = style_anchors[0] if style_anchors else None

        if not style_anchor:
            logger.error("No style anchor created")
            return

        # Step 4: Generate prompts
        await agent1_service.update_project_status(project_id, "GENERATING", "Agent 6/7", 70.0)

        for scene in scenes:
            if generate_veo:
                await agent6_service.generate_prompt(scene, style_anchor)
            if generate_runway:
                await agent7_service.generate_prompt(scene, style_anchor)

        # Complete
        await agent1_service.update_project_status(project_id, "QC", "Agent 2", 90.0)

        logger.info(f"Orchestration complete for project {project_id}")

    except Exception as e:
        logger.error(f"Orchestration error: {e}")
        await agent1_service.update_project_status(project_id, "ERROR", None, 0.0)


# ==================== Storyboard ====================

@router.get("/storyboard/{project_id}", response_model=StoryboardResponse)
async def get_storyboard(project_id: str):
    """
    Get complete storyboard data for frontend
    Aggregates all data from different agents
    """
    try:
        # Get project
        project = await agent1_service.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Get audio analysis
        audio_analysis = await agent3_service.get_analysis(project_id)

        # Get scenes
        scenes = await agent4_service.get_scenes_for_project(project_id)

        # Get style anchors
        style_anchors = await agent5_service.get_style_anchors_for_project(project_id)

        # Get prompts (grouped by scene)
        prompts_dict = {}
        for scene in scenes:
            veo_prompts = await agent6_service.get_prompts_for_scene(scene.id)
            runway_prompts = await agent7_service.get_prompts_for_scene(scene.id)
            prompts_dict[scene.id] = veo_prompts + runway_prompts

        # Get QC feedback (simplified - in production, filter by project)
        qc_feedback = []  # Would query from sheets

        # Build storyboard response
        storyboard = StoryboardResponse(
            project=project,
            audio_analysis=audio_analysis,
            scenes=scenes,
            style_anchors=style_anchors,
            prompts=prompts_dict,
            qc_feedback=qc_feedback
        )

        return storyboard

    except Exception as e:
        logger.error(f"Failed to get storyboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== QC ====================

@router.post("/qc/review", response_model=APIResponse)
async def submit_qc_review(qc_request: QCRequest):
    """Submit content for QC review"""
    try:
        qc_feedback = await agent2_service.review_content(qc_request)

        return APIResponse(
            success=True,
            message="QC review completed",
            data=qc_feedback.model_dump()
        )
    except Exception as e:
        logger.error(f"QC review failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Health Check ====================

@router.get("/health")
async def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "service": "Music Video Production System",
        "version": "1.0.0"
    }


# ==================== Suno Prompt Generation (Few-Shot Learning) ====================

@router.post("/suno/generate", response_model=APIResponse)
async def generate_suno_prompt(request: SunoPromptRequest):
    """
    Generate Suno v5 prompt using Dynamic Few-Shot Learning

    Process:
    1. Fetches 3-5 best practice examples from ApprovedBestPractices
    2. Injects them into Gemini prompt (in-context learning)
    3. Generates new prompt following learned patterns
    4. Returns prompt (status: PENDING_QC)
    """
    try:
        prompt_response = await suno_generator_service.generate_prompt(request)

        return APIResponse(
            success=True,
            message=f"Suno prompt generated using {prompt_response.few_shot_examples_used} examples",
            data=prompt_response.model_dump()
        )
    except Exception as e:
        logger.error(f"Failed to generate Suno prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suno/{prompt_id}/qc", response_model=APIResponse)
async def qc_suno_prompt(prompt_id: str, prompt_data: SunoPromptResponse):
    """
    QC review for Suno prompt with auto-learning

    Auto-Learning Mechanism:
    - If prompt scores >= 7.0, it's automatically added to ApprovedBestPractices
    - This makes it available as a Few-Shot example for future generations
    - The system "learns" and improves with every high-quality prompt
    """
    try:
        qc_feedback = await agent2_service.review_suno_prompt(
            prompt_data,
            auto_add_to_best_practices=True  # Enable auto-learning
        )

        return APIResponse(
            success=True,
            message=f"QC complete: {qc_feedback.qc_status}",
            data=qc_feedback.model_dump()
        )
    except Exception as e:
        logger.error(f"Suno QC failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suno/learning-stats", response_model=FewShotLearningStats)
async def get_learning_stats():
    """
    Get Few-Shot Learning statistics

    Shows:
    - Total number of approved examples in knowledge base
    - Average quality score
    - Distribution by genre
    - Recent additions (last 24h)
    - Top performing genres

    This shows how the system is "learning" over time
    """
    try:
        stats = await suno_generator_service.get_learning_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get learning stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
