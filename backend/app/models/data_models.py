"""
Data Models for Music Video Production System
Pydantic models for all agents and workflows
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4


def new_id() -> str:
    """Generate a new unique ID"""
    return str(uuid4())


# ==================== Common Models ====================

class ProjectStatus(BaseModel):
    """Project status tracking"""
    status: str  # "INIT", "ANALYZING", "PLANNING", "GENERATING", "QC", "COMPLETE"
    current_agent: Optional[str] = None
    progress_percentage: float = 0.0
    last_updated: datetime = Field(default_factory=datetime.utcnow)


# ==================== Agent 1: Project Manager ====================

class Project(BaseModel):
    """Main project model created by Agent 1"""
    id: str = Field(default_factory=new_id)
    name: str
    artist: str
    song_title: str
    audio_file_path: Optional[str] = None
    status: ProjectStatus = Field(default_factory=ProjectStatus)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProjectCreate(BaseModel):
    """Request model for creating a new project"""
    name: str
    artist: str
    song_title: str


# ==================== Agent 2: QC Agent ====================

class QCFeedback(BaseModel):
    """Quality control feedback from Agent 2"""
    id: str = Field(default_factory=new_id)
    project_id: str
    target_id: str  # ID of scene, prompt, etc. being checked
    target_type: str  # "scene", "prompt", "style", etc.
    qc_status: str  # "APPROVED", "NEEDS_REVISION", "REJECTED"
    feedback: str
    suggestions: List[str] = Field(default_factory=list)
    iteration: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)


class QCRequest(BaseModel):
    """Request for QC review"""
    project_id: str
    target_id: str
    target_type: str
    content: str  # The content to be reviewed


# ==================== Agent 3: Audio Analyzer ====================

class AudioAnalysis(BaseModel):
    """Audio analysis output from Agent 3"""
    id: str = Field(default_factory=new_id)
    project_id: str
    filename: str
    duration: float  # in seconds
    bpm: int
    key: str  # e.g., "C major", "A minor"
    structure: List[str]  # ["Intro", "Verse", "Chorus", "Verse", "Bridge", "Chorus", "Outro"]
    peak_moments: List[float]  # Timestamps of musical peaks
    energy_profile: List[Dict[str, Any]] = Field(default_factory=list)  # Energy levels over time
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)


class AudioUploadRequest(BaseModel):
    """Request for audio file upload"""
    project_id: str
    filename: str


# ==================== Agent 4: Scene Breakdown ====================

class Scene(BaseModel):
    """Scene definition from Agent 4"""
    id: str = Field(default_factory=new_id)
    project_id: str
    scene_number: int
    start_time: float  # in seconds
    end_time: float  # in seconds
    duration: float  # in seconds
    music_section: str  # "Intro", "Verse", "Chorus", etc.
    description: str  # Detailed scene description
    visual_style_ref: str  # Reference to style anchor
    mood: str  # "energetic", "melancholic", "dreamy", etc.
    key_elements: List[str] = Field(default_factory=list)  # Visual elements to include
    camera_movement: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SceneBreakdownRequest(BaseModel):
    """Request for scene breakdown"""
    project_id: str
    audio_analysis_id: str


# Backward compatibility alias - SceneBreakdown is the same as Scene
SceneBreakdown = Scene


# ==================== Agent 5: Style Anchors ====================

class StyleAnchor(BaseModel):
    """Visual style anchor from Agent 5"""
    id: str = Field(default_factory=new_id)
    project_id: str
    style_name: str
    description: str  # Detailed style description
    color_palette: List[str]  # Hex color codes
    visual_references: List[str] = Field(default_factory=list)  # URLs or descriptions
    keywords: List[str] = Field(default_factory=list)  # Style keywords
    mood: str
    consistency_notes: str  # How to maintain consistency
    created_at: datetime = Field(default_factory=datetime.utcnow)


class StyleAnchorRequest(BaseModel):
    """Request for style anchor creation"""
    project_id: str
    scene_ids: List[str]


# ==================== Agent 6 & 7: Video Prompters ====================

class VideoPrompt(BaseModel):
    """Video generation prompt from Agent 6 (Veo) or Agent 7 (Runway)"""
    id: str = Field(default_factory=new_id)
    project_id: str
    scene_id: str
    scene_number: int
    generator: str  # "veo" or "runway"
    prompt_text: str
    negative_prompt: Optional[str] = None
    style_anchor_id: str
    technical_params: Dict[str, Any] = Field(default_factory=dict)  # Resolution, duration, etc.
    status: str = "PENDING_QC"  # "PENDING_QC", "APPROVED", "NEEDS_REVISION"
    iteration: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)


class VideoPromptRequest(BaseModel):
    """Request for video prompt generation"""
    project_id: str
    scene_id: str
    generator: str  # "veo" or "runway"


# ==================== Agent 8: Prompt Refiner ====================

class PromptRefinement(BaseModel):
    """Refined prompt from Agent 8"""
    id: str = Field(default_factory=new_id)
    original_prompt_id: str
    project_id: str
    scene_id: str
    refined_prompt_text: str
    refinement_reason: str
    changes_made: List[str] = Field(default_factory=list)
    qc_feedback_id: Optional[str] = None
    iteration: int
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PromptRefinementRequest(BaseModel):
    """Request for prompt refinement"""
    prompt_id: str
    qc_feedback_id: str


# ==================== Orchestration Models ====================

class VideoProductionPlan(BaseModel):
    """Complete video production plan"""
    project_id: str
    audio_analysis: Optional[AudioAnalysis] = None
    scenes: List[Scene] = Field(default_factory=list)
    style_anchors: List[StyleAnchor] = Field(default_factory=list)
    video_prompts: List[VideoPrompt] = Field(default_factory=list)
    status: str = "PLANNING"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class StoryboardResponse(BaseModel):
    """Complete storyboard data for frontend"""
    project: Project
    audio_analysis: Optional[AudioAnalysis] = None
    scenes: List[Scene] = Field(default_factory=list)
    style_anchors: List[StyleAnchor] = Field(default_factory=list)
    prompts: Dict[str, List[VideoPrompt]] = Field(default_factory=dict)  # Grouped by scene_id
    qc_feedback: List[QCFeedback] = Field(default_factory=list)


class OrchestrationRequest(BaseModel):
    """Request to start video production orchestration"""
    project_id: str
    generate_for_veo: bool = True
    generate_for_runway: bool = True


# ==================== API Response Models ====================

class APIResponse(BaseModel):
    """Standard API response"""
    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Error response"""
    success: bool = False
    error: str
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ==================== Suno Prompt Generation (Dynamic Few-Shot Learning) ====================

