"""
Agent 2: QC Agent
Quality control for scenes, prompts, and styles
"""

from typing import Optional
from app.models.data_models import QCFeedback, QCRequest
from app.infrastructure.external_services.gemini_service import gemini_service
from app.infrastructure.database.google_sheet_service import google_sheet_service, SHEET_A2_QC_FEEDBACK
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


# Singleton instance
agent2_service = Agent2QC()
