"""
Agent 8: Prompt Refiner
Refines video prompts based on QC feedback
"""

from typing import Optional
from app.models.data_models import (
    VideoPrompt,
    PromptRefinement,
    QCFeedback,
    Scene,
    StyleAnchor
)
from app.infrastructure.external_services.gemini_service import gemini_service
from app.infrastructure.database.google_sheet_service import google_sheet_service, SHEET_A8_REFINEMENTS
from app.utils.logger import setup_logger

logger = setup_logger("Agent8_Refiner")


class Agent8Refiner:
    """Singleton service for prompt refinement"""

    _instance: Optional['Agent8Refiner'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def refine_prompt(
        self,
        original_prompt: VideoPrompt,
        qc_feedback: QCFeedback,
        scene: Scene,
        style_anchor: StyleAnchor
    ) -> PromptRefinement:
        """
        Refine a video prompt based on QC feedback

        Args:
            original_prompt: Original video prompt
            qc_feedback: QC feedback
            scene: Scene information
            style_anchor: Style anchor

        Returns:
            Refined prompt
        """
        logger.info(f"Refining prompt {original_prompt.id} based on QC feedback")

        # Create refinement prompt for Gemini
        gemini_prompt = self._create_refinement_prompt(
            original_prompt,
            qc_feedback,
            scene,
            style_anchor
        )

        # Get refined prompt
        refined_text = await gemini_service.generate_text(gemini_prompt, temperature=0.6)

        # Create refinement
        refinement = PromptRefinement(
            original_prompt_id=original_prompt.id,
            project_id=original_prompt.project_id,
            scene_id=original_prompt.scene_id,
            refined_prompt_text=refined_text.strip(),
            refinement_reason=qc_feedback.feedback,
            changes_made=qc_feedback.suggestions,
            qc_feedback_id=qc_feedback.id,
            iteration=original_prompt.iteration + 1
        )

        # Save to Google Sheets
        await self._save_to_sheets(refinement)

        logger.info(f"Prompt refined: {refinement.id} (iteration {refinement.iteration})")
        return refinement

    def _create_refinement_prompt(
        self,
        original_prompt: VideoPrompt,
        qc_feedback: QCFeedback,
        scene: Scene,
        style_anchor: StyleAnchor
    ) -> str:
        """Create prompt for refining the video prompt"""
        return f"""
You are refining a video generation prompt based on quality control feedback.

Original Prompt ({original_prompt.generator.upper()}):
{original_prompt.prompt_text}

QC Feedback:
Status: {qc_feedback.qc_status}
Feedback: {qc_feedback.feedback}
Suggestions:
{chr(10).join(f'- {s}' for s in qc_feedback.suggestions)}

Scene Context:
- Scene {scene.scene_number}: {scene.music_section}
- Mood: {scene.mood}
- Camera: {scene.camera_movement}

Style Requirements:
- {style_anchor.style_name}
- {style_anchor.description}

Task:
Revise the prompt to address ALL QC feedback points while:
1. Maintaining the scene's core vision
2. Staying consistent with the style guide
3. Optimizing for {original_prompt.generator.upper()}'s capabilities
4. Being specific and actionable

Refined Prompt:
"""

    async def _save_to_sheets(self, refinement: PromptRefinement) -> bool:
        """Save refinement to Google Sheets"""
        data = [
            refinement.id,
            refinement.original_prompt_id,
            refinement.project_id,
            refinement.scene_id,
            refinement.refined_prompt_text[:500],  # Truncate for sheet
            refinement.refinement_reason[:200],
            "; ".join(refinement.changes_made),
            refinement.qc_feedback_id or "",
            refinement.iteration,
            refinement.created_at.isoformat()
        ]

        return await google_sheet_service.append_row(SHEET_A8_REFINEMENTS, data)


# Singleton instance
agent8_service = Agent8Refiner()
