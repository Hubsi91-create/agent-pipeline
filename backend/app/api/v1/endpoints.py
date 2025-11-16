"""
API v1 Endpoints for 11-Agent Music Video Production System
Phase A: Agent 1, Agent 2, and QC Processor endpoints
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import logging

from app.models.data_models import AgentRunRequest, AgentRunResponse, QCProcessResponse
from app.agents.agent_1_trend_detective.service import get_trend_detective_service
from app.agents.agent_2_suno_generator.service import get_suno_generator_service
from app.agents.qc_processor.service import get_qc_processor_service
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Create API router
router = APIRouter()


# ============================================================
# HEALTH CHECK
# ============================================================

@router.get("/health", tags=["System"])
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


# ============================================================
# AGENT 1: TREND DETECTIVE
# ============================================================

@router.post(
    "/agent1/run",
    response_model=AgentRunResponse,
    tags=["Agent 1: Trend Detective"]
)
async def run_agent1(request: AgentRunRequest = None):
    """
    Run Agent 1: Trend Detective
    Generates music trend reports and stores them in Google Sheets.

    Args:
        request: Optional request with count parameter

    Returns:
        Operation results with generated trends
    """
    try:
        count = request.count if request else settings.AGENT1_DEFAULT_TREND_COUNT

        logger.info(f"API: Starting Agent 1 with count={count}")

        agent1 = get_trend_detective_service()
        result = agent1.generate_and_store_trend_reports(count=count)

        return AgentRunResponse(
            success=result.get('success', False),
            message=result.get('message', ''),
            data=result
        )

    except Exception as e:
        logger.error(f"API Error in Agent 1: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/agent1/run-async",
    tags=["Agent 1: Trend Detective"]
)
async def run_agent1_async(
    background_tasks: BackgroundTasks,
    request: AgentRunRequest = None
):
    """
    Run Agent 1 asynchronously in the background.
    Returns immediately while agent runs in background.
    """
    count = request.count if request else settings.AGENT1_DEFAULT_TREND_COUNT

    def run_agent():
        agent1 = get_trend_detective_service()
        agent1.generate_and_store_trend_reports(count=count)

    background_tasks.add_task(run_agent)

    return {
        "status": "started",
        "message": f"Agent 1 started in background with count={count}"
    }


# ============================================================
# AGENT 2: SUNO PROMPT GENERATOR
# ============================================================

@router.post(
    "/agent2/run",
    response_model=AgentRunResponse,
    tags=["Agent 2: Suno Prompt Generator"]
)
async def run_agent2(request: AgentRunRequest = None):
    """
    Run Agent 2: Suno Prompt Generator
    Processes NEW trend reports and generates Suno prompts.

    Args:
        request: Optional request with count_per_trend parameter

    Returns:
        Operation results with prompts generated
    """
    try:
        count_per_trend = request.count if request else settings.AGENT2_DEFAULT_PROMPTS_PER_TREND

        logger.info(f"API: Starting Agent 2 with count_per_trend={count_per_trend}")

        agent2 = get_suno_generator_service()
        result = agent2.process_new_trends(count_per_trend=count_per_trend)

        return AgentRunResponse(
            success=result.get('success', False),
            message=result.get('message', ''),
            data=result
        )

    except Exception as e:
        logger.error(f"API Error in Agent 2: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/agent2/run-async",
    tags=["Agent 2: Suno Prompt Generator"]
)
async def run_agent2_async(
    background_tasks: BackgroundTasks,
    request: AgentRunRequest = None
):
    """
    Run Agent 2 asynchronously in the background.
    Returns immediately while agent runs in background.
    """
    count_per_trend = request.count if request else settings.AGENT2_DEFAULT_PROMPTS_PER_TREND

    def run_agent():
        agent2 = get_suno_generator_service()
        agent2.process_new_trends(count_per_trend=count_per_trend)

    background_tasks.add_task(run_agent)

    return {
        "status": "started",
        "message": f"Agent 2 started in background with count_per_trend={count_per_trend}"
    }


# ============================================================
# QC PROCESSOR
# ============================================================

@router.post(
    "/qc/run",
    response_model=QCProcessResponse,
    tags=["QC Processor"]
)
async def run_qc_processor():
    """
    Run QC Processor
    Evaluates all PENDING_QC prompts and updates best practices.

    Returns:
        Processing summary with counts
    """
    try:
        logger.info("API: Starting QC Processor")

        qc = get_qc_processor_service()
        result = qc.process_queue()

        return QCProcessResponse(
            success=result.get('success', False),
            message=result.get('message', ''),
            processed=result.get('processed', 0),
            approved=result.get('approved', 0),
            failed=result.get('failed', 0)
        )

    except Exception as e:
        logger.error(f"API Error in QC Processor: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/qc/run-async",
    tags=["QC Processor"]
)
async def run_qc_processor_async(background_tasks: BackgroundTasks):
    """
    Run QC Processor asynchronously in the background.
    Returns immediately while processing runs in background.
    """
    def run_qc():
        qc = get_qc_processor_service()
        qc.process_queue()

    background_tasks.add_task(run_qc)

    return {
        "status": "started",
        "message": "QC Processor started in background"
    }


# ============================================================
# ORCHESTRATION - RUN ALL AGENTS IN SEQUENCE
# ============================================================

@router.post(
    "/orchestration/run-phase-a",
    tags=["Orchestration"]
)
async def run_phase_a_pipeline():
    """
    Run complete Phase A pipeline:
    1. Agent 1: Generate trends
    2. Agent 2: Generate prompts
    3. QC: Evaluate prompts

    This is a synchronous sequential execution.
    Use with caution - may take several minutes.
    """
    try:
        logger.info("API: Starting Phase A Pipeline")

        results = {
            "agent1": None,
            "agent2": None,
            "qc": None
        }

        # Step 1: Agent 1
        logger.info("Pipeline: Running Agent 1...")
        agent1 = get_trend_detective_service()
        results["agent1"] = agent1.generate_and_store_trend_reports(
            count=settings.AGENT1_DEFAULT_TREND_COUNT
        )

        # Step 2: Agent 2
        logger.info("Pipeline: Running Agent 2...")
        agent2 = get_suno_generator_service()
        results["agent2"] = agent2.process_new_trends(
            count_per_trend=settings.AGENT2_DEFAULT_PROMPTS_PER_TREND
        )

        # Step 3: QC Processor
        logger.info("Pipeline: Running QC Processor...")
        qc = get_qc_processor_service()
        results["qc"] = qc.process_queue()

        logger.info("Pipeline: Phase A completed")

        return {
            "success": True,
            "message": "Phase A pipeline completed",
            "results": results
        }

    except Exception as e:
        logger.error(f"API Error in Phase A pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/orchestration/run-phase-a-async",
    tags=["Orchestration"]
)
async def run_phase_a_pipeline_async(background_tasks: BackgroundTasks):
    """
    Run complete Phase A pipeline in the background.
    Returns immediately.
    """
    def run_pipeline():
        try:
            agent1 = get_trend_detective_service()
            agent1.generate_and_store_trend_reports(count=settings.AGENT1_DEFAULT_TREND_COUNT)

            agent2 = get_suno_generator_service()
            agent2.process_new_trends(count_per_trend=settings.AGENT2_DEFAULT_PROMPTS_PER_TREND)

            qc = get_qc_processor_service()
            qc.process_queue()

            logger.info("Background Pipeline: Phase A completed successfully")
        except Exception as e:
            logger.error(f"Background Pipeline Error: {e}")

    background_tasks.add_task(run_pipeline)

    return {
        "status": "started",
        "message": "Phase A pipeline started in background. Check logs for progress."
    }
