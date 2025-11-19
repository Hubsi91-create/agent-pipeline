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


# ==================== Trend Detection & Genre Variations ====================

@router.get("/trends/viral", response_model=APIResponse)
async def get_viral_trends():
    """
    Get current viral music trends from YouTube, TikTok, Spotify

    Returns:
    - List of 20 trending subgenres with platform and trend scores
    - Shuffled on each request for variety
    """
    try:
        trends = await agent1_service.get_current_viral_trends()

        return APIResponse(
            success=True,
            message=f"Retrieved {len(trends)} viral trends",
            data=trends
        )
    except Exception as e:
        logger.error(f"Failed to get viral trends: {e}")
        # FALLBACK: Return mock data instead of HTTP 500 (unbreakable endpoint)
        fallback_trends = [
            {"genre": "Drift Phonk", "platform": "TikTok", "trend_score": "🔥🔥🔥"},
            {"genre": "Sped-Up Nightcore", "platform": "YouTube", "trend_score": "🔥🔥🔥"},
            {"genre": "Liquid DnB", "platform": "Spotify", "trend_score": "🔥🔥"},
            {"genre": "Hypertechno", "platform": "TikTok", "trend_score": "🔥🔥🔥"},
            {"genre": "Slowed + Reverb", "platform": "YouTube", "trend_score": "🔥🔥"},
            {"genre": "Brazilian Phonk", "platform": "TikTok", "trend_score": "🔥🔥🔥"},
            {"genre": "Dark Ambient Trap", "platform": "Spotify", "trend_score": "🔥🔥"},
            {"genre": "Rage Beats", "platform": "TikTok", "trend_score": "🔥🔥"},
            {"genre": "Pluggnb", "platform": "Spotify", "trend_score": "🔥🔥"},
            {"genre": "Hyperpop 2.0", "platform": "TikTok", "trend_score": "🔥🔥🔥"}
        ]
        logger.warning("Using fallback trend data due to error")
        return APIResponse(
            success=True,
            message=f"Retrieved {len(fallback_trends)} viral trends (fallback mode)",
            data=fallback_trends
        )


@router.post("/genres/variations", response_model=APIResponse)
async def generate_genre_variations(request: Dict[str, Any]):
    """
    Generate subgenre variations for a given super genre

    Args:
    - super_genre: Main genre (e.g., "Electronic", "Hip-Hop")
    - num_variations: Number of variations to generate (default: 20)

    Returns:
    - List of subgenres with descriptions
    - Uses AI to generate real, specific subgenre names
    """
    try:
        super_genre = request.get("super_genre")
        num_variations = request.get("num_variations", 20)

        if not super_genre:
            raise HTTPException(status_code=400, detail="super_genre is required")

        variations = await agent1_service.generate_genre_variations(
            super_genre,
            num_variations
        )

        return APIResponse(
            success=True,
            message=f"Generated {len(variations)} {super_genre} variations",
            data=variations
        )
    except HTTPException:
        # Re-raise validation errors (400)
        raise
    except Exception as e:
        logger.error(f"Failed to generate genre variations: {e}")
        # FALLBACK: Return generic variations instead of HTTP 500
        fallback_variations = []
        for i in range(min(num_variations, 10)):
            fallback_variations.append({
                "subgenre": f"{super_genre} Style {i+1}",
                "description": f"Variation {i+1} of {super_genre} with unique characteristics"
            })
        logger.warning(f"Using fallback variations for {super_genre}")
        return APIResponse(
            success=True,
            message=f"Generated {len(fallback_variations)} {super_genre} variations (fallback mode)",
            data=fallback_variations
        )


@router.post("/trends/update", response_model=APIResponse)
async def update_viral_trends():
    """
    Update viral music trends from live web search

    Process:
    1. Uses Gemini AI with current knowledge to identify viral trends
    2. Searches for trends on TikTok, Spotify, YouTube Shorts
    3. Includes both audio trends and music video aesthetics
    4. Updates A1_Trend_Database sheet with 20 current trends
    5. Returns updated trends list

    This endpoint powers the "🔄 Update Trends from Web" button in the frontend.
    """
    try:
        result = await agent1_service.update_viral_trends()

        if result["status"] == "success":
            return APIResponse(
                success=True,
                message=result["message"],
                data={
                    "count": result["count"],
                    "trends": result.get("trends", [])
                }
            )
        else:
            # Service returned error status - log but don't crash
            logger.warning(f"Trend update service returned error: {result.get('message')}")
            return APIResponse(
                success=False,
                message=result.get("message", "Failed to update trends - using cached data"),
                data={"count": 0, "trends": []}
            )

    except Exception as e:
        logger.error(f"Failed to update viral trends: {e}")
        # FALLBACK: Don't crash, return graceful error response
        return APIResponse(
            success=False,
            message=f"Unable to update trends from web - using cached data",
            data={"count": 0, "trends": []}
        )


