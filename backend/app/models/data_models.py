"""
Pydantic Data Models for 11-Agent Music Video Production System
Phase A: Models for Agent 1, Agent 2, and QC Processor
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid


def new_id() -> str:
    """Generate a new UUID"""
    return str(uuid.uuid4())


def now_utc() -> datetime:
    """Get current UTC timestamp"""
    return datetime.utcnow()


# ============================================================
# AGENT 1: TREND DETECTIVE - OUTPUT MODEL
# ============================================================

class TrendReport(BaseModel):
    """
    Output from Agent 1 (Trend Detective)
    Stored in Google Sheet: A1_Trends_DB
    """
    id: str = Field(default_factory=new_id)
    timestamp: datetime = Field(default_factory=now_utc)
    genre: str = Field(..., description="Music genre (e.g., 'Afrobeat', 'Lo-fi Hip Hop')")
    details: str = Field(..., description="Detailed description of the trend")
    viral_potential: int = Field(..., ge=1, le=10, description="Viral potential score (1-10)")
    status: str = Field(default='NEW', description="Processing status: NEW, PROCESSED")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2025-11-16T12:00:00",
                "genre": "Afrobeat",
                "details": "Fusion of traditional African rhythms with modern electronic production",
                "viral_potential": 8,
                "status": "NEW"
            }
        }


# ============================================================
# AGENT 2: SUNO PROMPT GENERATOR - OUTPUT MODEL
# ============================================================

class SunoPrompt(BaseModel):
    """
    Output from Agent 2 (Suno Prompt Generator)
    Stored in Google Sheet: A2_GeneratedPrompts_DB
    """
    id: str = Field(default_factory=new_id)
    trend_id: str = Field(..., description="Reference to the TrendReport ID")
    timestamp: datetime = Field(default_factory=now_utc)
    prompt_text: str = Field(..., description="Generated Suno prompt (70-100 words)")
    status: str = Field(default='PENDING_QC', description="QC status: PENDING_QC, REVIEWED, FAILED")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440001",
                "trend_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2025-11-16T12:05:00",
                "prompt_text": "Create an Afrobeat track with pulsing 808 bass, traditional talking drums, and hypnotic guitar riffs. Incorporate modern trap hi-hats and atmospheric synth pads. The rhythm should be danceable at 128 BPM with call-and-response vocal patterns reminiscent of Burna Boy and Wizkid. Add layered percussion including shakers and congas for authentic African flavor.",
                "status": "PENDING_QC"
            }
        }


# ============================================================
# QC PROCESSOR - OUTPUT MODEL
# ============================================================

class QCResult(BaseModel):
    """
    Quality Control evaluation result
    Stored in Google Sheet: QC_Results_DB
    """
    id: str = Field(default_factory=new_id)
    prompt_id: str = Field(..., description="Reference to the SunoPrompt ID")
    timestamp: datetime = Field(default_factory=now_utc)
    score: int = Field(..., ge=1, le=10, description="Quality score (1-10)")
    feedback: str = Field(..., description="Concise feedback from QC agent")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "770e8400-e29b-41d4-a716-446655440002",
                "prompt_id": "660e8400-e29b-41d4-a716-446655440001",
                "timestamp": "2025-11-16T12:10:00",
                "score": 9,
                "feedback": "Excellent genre authenticity and production detail. Well-structured prompt."
            }
        }


# ============================================================
# BEST PRACTICES - FEW-SHOT LEARNING MODEL
# ============================================================

class ApprovedPrompt(BaseModel):
    """
    Approved prompts for Few-Shot Learning
    Stored in Google Sheet: ApprovedBestPractices
    """
    id: str = Field(default_factory=new_id)
    prompt_text: str = Field(..., description="The approved prompt text")
    score: int = Field(..., ge=7, le=10, description="Quality score (7-10 for approved)")
    source: str = Field(default='Generated', description="Source: 'Generated' or 'Community'")
    timestamp: datetime = Field(default_factory=now_utc)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "880e8400-e29b-41d4-a716-446655440003",
                "prompt_text": "Create an Afrobeat track...",
                "score": 9,
                "source": "Generated",
                "timestamp": "2025-11-16T12:10:00"
            }
        }


# ============================================================
# API REQUEST/RESPONSE MODELS
# ============================================================

class AgentRunRequest(BaseModel):
    """Generic request model for agent execution"""
    count: Optional[int] = Field(default=5, ge=1, le=100, description="Number of items to process")


class AgentRunResponse(BaseModel):
    """Generic response model for agent execution"""
    success: bool
    message: str
    data: Optional[dict] = None


class QCProcessResponse(BaseModel):
    """Response model for QC Processor"""
    success: bool
    message: str
    processed: int = 0
    approved: int = 0
    failed: int = 0
