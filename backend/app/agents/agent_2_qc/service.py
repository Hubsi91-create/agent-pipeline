"""
Agent 2: QC Agent
Quality control for scenes, prompts, and styles
Includes auto-learning feedback loop for Few-Shot Learning
"""

from typing import Optional
from datetime import datetime
from app.models.data_models import QCFeedback, QCRequest, SunoPromptResponse, SunoPromptExample
from app.infrastructure.external_services.gemini_service import gemini_service
from app.infrastructure.database.google_sheet_service import (
    google_sheet_service,
    SHEET_A2_QC_FEEDBACK,
    SHEET_APPROVED_BEST_PRACTICES
)
from app.utils.logger import setup_logger

logger = setup_logger("Agent2_QC")


class Agent2QC:
    """Singleton service for quality control"""

    _instance: Optional['Agent2QC'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def review_content(self, qc_request: QCRequest) -> QCFeedback:
        """
        Review content and provide QC feedback

        Args:
            qc_request: QC review request

        Returns:
            QC feedback
        """
        logger.info(f"Reviewing {qc_request.target_type}: {qc_request.target_id}")

        # Create prompt for Gemini
        prompt = self._create_qc_prompt(qc_request)

        # Get AI feedback
        ai_response = await gemini_service.generate_text(prompt, temperature=0.3)

        # Parse response and determine status
        qc_status, feedback, suggestions = self._parse_qc_response(ai_response)

        # Create feedback
        qc_feedback = QCFeedback(
            project_id=qc_request.project_id,
            target_id=qc_request.target_id,
            target_type=qc_request.target_type,
            qc_status=qc_status,
            feedback=feedback,
            suggestions=suggestions
        )

        # Save to Google Sheets
        await self._save_to_sheets(qc_feedback)

        logger.info(f"QC Review complete: {qc_status}")
        return qc_feedback

    def _create_qc_prompt(self, qc_request: QCRequest) -> str:
        """Create QC prompt for Gemini"""
        return f"""
You are a quality control agent for music video production.

Review the following {qc_request.target_type}:

{qc_request.content}

Provide feedback in this format:
STATUS: [APPROVED/NEEDS_REVISION/REJECTED]
FEEDBACK: [Your detailed feedback]
SUGGESTIONS: [Bullet points of specific improvements if needed]

Be specific and actionable in your feedback.
"""

    def _parse_qc_response(self, response: str) -> tuple[str, str, list[str]]:
        """Parse Gemini's QC response"""
        lines = response.strip().split('\n')

        status = "NEEDS_REVISION"  # Default
        feedback = ""
        suggestions = []

        for line in lines:
            if line.startswith("STATUS:"):
                status_text = line.replace("STATUS:", "").strip()
                if "APPROVED" in status_text.upper():
                    status = "APPROVED"
                elif "REJECTED" in status_text.upper():
                    status = "REJECTED"
            elif line.startswith("FEEDBACK:"):
                feedback = line.replace("FEEDBACK:", "").strip()
            elif line.startswith("-") or line.startswith("*"):
                suggestions.append(line.lstrip("-* ").strip())

        if not feedback:
            feedback = response

        return status, feedback, suggestions

    async def _save_to_sheets(self, qc_feedback: QCFeedback) -> bool:
        """Save QC feedback to Google Sheets"""
        data = [
            qc_feedback.id,
            qc_feedback.project_id,
            qc_feedback.target_id,
            qc_feedback.target_type,
            qc_feedback.qc_status,
            qc_feedback.feedback,
            "; ".join(qc_feedback.suggestions),
            qc_feedback.iteration,
            qc_feedback.created_at.isoformat()
        ]

        return await google_sheet_service.append_row(SHEET_A2_QC_FEEDBACK, data)

    async def review_suno_prompt(
        self,
        suno_prompt: SunoPromptResponse,
        auto_add_to_best_practices: bool = True
    ) -> QCFeedback:
        """
        Review a Suno prompt with auto-learning feedback loop

        This method implements the "learning" mechanism:
        1. QC reviews the prompt
        2. Extracts a quality score (0-10)
        3. If score >= 7.0 AND auto_add_to_best_practices is True:
           -> Automatically adds to ApprovedBestPractices sheet
           -> This makes it available for Few-Shot Learning in future generations

        Args:
            suno_prompt: The Suno prompt to review
            auto_add_to_best_practices: Auto-add if high quality (default: True)

        Returns:
            QC feedback with quality score
        """
        logger.info(f"QC reviewing Suno prompt {suno_prompt.id}")

        # Create QC prompt for Gemini
        qc_prompt = f"""
You are a quality control expert for Suno v5 music prompts.

Evaluate the following Suno prompt on a scale of 0-10:

PROMPT:
{suno_prompt.prompt_text}

CONTEXT:
- Genre: {suno_prompt.genre}
- Mood: {suno_prompt.mood or 'Not specified'}
- Tempo: {suno_prompt.tempo or 'Not specified'}

EVALUATION CRITERIA (score each 0-10):
1. Structure clarity (proper [Verse], [Chorus], [Bridge] markers)
2. Imagery and sensory details
3. Emotional impact
4. Language quality and flow
5. Genre appropriateness
6. Originality
7. Commercial viability

Provide your response in this EXACT format:
SCORE: [0-10 number]
FEEDBACK: [Your detailed feedback]
STRENGTHS: [Bullet points]
IMPROVEMENTS: [Bullet points if score < 8]

Be honest and critical. Only scores >= 7 will be used for training.
"""

        # Get Gemini's review
        ai_response = await gemini_service.generate_text(qc_prompt, temperature=0.3)

        # Parse response
        quality_score, feedback, suggestions = self._parse_suno_qc_response(ai_response)

        # Determine status
        if quality_score >= 8.0:
            qc_status = "APPROVED"
        elif quality_score >= 6.0:
            qc_status = "NEEDS_REVISION"
        else:
            qc_status = "REJECTED"

        # Create QC feedback
        qc_feedback = QCFeedback(
            project_id=suno_prompt.metadata.get("project_id", "suno-standalone"),
            target_id=suno_prompt.id,
            target_type="suno_prompt",
            qc_status=qc_status,
            feedback=f"Quality Score: {quality_score}/10. {feedback}",
            suggestions=suggestions
        )

        # Save to QC sheet
        await self._save_to_sheets(qc_feedback)

        # AUTO-LEARNING FEEDBACK LOOP
        # If high quality, add to ApprovedBestPractices for Few-Shot Learning
        if quality_score >= 7.0 and auto_add_to_best_practices:
            await self._add_to_best_practices(suno_prompt, quality_score)
            logger.info(f"✓ Added prompt {suno_prompt.id} to ApprovedBestPractices (Score: {quality_score})")

        logger.info(f"QC complete: {qc_status} (Score: {quality_score}/10)")
        return qc_feedback

    def _parse_suno_qc_response(self, response: str) -> tuple[float, str, list[str]]:
        """Parse Gemini's Suno QC response to extract score and feedback"""
        lines = response.strip().split('\n')

        quality_score = 5.0  # Default middle score
        feedback = ""
        suggestions = []

        for line in lines:
            line = line.strip()

            # Extract score
            if line.startswith("SCORE:"):
                score_text = line.replace("SCORE:", "").strip()
                try:
                    # Handle formats like "8.5/10" or just "8.5"
                    score_text = score_text.split('/')[0].strip()
                    quality_score = float(score_text)
                    quality_score = max(0.0, min(10.0, quality_score))  # Clamp 0-10
                except:
                    pass

            # Extract feedback
            elif line.startswith("FEEDBACK:"):
                feedback = line.replace("FEEDBACK:", "").strip()

            # Extract suggestions
            elif line.startswith("IMPROVEMENTS:") or line.startswith("STRENGTHS:"):
                continue  # Skip headers
            elif line.startswith("-") or line.startswith("*"):
                suggestions.append(line.lstrip("-* ").strip())

        if not feedback:
            feedback = response  # Use full response if parsing fails

        return quality_score, feedback, suggestions

    async def _add_to_best_practices(
        self,
        suno_prompt: SunoPromptResponse,
        quality_score: float
    ) -> bool:
        """
        Add high-quality prompt to ApprovedBestPractices sheet

        This is the "learning" mechanism - excellent prompts become
        Few-Shot examples for future generations.
        """
        try:
            # Create SunoPromptExample
            example = SunoPromptExample(
                id=suno_prompt.id,
                prompt_text=suno_prompt.prompt_text,
                genre=suno_prompt.genre,
                quality_score=quality_score,
                performance_metrics=suno_prompt.metadata.get("performance", {}),
                tags=[suno_prompt.mood or "", suno_prompt.tempo or ""],
                created_at=datetime.utcnow(),
                source="qc_approved"
            )

            # Save to ApprovedBestPractices sheet
            data = [
                example.id,
                example.prompt_text[:500],  # Truncate for sheet
                example.genre,
                example.quality_score,
                ",".join(example.tags),
                example.source,
                example.created_at.isoformat()
            ]

            success = await google_sheet_service.append_row(
                SHEET_APPROVED_BEST_PRACTICES,
                data
            )

            if success:
                logger.info(f"✓ Prompt added to knowledge base for Few-Shot Learning")
            else:
                logger.warning(f"Failed to add prompt to ApprovedBestPractices")

            return success

        except Exception as e:
            logger.error(f"Failed to add to best practices: {e}")
            return False


# Singleton instance
agent2_service = Agent2QC()
