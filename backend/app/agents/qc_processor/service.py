"""
QC Processor: Quality Control & Feedback Loop
Evaluates generated Suno prompts and implements Few-Shot Learning
"""

import logging
from typing import List, Dict, Any, Optional

from app.models.data_models import QCResult, ApprovedPrompt
from app.infrastructure.llm.gemini_service import get_gemini_service
from app.infrastructure.database.google_sheet_service import get_google_sheet_service

logger = logging.getLogger(__name__)


class QCProcessorService:
    """
    Quality Control Processor
    Evaluates prompts in the QC queue and implements the feedback loop
    for Few-Shot Learning (Concept 3).
    """

    PROMPTS_SHEET = "A2_GeneratedPrompts_DB"
    QC_RESULTS_SHEET = "QC_Results_DB"
    BEST_PRACTICES_SHEET = "ApprovedBestPractices"

    # QC approval threshold
    APPROVAL_THRESHOLD = 7

    def __init__(self):
        self.gemini = get_gemini_service()
        self.sheets = get_google_sheet_service()

    def process_queue(self) -> Dict[str, Any]:
        """
        Process all prompts with status 'PENDING_QC'.
        Evaluates each prompt, stores results, and adds high-scoring prompts
        to best practices for Few-Shot Learning.

        Returns:
            Dictionary with processing summary
        """
        logger.info("QC Processor starting: Processing PENDING_QC queue...")

        try:
            # Step 1: Find all PENDING_QC prompts
            pending_prompts = self._find_pending_prompts()

            if not pending_prompts:
                return {
                    "success": True,
                    "message": "No prompts in QC queue",
                    "processed": 0,
                    "approved": 0,
                    "failed": 0
                }

            # Step 2: Process each prompt
            processed = 0
            approved = 0
            failed = 0

            for row_index, prompt_data in pending_prompts:
                try:
                    result = self._process_single_prompt(row_index, prompt_data)

                    processed += 1
                    if result == "approved":
                        approved += 1
                    elif result == "failed":
                        failed += 1

                except Exception as e:
                    logger.error(f"Error processing prompt at row {row_index}: {e}")
                    failed += 1
                    # Mark as FAILED
                    try:
                        self.sheets.update_cell(
                            self.PROMPTS_SHEET,
                            row_index,
                            'status',
                            'FAILED'
                        )
                    except:
                        pass
                    continue

            logger.info(
                f"QC Processor completed: Processed={processed}, "
                f"Approved={approved}, Failed={failed}"
            )

            return {
                "success": True,
                "message": f"QC processing complete",
                "processed": processed,
                "approved": approved,
                "failed": failed
            }

        except Exception as e:
            error_msg = f"QC Processor failed: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "processed": 0,
                "approved": 0,
                "failed": 0
            }

    def _find_pending_prompts(self) -> List[tuple]:
        """
        Find all prompts with status 'PENDING_QC'.

        Returns:
            List of tuples: (row_index, prompt_data)
        """
        try:
            pending = self.sheets.find_rows(
                self.PROMPTS_SHEET,
                'status',
                'PENDING_QC'
            )
            logger.info(f"Found {len(pending)} prompts in PENDING_QC queue")
            return pending
        except Exception as e:
            logger.error(f"Error finding PENDING_QC prompts: {e}")
            return []

    def _process_single_prompt(
        self,
        row_index: int,
        prompt_data: Dict[str, Any]
    ) -> str:
        """
        Process a single prompt through QC evaluation.

        Args:
            row_index: Row index in the sheet
            prompt_data: Prompt data dictionary

        Returns:
            Result status: "approved", "reviewed", or "failed"
        """
        prompt_id = prompt_data.get('id')
        prompt_text = prompt_data.get('prompt_text', '')

        if not prompt_text:
            logger.warning(f"Empty prompt at row {row_index}, marking as FAILED")
            self.sheets.update_cell(self.PROMPTS_SHEET, row_index, 'status', 'FAILED')
            return "failed"

        # Step 1: Evaluate the prompt
        evaluation = self._evaluate_prompt(prompt_text)

        if not evaluation:
            logger.error(f"Evaluation failed for prompt {prompt_id}")
            self.sheets.update_cell(self.PROMPTS_SHEET, row_index, 'status', 'FAILED')
            return "failed"

        score = evaluation.get('score', 0)
        feedback = evaluation.get('feedback', 'No feedback')

        # Step 2: Store QC Result
        qc_result = QCResult(
            prompt_id=prompt_id,
            score=score,
            feedback=feedback
        )

        try:
            self.sheets.append_to_sheet(
                self.QC_RESULTS_SHEET,
                qc_result.model_dump()
            )
        except Exception as e:
            logger.error(f"Error storing QC result: {e}")

        # Step 3: Feedback Loop - Add to Best Practices if score >= threshold
        if score >= self.APPROVAL_THRESHOLD:
            try:
                approved_prompt = ApprovedPrompt(
                    prompt_text=prompt_text,
                    score=score,
                    source='Generated'
                )

                self.sheets.append_to_sheet(
                    self.BEST_PRACTICES_SHEET,
                    approved_prompt.model_dump()
                )

                logger.info(f"Prompt {prompt_id} approved (score: {score}) and added to best practices")

            except Exception as e:
                logger.error(f"Error adding to best practices: {e}")

        # Step 4: Update prompt status
        try:
            self.sheets.update_cell(
                self.PROMPTS_SHEET,
                row_index,
                'status',
                'REVIEWED'
            )
        except Exception as e:
            logger.error(f"Error updating prompt status: {e}")

        return "approved" if score >= self.APPROVAL_THRESHOLD else "reviewed"

    def _evaluate_prompt(self, prompt_text: str) -> Optional[Dict[str, Any]]:
        """
        Evaluate a prompt using Gemini AI.

        Args:
            prompt_text: The Suno prompt to evaluate

        Returns:
            Dictionary with 'score' and 'feedback', or None if evaluation fails
        """
        system_prompt = """You are a Quality Control Agent for Suno v5 music generation prompts.

Evaluate the prompt based on these criteria:
1. Genre Authenticity (25%): Does it accurately represent the genre?
2. Structure & Length (25%): Is it 70-100 words with good structure?
3. Technical Detail (25%): Does it include specific instrumentation, BPM, production details?
4. Originality & Creativity (25%): Is it creative and likely to produce unique music?

Provide:
- score: Integer from 1-10 (10 = excellent, ready for production)
- feedback: One concise sentence explaining the score

Return ONLY valid JSON in this exact format:
{"score": <int>, "feedback": "<string>"}

DO NOT include explanations, markdown, or extra text."""

        user_prompt = f"""Evaluate this Suno prompt:

{prompt_text}"""

        try:
            evaluation = self.gemini.generate_json(
                prompt=user_prompt,
                system_instruction=system_prompt,
                temperature=0.3  # Lower temperature for consistent evaluation
            )

            # Validate structure
            if isinstance(evaluation, dict) and 'score' in evaluation and 'feedback' in evaluation:
                # Ensure score is valid integer
                score = int(evaluation['score'])
                if 1 <= score <= 10:
                    return {
                        'score': score,
                        'feedback': str(evaluation['feedback'])
                    }

            logger.error(f"Invalid evaluation format: {evaluation}")
            return None

        except Exception as e:
            logger.error(f"Error evaluating prompt: {e}")
            return None


# ============================================================
# SINGLETON INSTANCE
# ============================================================

_qc_processor_service = None


def get_qc_processor_service() -> QCProcessorService:
    """Get or create singleton instance of QCProcessorService"""
    global _qc_processor_service
    if _qc_processor_service is None:
        _qc_processor_service = QCProcessorService()
    return _qc_processor_service