# ==================== Phase B: Audio Analysis & Scene Planning ====================

@router.post("/audio/analyze", response_model=APIResponse)
async def analyze_audio(file: bytes, filename: str):
    """
    Analyze audio file and create smart scene breakdown

    Process:
    1. Agent 3 analyzes audio (RMS energy, BPM, sections)
    2. Detects Intro/Verse/Chorus based on energy changes
    3. Smart-splits sections into ≤8s chunks (Veo/Runway limit)
    4. Returns scene list with start, end, energy, type

    Args:
        file: Audio file bytes (WAV/MP3)
        filename: Original filename

    Returns:
        Scenes list with timing and energy data
    """
    try:
        logger.info(f"Analyzing audio file: {filename}")

        # Call Agent 3 for audio analysis
        analysis_result = await agent3_service.analyze_audio_file(
            audio_file_bytes=file,
            filename=filename,
            max_scene_duration=8.0  # Veo/Runway limit
        )

        return APIResponse(
            success=True,
            message=f"Audio analyzed: {analysis_result['total_scenes']} scenes created",
            data=analysis_result
        )

    except Exception as e:
        logger.error(f"Audio analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scenes/process", response_model=APIResponse)
async def process_scenes(scenes: list[Dict[str, Any]], project_id: str = None, use_ai: bool = True):
    """
    Process scenes with Agent 4 "The Director"

    Process:
    1. Takes scene list from Agent 3
    2. Loads Video_Prompt_Cheatsheet from Google Sheets
    3. Maps energy levels to camera/lighting:
       - Low energy → Slow Zoom, Soft lighting
       - High energy → Whip Pan, Strobe lighting
    4. Generates cinematic descriptions (AI or templates)

    Args:
        scenes: List of scenes from audio analysis
        project_id: Optional project ID
        use_ai: Use Gemini AI for descriptions (default: True)

    Returns:
        Enhanced scenes with camera, lighting, description
    """
    try:
        logger.info(f"Processing {len(scenes)} scenes with Agent 4")

        # Call Agent 4 for scene enhancement
        enhanced_scenes = await agent4_service.process_scenes(
            scenes=scenes,
            project_id=project_id,
            use_ai_enhancement=use_ai
        )

        return APIResponse(
            success=True,
            message=f"Processed {len(enhanced_scenes)} scenes with directing details",
            data={"scenes": enhanced_scenes}
        )

    except Exception as e:
        logger.error(f"Scene processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Phase C1: Style Anchors & Visual Learning ====================

@router.get("/styles", response_model=APIResponse)
async def get_available_styles():
    """
    Get all available style presets from A5_Style_Database

    Returns:
        List of style dictionaries with:
        - name: Style name (e.g., "CineStill 800T")
        - suffix: Prompt suffix for video generation
        - negative: Negative prompt (optional)
        - description: Human-readable description
    """
    try:
        from app.agents.agent_5_style_anchors.service import agent5_service

        styles = await agent5_service.get_available_styles()

        return APIResponse(
            success=True,
            message=f"Retrieved {len(styles)} style presets",
            data=styles
        )
    except Exception as e:
        logger.error(f"Failed to get styles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/styles/learn", response_model=APIResponse)
async def learn_style_from_image(
    file: bytes,
    style_name: str,
    mime_type: str = "image/jpeg"
):
    """
    Learn a new visual style from an uploaded image using Gemini Vision

    Process:
    1. Send image to Gemini 3.0 Preview (Vision)
    2. AI analyzes lighting, color grading, film stock, composition
    3. Generates a compact "prompt suffix" (30-50 words)
    4. Saves to A5_Style_Database as a new preset

    Args:
        file: Image file bytes
        style_name: Name for the new style (e.g., "My Custom Look")
        mime_type: MIME type (image/jpeg, image/png, etc.)

    Returns:
        Style analysis result with generated suffix
    """
    try:
        from app.agents.agent_5_style_anchors.service import agent5_service

        logger.info(f"Learning style from image: {style_name}")

        result = await agent5_service.learn_style_from_image(
            image_bytes=file,
            style_name=style_name,
            mime_type=mime_type
        )

        if result["status"] == "success":
            return APIResponse(
                success=True,
                message=result["message"],
                data=result
            )
        else:
            raise HTTPException(status_code=500, detail=result["message"])

    except Exception as e:
        logger.error(f"Style learning failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Phase C2: Video Prompt Generation ====================

@router.post("/prompts/generate", response_model=APIResponse)
async def generate_video_prompts(request: Dict[str, Any]):
    """
    Generate platform-optimized video prompts for all scenes

    Process:
    1. Load scenes (from request or project)
    2. Load selected style preset (optional)
    3. Agent 6 generates narrative prompts for Veo
    4. Agent 7 generates modular prompts for Runway
    5. Agent 8 validates and auto-corrects all prompts
    6. Returns complete prompt set ready for production

    Args:
        scenes: List of scene dicts
        style_name: Optional style preset name (from A5_Style_Database)
        validate: Whether to run QC validation (default: True)

    Returns:
        Dict with veo_prompts, runway_prompts, and validation_stats
    """
    try:
        from app.agents.agent_6_veo_prompter.service import agent6_service
        from app.agents.agent_7_runway_prompter.service import agent7_service
        from app.agents.agent_8_refiner.service import agent8_service
        from app.agents.agent_5_style_anchors.service import agent5_service

        scenes = request.get("scenes", [])
        style_name = request.get("style_name")
        validate = request.get("validate", True)

        if not scenes:
            raise HTTPException(status_code=400, detail="scenes list is required")

        logger.info(f"Generating prompts for {len(scenes)} scenes (style: {style_name or 'default'})")

        # Load style if specified
        style = None
        if style_name:
            all_styles = await agent5_service.get_available_styles()
            style = next((s for s in all_styles if s["name"] == style_name), None)
            if not style:
                logger.warning(f"Style '{style_name}' not found, using default")

        veo_prompts = []
        runway_prompts = []

        # Generate prompts for each scene
        for scene in scenes:
            # Generate Veo prompt
            veo_prompt = await agent6_service.generate_prompt(scene, style)
            veo_prompts.append(veo_prompt)

            # Generate Runway prompt
            runway_prompt = await agent7_service.generate_prompt(scene, style)
            runway_prompts.append(runway_prompt)

        # Validate with Agent 8 if requested
        validation_stats = None
        if validate:
            logger.info("Running QC validation on all prompts")

            # Validate all prompts
            all_prompts = veo_prompts + runway_prompts
            validation_result = await agent8_service.validate_batch(all_prompts, style)

            # Update prompts with validated versions
            validated_prompts = validation_result["results"]

            # Split back into veo and runway
            veo_count = len(veo_prompts)
            veo_prompts = validated_prompts[:veo_count]
            runway_prompts = validated_prompts[veo_count:]

            validation_stats = {
                "total": validation_result["total"],
                "valid": validation_result["valid"],
                "corrected": validation_result["corrected"],
                "errors": validation_result["errors"]
            }

            logger.info(f"Validation complete: {validation_stats['valid']} valid, {validation_stats['corrected']} corrected, {validation_stats['errors']} errors")

        return APIResponse(
            success=True,
            message=f"Generated {len(veo_prompts)} Veo prompts and {len(runway_prompts)} Runway prompts",
            data={
                "veo_prompts": veo_prompts,
                "runway_prompts": runway_prompts,
                "validation_stats": validation_stats,
                "style_used": style["name"] if style else None
            }
        )

    except Exception as e:
        logger.error(f"Prompt generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/prompts/validate", response_model=APIResponse)
async def validate_prompt(request: Dict[str, Any]):
    """
    Validate and auto-correct a single video prompt

    Process:
    1. Check prompt length against model limits (Veo: 500, Runway: 300)
    2. Scan for negative/forbidden keywords from style
    3. Auto-correct issues (remove forbidden words, trim length)
    4. Return validated prompt with status and corrections list

    Args:
        prompt_dict: Dict with 'prompt', 'model', 'scene_id'
        style_name: Optional style preset name for negative keyword checking

    Returns:
        Validated prompt with status ("valid", "corrected", "error")
    """
    try:
        from app.agents.agent_8_refiner.service import agent8_service
        from app.agents.agent_5_style_anchors.service import agent5_service

        prompt_dict = request.get("prompt_dict")
        style_name = request.get("style_name")

        if not prompt_dict:
            raise HTTPException(status_code=400, detail="prompt_dict is required")

        logger.info(f"Validating {prompt_dict.get('model', 'unknown')} prompt")

        # Load style if specified
        style = None
        if style_name:
            all_styles = await agent5_service.get_available_styles()
            style = next((s for s in all_styles if s["name"] == style_name), None)

        # Validate
        validated = await agent8_service.validate_prompt(prompt_dict, style)

        return APIResponse(
            success=True,
            message=f"Validation complete: {validated['status']}",
            data=validated
        )

    except Exception as e:
        logger.error(f"Prompt validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/prompts/batch-validate", response_model=APIResponse)
async def batch_validate_prompts(request: Dict[str, Any]):
    """
    Validate multiple prompts at once

    Args:
        prompts: List of prompt dicts
        style_name: Optional style preset name

    Returns:
        Validation statistics and all validated prompts
    """
    try:
        from app.agents.agent_8_refiner.service import agent8_service
        from app.agents.agent_5_style_anchors.service import agent5_service

        prompts = request.get("prompts", [])
        style_name = request.get("style_name")

        if not prompts:
            raise HTTPException(status_code=400, detail="prompts list is required")

        logger.info(f"Batch validating {len(prompts)} prompts")

        # Load style if specified
        style = None
        if style_name:
            all_styles = await agent5_service.get_available_styles()
            style = next((s for s in all_styles if s["name"] == style_name), None)

        # Validate batch
        result = await agent8_service.validate_batch(prompts, style)

        return APIResponse(
            success=True,
            message=f"Validated {result['total']} prompts: {result['valid']} valid, {result['corrected']} corrected",
            data=result
        )

    except Exception as e:
        logger.error(f"Batch validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Phase D: Post-Production & Distribution ====================

@router.post("/capcut/generate-guide", response_model=APIResponse)
async def generate_capcut_guide(request: Dict[str, Any]):
    """
    Generate CapCut editing guide (Edit Decision List)

    Process:
    1. Analyzes scene timings and energy levels
    2. Loads CapCut effects from A9_CapCut_Effects database
    3. Creates step-by-step markdown editing guide
    4. Recommends effects based on energy (low → glow/blur, high → shake/strobe)

    Args:
        scenes: List of scene dicts with timing, energy, type
        audio_duration: Total audio duration (optional)

    Returns:
        Markdown-formatted editing guide
    """
    try:
        from app.agents.agent_9_capcut.service import agent9_service

        scenes = request.get("scenes", [])
        audio_duration = request.get("audio_duration")

        if not scenes:
            raise HTTPException(status_code=400, detail="scenes list is required")

        logger.info(f"Generating CapCut guide for {len(scenes)} scenes")

        # Generate guide
        guide_markdown = await agent9_service.generate_edit_guide(
            scenes=scenes,
            audio_duration=audio_duration
        )

        return APIResponse(
            success=True,
            message=f"CapCut guide generated for {len(scenes)} scenes",
            data={
                "guide": guide_markdown,
                "scene_count": len(scenes)
            }
        )

    except Exception as e:
        logger.error(f"CapCut guide generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/youtube/generate-metadata", response_model=APIResponse)
async def generate_youtube_metadata(request: Dict[str, Any]):
    """
    Generate viral YouTube metadata package

    Process:
    1. Uses Gemini AI to create click-worthy title
    2. Generates SEO-optimized description
    3. Creates 15-20 relevant tags
    4. Extracts top 5 hashtags

    Args:
        song_title: Song title
        artist: Artist name
        genre: Music genre (optional)
        mood: Song mood (optional)
        style_name: Visual style name (optional)

    Returns:
        Dict with title, description, tags, hashtags
    """
    try:
        from app.agents.agent_10_youtube.service import agent10_service
        from app.agents.agent_5_style_anchors.service import agent5_service

        song_title = request.get("song_title")
        artist = request.get("artist")
        genre = request.get("genre")
        mood = request.get("mood")
        style_name = request.get("style_name")

        if not song_title or not artist:
            raise HTTPException(status_code=400, detail="song_title and artist are required")

        logger.info(f"Generating YouTube metadata for '{song_title}' by {artist}")

        # Load style if specified
        style = None
        if style_name:
            all_styles = await agent5_service.get_available_styles()
            style = next((s for s in all_styles if s["name"] == style_name), None)

        # Generate metadata
        metadata = await agent10_service.generate_metadata(
            song_title=song_title,
            artist=artist,
            genre=genre,
            mood=mood,
            style=style
        )

        return APIResponse(
            success=True,
            message="YouTube metadata generated successfully",
            data=metadata
        )

    except Exception as e:
        logger.error(f"YouTube metadata generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/youtube/generate-thumbnail", response_model=APIResponse)
async def generate_thumbnail_prompt(request: Dict[str, Any]):
    """
    Generate thumbnail image prompt for Imagen 3 / Midjourney

    Process:
    1. Analyzes song title, artist, and visual style
    2. Creates detailed image generation prompt
    3. Optimized for 16:9 YouTube thumbnail format
    4. Focuses on click-worthy, eye-catching composition

    Args:
        song_title: Song title
        artist: Artist name
        style_name: Visual style name (optional)
        mood: Song mood (optional)

    Returns:
        Image generation prompt string
    """
    try:
        from app.agents.agent_10_youtube.service import agent10_service
        from app.agents.agent_5_style_anchors.service import agent5_service

        song_title = request.get("song_title")
        artist = request.get("artist")
        style_name = request.get("style_name")
        mood = request.get("mood")

        if not song_title or not artist:
            raise HTTPException(status_code=400, detail="song_title and artist are required")

        logger.info(f"Generating thumbnail prompt for '{song_title}'")

        # Load style if specified
        style = None
        if style_name:
            all_styles = await agent5_service.get_available_styles()
            style = next((s for s in all_styles if s["name"] == style_name), None)

        # Generate thumbnail prompt
        thumbnail_prompt = await agent10_service.generate_thumbnail_prompt(
            song_title=song_title,
            artist=artist,
            style=style,
            mood=mood
        )

        return APIResponse(
            success=True,
            message="Thumbnail prompt generated successfully",
            data={
                "prompt": thumbnail_prompt,
                "format": "1280x720px (16:9)",
                "platform": "Imagen 3 / Midjourney"
            }
        )

    except Exception as e:
        logger.error(f"Thumbnail prompt generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Phase E: Self-Learning & Imagen Integration ====================

@router.post("/styles/generate", response_model=APIResponse)
async def generate_style_with_imagen(request: Dict[str, Any]):
    """
    Generate a visual style reference image using Imagen 3.0/4

    Process:
    1. Generates image from text prompt using Imagen
    2. Analyzes generated image with Gemini Vision
    3. Extracts style suffix for video prompts
    4. Optionally saves to A5_Style_Database

    Args:
        prompt: Text description of desired style
        style_name: Name for the style (optional, required if save=True)
        aspect_ratio: Image aspect ratio (default: "1:1")
        save_to_database: Whether to save the style (default: False)

    Returns:
        Dict with:
        - image_base64: Base64-encoded generated image
        - style_suffix: Extracted style description
        - success: Generation status
    """
    try:
        from app.agents.agent_5_style_anchors.service import agent5_service

        prompt = request.get("prompt")
        style_name = request.get("style_name")
        aspect_ratio = request.get("aspect_ratio", "1:1")
        save_to_database = request.get("save_to_database", False)

        if not prompt:
            raise HTTPException(status_code=400, detail="prompt is required")

        if save_to_database and not style_name:
            raise HTTPException(status_code=400, detail="style_name is required when save_to_database=True")

        logger.info(f"Generating style reference with Imagen: {prompt[:100]}")

        # Generate style reference
        result = await agent5_service.generate_style_reference(
            prompt=prompt,
            style_name=style_name,
            aspect_ratio=aspect_ratio,
            save_to_database=save_to_database
        )

        return APIResponse(
            success=result.get("success", False),
            message=result.get("message", "Style reference generated"),
            data=result
        )

    except Exception as e:
        logger.error(f"Style generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/prompts/mark-gold-standard", response_model=APIResponse)
async def mark_prompt_as_gold_standard(request: Dict[str, Any]):
    """
    Mark a prompt as gold standard for Few-Shot Learning (Feedback Loop)

    This enables self-learning: good prompts are saved to A6_Video_Examples
    and become part of the Few-Shot Learning knowledge base for future generations.

    Process:
    1. Receives a prompt + scene description
    2. Saves to A6_Video_Examples database
    3. Future prompt generations will learn from this example

    Args:
        model: Model type ("veo" or "runway")
        prompt: The prompt text to save
        scene_description: Brief description of the scene
        energy: Energy level (low, medium, high)

    Returns:
        Success status and confirmation message
    """
    try:
        from app.agents.agent_6_veo_prompter.service import agent6_service
        from app.agents.agent_7_runway_prompter.service import agent7_service

        model = request.get("model")
        prompt = request.get("prompt")
        scene_description = request.get("scene_description", "")
        energy = request.get("energy", "medium")

        if not model or not prompt:
            raise HTTPException(status_code=400, detail="model and prompt are required")

        if model not in ["veo", "runway"]:
            raise HTTPException(status_code=400, detail="model must be 'veo' or 'runway'")

        logger.info(f"Marking {model} prompt as gold standard")

        # Save to appropriate agent
        if model == "veo":
            result = await agent6_service.save_as_gold_standard(
                prompt=prompt,
                scene_description=scene_description,
                energy=energy
            )
        else:  # runway
            result = await agent7_service.save_as_gold_standard(
                prompt=prompt,
                scene_description=scene_description,
                energy=energy
            )

        if result.get("success"):
            return APIResponse(
                success=True,
                message=f"✅ {result.get('message')} - System will learn from this prompt!",
                data=result
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("message"))

    except Exception as e:
        logger.error(f"Failed to mark prompt as gold standard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Phase F: Doku-Studio (Agents 12 & 13) ====================

@router.post("/documentary/analyze-style", response_model=APIResponse)
async def analyze_documentary_style(request: Dict[str, Any]):
    """
    Analyze a documentary video to extract its style template (Reverse Engineering)

    Process:
    1. Extract transcript from YouTube URL
    2. Analyze pacing (words per minute, cut frequency)
    3. Extract keywords and B-roll suggestions with AI
    4. Generate comprehensive style template

    Args:
        video_url: YouTube URL (optional)
        transcript_text: Pre-extracted transcript (optional, alternative to URL)

    Returns:
        StyleTemplate with pacing, tone, visual style, keywords, B-roll suggestions
    """
    try:
        from app.agents.agent_12_style_analyst.service import agent12_service

        video_url = request.get("video_url")
        transcript_text = request.get("transcript_text")

        if not video_url and not transcript_text:
            raise HTTPException(
                status_code=400,
                detail="Either video_url or transcript_text is required"
            )

        logger.info(f"Analyzing documentary style from {'URL' if video_url else 'transcript'}")

        # Analyze style
        style_template = await agent12_service.analyze_video_style(
            video_url=video_url,
            transcript_text=transcript_text
        )

        if not style_template.get("success"):
            raise HTTPException(
                status_code=500,
                detail=style_template.get("error", "Style analysis failed")
            )

        return APIResponse(
            success=True,
            message=f"Style template extracted: {style_template.get('template_name')}",
            data=style_template
        )

    except Exception as e:
        logger.error(f"Documentary style analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documentary/generate-script", response_model=APIResponse)
async def generate_documentary_script(request: Dict[str, Any]):
    """
    Generate a complete documentary script using 3-Act structure

    Process:
    1. Takes topic and optional style template
    2. Uses Gemini Pro to create 15-minute documentary script
    3. Applies 3-Act structure: Hook (0-2min), Conflict (2-10min), Resolution (10-15min)
    4. Generates chapters with full narration and B-roll suggestions

    Args:
        topic: Documentary topic (e.g., "The Rise of AI")
        duration_minutes: Total duration (default: 15)
        style_template: Optional style template from Agent 12 (for style cloning)

    Returns:
        Complete documentary script with:
        - chapters: List of chapter objects with timing
        - narration: Full narrator script
        - b_roll: B-roll suggestions for each chapter
        - structure: 3-act breakdown
    """
    try:
        from app.agents.agent_13_story_architect.service import agent13_service

        topic = request.get("topic")
        duration_minutes = request.get("duration_minutes", 15)
        style_template = request.get("style_template")

        if not topic:
            raise HTTPException(status_code=400, detail="topic is required")

        logger.info(f"Generating documentary script for topic: {topic}")

        # Generate script
        script = await agent13_service.create_3_act_structure(
            topic=topic,
            duration_minutes=duration_minutes,
            style_template=style_template
        )

        return APIResponse(
            success=True,
            message=f"Documentary script generated: {script.get('title', 'Untitled')}",
            data=script
        )

    except Exception as e:
        logger.error(f"Documentary script generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Phase F Extensions: Documentary Production (Agents 14-17) ====================

@router.post("/documentary/prepare-voiceover", response_model=APIResponse)
async def prepare_voiceover(request: Dict[str, Any]):
    """
    Prepare voiceover script for documentary narration (Agent 14)

    Hybrid Mode:
    - Manual: Download clean script for ElevenLabs web interface
    - API: Automatic generation with ElevenLabs API (future)

    Process:
    1. Extracts narration text from documentary script
    2. Calculates duration estimate (150 WPM average)
    3. Returns clean text file or audio URL

    Args:
        script: Complete script from Agent 13
        mode: "manual" (download text) or "api" (ElevenLabs)
        voice_id: ElevenLabs voice ID (for API mode)

    Returns:
        - script_text: Clean narration text (for manual download)
        - audio_url: Audio file URL (for API mode)
        - duration_estimate: Estimated minutes
        - word_count: Total word count
    """
    try:
        from app.agents.agent_14_narrator.service import narrator_service

        script = request.get("script")
        mode = request.get("mode", "manual")
        voice_id = request.get("voice_id")

        if not script:
            raise HTTPException(status_code=400, detail="script is required")

        logger.info(f"Preparing voiceover in {mode} mode")

        # Prepare voiceover
        result = await narrator_service.prepare_voiceover_script(
            script=script,
            mode=mode,
            voice_id=voice_id
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Voiceover preparation failed")
            )

        return APIResponse(
            success=True,
            message=f"Voiceover prepared ({mode} mode): {result.get('word_count', 0)} words, ~{result.get('duration_estimate', 0)} min",
            data=result
        )

    except Exception as e:
        logger.error(f"Voiceover preparation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documentary/fact-check", response_model=APIResponse)
async def fact_check_script(request: Dict[str, Any]):
    """
    Verify factual claims in documentary script using AI (Agent 15)

    Process:
    1. Extracts factual claims from script
    2. Verifies each claim with Gemini + Google Search Grounding
    3. Generates detailed fact-check report (Markdown)
    4. Highlights critical issues and warnings

    Args:
        script: Documentary script from Agent 13
        check_mode: "critical" (numbers/dates/names) or "full" (all claims)

    Returns:
        - fact_report: Markdown report with issues and verified claims
        - issues_found: Number of critical issues
        - checks_performed: Total checks
        - critical_issues: List of false/misleading claims
        - warnings: List of uncertain claims
    """
    try:
        from app.agents.agent_15_fact_checker.service import fact_checker_service

        script = request.get("script")
        check_mode = request.get("check_mode", "critical")

        if not script:
            raise HTTPException(status_code=400, detail="script is required")

        logger.info(f"Fact-checking script in {check_mode} mode")

        # Run fact check
        result = await fact_checker_service.verify_facts(
            script=script,
            check_mode=check_mode
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Fact-checking failed")
            )

        issues_count = result.get("issues_found", 0)
        warning_message = f"⚠️ {issues_count} critical issues found!" if issues_count > 0 else "✅ All facts verified!"

        return APIResponse(
            success=True,
            message=f"Fact-check complete: {result.get('checks_performed', 0)} claims checked. {warning_message}",
            data=result
        )

    except Exception as e:
        logger.error(f"Fact-checking failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documentary/find-stock-footage", response_model=APIResponse)
async def find_stock_footage(request: Dict[str, Any]):
    """
    Find free stock footage for B-roll using Pexels API (Agent 16)

    Process:
    1. Takes B-roll keywords from script or manual list
    2. Searches Pexels for free, high-quality stock videos
    3. Returns video URLs with download links
    4. Supports both videos and photos

    Args:
        keywords: List of search keywords OR
        script: Documentary script (will auto-extract B-roll keywords)
        media_type: "videos" or "photos" (default: "videos")
        results_per_keyword: Number of results per keyword (default: 3)

    Returns:
        - results: List of stock footage with:
          - title: Video title
          - thumbnail: Preview image URL
          - download_url: Direct download link
          - duration: Video duration (for videos)
          - photographer: Creator name
          - source: "Pexels"
    """
    try:
        from app.agents.agent_16_stock_scout.service import stock_scout_service

        keywords = request.get("keywords")
        script = request.get("script")
        media_type = request.get("media_type", "videos")
        results_per_keyword = request.get("results_per_keyword", 3)

        # Either keywords or script is required
        if not keywords and not script:
            raise HTTPException(
                status_code=400,
                detail="Either keywords list or script is required"
            )

        # Extract keywords from script if provided
        if script and not keywords:
            logger.info("Extracting B-roll keywords from script")
            keywords = await stock_scout_service.extract_broll_keywords(script)

        logger.info(f"Finding stock footage for {len(keywords)} keywords")

        # Search for stock footage
        result = await stock_scout_service.find_stock_footage(
            keywords=keywords,
            media_type=media_type,
            results_per_keyword=results_per_keyword
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Stock footage search failed")
            )

        return APIResponse(
            success=True,
            message=f"Found {result.get('total_found', 0)} {media_type} across {len(keywords)} keywords",
            data=result
        )

    except Exception as e:
        logger.error(f"Stock footage search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documentary/generate-xml", response_model=APIResponse)
async def generate_timeline_xml(request: Dict[str, Any]):
    """
    Generate FCPXML timeline for DaVinci Resolve / Premiere Pro (Agent 17)

    Process:
    1. Takes all production assets (voiceover, music, videos, images)
    2. Generates FCPXML (Final Cut Pro XML) format
    3. Creates multi-track timeline:
       - Track 1: Voiceover narration
       - Track 2: Background music (30% volume)
       - Track 3: B-roll videos
       - Track 4: Still images
    4. Adds chapter markers from script

    Args:
        assets: {
            "voiceover": {"file_path": str, "duration": float},
            "music": {"file_path": str, "duration": float},
            "videos": [{"file_path": str, "duration": float, "start_time": float}],
            "images": [{"file_path": str, "duration": float, "start_time": float}]
        }
        script: Optional script for chapter markers
        frame_rate: "24", "25", "30", or "60" (default: "24")
        format: "fcpxml" or "edl" (default: "fcpxml")

    Returns:
        - xml_content: Complete FCPXML content
        - timeline_duration: Total duration in seconds
        - tracks: Number of tracks
    """
    try:
        from app.agents.agent_17_xml_architect.service import xml_architect_service

        assets = request.get("assets")
        script = request.get("script")
        frame_rate = request.get("frame_rate", "24")
        xml_format = request.get("format", "fcpxml")

        if not assets:
            raise HTTPException(status_code=400, detail="assets are required")

        logger.info(f"Generating {xml_format.upper()} timeline at {frame_rate} fps")

        # Generate XML
        if xml_format == "fcpxml":
            result = await xml_architect_service.generate_fcpxml(
                assets=assets,
                script=script,
                frame_rate=frame_rate
            )
        elif xml_format == "edl":
            result = await xml_architect_service.generate_edl(assets=assets)
        else:
            raise HTTPException(
                status_code=400,
                detail="format must be 'fcpxml' or 'edl'"
            )

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "XML generation failed")
            )

        return APIResponse(
            success=True,
            message=f"{xml_format.upper()} generated: {result.get('timeline_duration', 0):.1f}s, {result.get('tracks', 0)} tracks",
            data=result
        )

    except Exception as e:
        logger.error(f"XML generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Debugger ====================

@router.post("/debugger/chat", response_model=APIResponse)
async def debugger_chat(request: Dict[str, Any]):
    """
    Debugger chat endpoint - send messages to Gemini for testing

    Request body:
    - message: str - User message
    - config: dict - Agent configuration (model, temperature, system_instruction, etc.)
    - chat_history: list - Previous messages (optional)
    """
    try:
        from app.services.debugger_service import debugger_service

        message = request.get("message", "")
        config = request.get("config", {})
        chat_history = request.get("chat_history", [])

        if not message:
            raise HTTPException(status_code=400, detail="Message is required")

        # Send message to debugger service
        result = await debugger_service.send_message(
            message=message,
            config=config,
            chat_history=chat_history
        )

        return APIResponse(
            success=result.get("success", False),
            message="Message processed",
            data=result
        )

    except Exception as e:
        logger.error(f"Debugger chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debugger/presets", response_model=APIResponse)
async def get_debugger_presets():
    """Get agent preset configurations for the debugger"""
    try:
        from app.services.debugger_service import debugger_service

        presets = debugger_service.get_agent_presets()

        return APIResponse(
            success=True,
            message="Presets retrieved",
            data=presets
        )

    except Exception as e:
        logger.error(f"Failed to get debugger presets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debugger/models", response_model=APIResponse)
async def get_available_models():
    """Get list of available Gemini models"""
    try:
        from app.services.debugger_service import debugger_service

        models = debugger_service.get_available_models()

        return APIResponse(
            success=True,
            message="Models retrieved",
            data={"models": models}
        )

    except Exception as e:
        logger.error(f"Failed to get available models: {e}")
        raise HTTPException(status_code=500, detail=str(e))
