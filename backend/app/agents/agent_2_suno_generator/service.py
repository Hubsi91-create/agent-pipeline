"""
Agent 2: Suno Prompt Generator
Generates optimized Suno v5 prompts based on trend reports
Includes Few-Shot Learning from approved best practices
"""

import logging
from typing import List, Dict, Any, Optional

from app.models.data_models import SunoPrompt, TrendReport, ApprovedPrompt
from app.infrastructure.llm.gemini_service import get_gemini_service
from app.infrastructure.database.google_sheet_service import get_google_sheet_service

logger = logging.getLogger(__name__)


class SunoPromptGeneratorService:
    """
    Agent 2: Suno Prompt Generator
    Processes NEW trend reports and generates optimized Suno prompts.
    Uses Few-Shot Learning from approved best practices.
    """

    TRENDS_SHEET = "A1_Trends_DB"
    PROMPTS_SHEET = "A2_GeneratedPrompts_DB"
    BEST_PRACTICES_SHEET = "ApprovedBestPractices"

    def __init__(self):
        self.gemini = get_gemini_service()
        self.sheets = get_google_sheet_service()

    def process_new_trends(self, count_per_trend: int = 10) -> Dict[str, Any]:
        """
        Process all NEW trend reports and generate Suno prompts.

        Args:
            count_per_trend: Number of prompts to generate per trend (default: 10)

        Returns:
            Dictionary with operation results
        """
        logger.info(f"Agent 2 starting: Processing NEW trends ({count_per_trend} prompts per trend)...")

        try:
            # Step 1: Find all NEW trends
            new_trends = self._find_new_trends()

            if not new_trends:
                return {
                    "success": True,
                    "message": "No NEW trends to process",
                    "trends_processed": 0,
                    "prompts_generated": 0
                }

            # Step 2: Load best practices for Few-Shot Learning
            best_practices = self._load_best_practices(limit=15)

            # Step 3: Process each trend
            total_prompts_generated = 0
            trends_processed = 0

            for row_index, trend_data in new_trends:
                try:
                    # Generate prompts for this trend
                    prompts_generated = self._process_single_trend(
                        trend_data=trend_data,
                        count=count_per_trend,
                        best_practices=best_practices
                    )

                    total_prompts_generated += prompts_generated

                    # Mark trend as PROCESSED
                    self.sheets.update_cell(
                        self.TRENDS_SHEET,
                        row_index,
                        'status',
                        'PROCESSED'
                    )

                    trends_processed += 1
                    logger.info(f"Processed trend (row {row_index}): {prompts_generated} prompts generated")

                except Exception as e:
                    logger.error(f"Error processing trend at row {row_index}: {e}")
                    continue

            logger.info(
                f"Agent 2 completed: {trends_processed} trends processed, "
                f"{total_prompts_generated} prompts generated"
            )

            return {
                "success": True,
                "message": f"Processed {trends_processed} trends, generated {total_prompts_generated} prompts",
                "trends_processed": trends_processed,
                "prompts_generated": total_prompts_generated
            }

        except Exception as e:
            error_msg = f"Agent 2 failed: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "trends_processed": 0,
                "prompts_generated": 0
            }

    def _find_new_trends(self) -> List[tuple]:
        """
        Find all trend reports with status 'NEW'.

        Returns:
            List of tuples: (row_index, trend_data)
        """
        try:
            new_trends = self.sheets.find_rows(
                self.TRENDS_SHEET,
                'status',
                'NEW'
            )
            logger.info(f"Found {len(new_trends)} NEW trends")
            return new_trends
        except Exception as e:
            logger.error(f"Error finding NEW trends: {e}")
            return []

    def _load_best_practices(self, limit: int = 15) -> List[str]:
        """
        Load the most recent approved prompts for Few-Shot Learning.

        Args:
            limit: Maximum number of examples to load

        Returns:
            List of approved prompt texts
        """
        try:
            all_practices = self.sheets.read_sheet(self.BEST_PRACTICES_SHEET)

            # Sort by timestamp (most recent first) and take top N
            # Note: timestamp is stored as ISO string, so alphabetical sort works
            sorted_practices = sorted(
                all_practices,
                key=lambda x: x.get('timestamp', ''),
                reverse=True
            )

            best_practices = [
                p.get('prompt_text', '')
                for p in sorted_practices[:limit]
                if p.get('prompt_text')
            ]

            logger.info(f"Loaded {len(best_practices)} best practice examples")
            return best_practices

        except Exception as e:
            logger.warning(f"Could not load best practices: {e}. Proceeding without Few-Shot examples.")
            return []

    def _process_single_trend(
        self,
        trend_data: Dict[str, Any],
        count: int,
        best_practices: List[str]
    ) -> int:
        """
        Process a single trend and generate prompts.

        Args:
            trend_data: Trend data dictionary
            count: Number of prompts to generate
            best_practices: List of approved prompt examples

        Returns:
            Number of prompts successfully generated
        """
        trend_id = trend_data.get('id')
        genre = trend_data.get('genre', 'Unknown')
        details = trend_data.get('details', 'No details')

        logger.info(f"Generating {count} prompts for trend: {genre}")

        # Build Few-Shot examples section
        few_shot_section = ""
        if best_practices:
            examples_text = "\n\n".join([f"Example {i+1}:\n{ex}" for i, ex in enumerate(best_practices[:5])])
            few_shot_section = f"""
Use these Best Practice examples as reference (Few-Shot Learning):
{examples_text}

Your generated prompts should follow similar structure, detail level, and quality.
"""

        # Build system prompt
        system_prompt = f"""You are Agent 2: Suno Prompt Generator.
Your mission is to create {count} optimized prompts for Suno v5 Custom Mode.

Context - Trend Report:
Genre: {genre}
Details: {details}

Requirements for each prompt:
- Length: 70-100 words
- Include specific instrumentation, BPM, production techniques
- Reference sonic characteristics and mood
- Use vivid, technical language
- Optimized for Suno v5 API
{few_shot_section}

Return ONLY a valid JSON array of strings (just the prompt texts):
["prompt 1 text...", "prompt 2 text...", ...]

DO NOT include explanations, markdown, or extra text. Return ONLY the JSON array of prompt strings."""

        user_prompt = f"Generate {count} Suno prompts for the {genre} trend."

        try:
            # Generate prompts with Gemini
            prompts_list = self.gemini.generate_json(
                prompt=user_prompt,
                system_instruction=system_prompt,
                temperature=0.85
            )

            # Validate it's a list of strings
            if not isinstance(prompts_list, list):
                logger.error("Gemini did not return a list")
                return 0

            # Create SunoPrompt objects and store them
            suno_prompts = []
            for prompt_text in prompts_list:
                if isinstance(prompt_text, str) and len(prompt_text) > 20:
                    suno_prompt = SunoPrompt(
                        trend_id=trend_id,
                        prompt_text=prompt_text,
                        status='PENDING_QC'
                    )
                    suno_prompts.append(suno_prompt)

            # Store in Google Sheets
            if suno_prompts:
                data_list = [p.model_dump() for p in suno_prompts]
                self.sheets.batch_append(self.PROMPTS_SHEET, data_list)
                logger.info(f"Stored {len(suno_prompts)} prompts for trend {trend_id}")
                return len(suno_prompts)
            else:
                return 0

        except Exception as e:
            logger.error(f"Error generating prompts for trend {trend_id}: {e}")
            return 0


# ============================================================
# SINGLETON INSTANCE
# ============================================================

_suno_generator_service = None


def get_suno_generator_service() -> SunoPromptGeneratorService:
    """Get or create singleton instance of SunoPromptGeneratorService"""
    global _suno_generator_service
    if _suno_generator_service is None:
        _suno_generator_service = SunoPromptGeneratorService()
    return _suno_generator_service
