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
        raise HTTPException(status_code=500, detail=str(e))


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
    except Exception as e:
        logger.error(f"Failed to generate genre variations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
            raise HTTPException(
                status_code=500,
                detail=result.get("message", "Failed to update trends")
            )

    except Exception as e:
        logger.error(f"Failed to update viral trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
    1. Send image to Gemini 1.5 Pro (Vision)
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