class SunoPromptExample(BaseModel):
    """Best practice example for Few-Shot Learning"""
    id: str = Field(default_factory=new_id)
    prompt_text: str
    genre: str
    quality_score: float  # 0-10 scale
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)  # plays, likes, etc.
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    source: str = "generated"  # "generated", "manual", "imported"


class SunoPromptRequest(BaseModel):
    """Request for generating Suno prompt"""
    target_genre: str
    mood: Optional[str] = None
    tempo: Optional[str] = None  # "slow", "medium", "fast"
    style_references: List[str] = Field(default_factory=list)
    additional_instructions: Optional[str] = None


class SunoPromptResponse(BaseModel):
    """Generated Suno prompt"""
    id: str = Field(default_factory=new_id)
    prompt_text: str
    genre: str
    mood: Optional[str] = None
    tempo: Optional[str] = None
    few_shot_examples_used: int = 0  # Number of examples used for generation
    quality_score: Optional[float] = None  # Set after QC
    status: str = "PENDING_QC"  # "PENDING_QC", "APPROVED", "REJECTED", "IN_BEST_PRACTICES"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FewShotLearningStats(BaseModel):
    """Statistics about the Few-Shot Learning system"""
    total_examples: int
    avg_quality_score: float
    examples_by_genre: Dict[str, int]
    recent_additions: int  # Last 24h
    top_performing_genres: List[str]
