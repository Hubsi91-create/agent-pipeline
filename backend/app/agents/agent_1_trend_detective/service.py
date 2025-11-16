"""
Agent 1: Trend Detective
Identifies current viral music trends for Suno AI prompt generation
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

from app.models.data_models import TrendReport
from app.infrastructure.llm.gemini_service import get_gemini_service
from app.infrastructure.database.google_sheet_service import get_google_sheet_service

logger = logging.getLogger(__name__)


class TrendDetectiveService:
    """
    Agent 1: Trend Detective
    Identifies viral music trends using Gemini AI and stores them in Google Sheets.
    """

    SHEET_NAME = "A1_Trends_DB"

    def __init__(self):
        self.gemini = get_gemini_service()
        self.sheets = get_google_sheet_service()

    def generate_and_store_trend_reports(self, count: int = 5) -> Dict[str, Any]:
        """
        Generate trend reports using Gemini and store them in Google Sheets.

        Args:
            count: Number of trend reports to generate (default: 5)

        Returns:
            Dictionary with operation results
        """
        logger.info(f"Agent 1 starting: Generating {count} trend reports...")

        try:
            # Step 1: Generate trends using Gemini
            trends = self._generate_trends_with_gemini(count)

            if not trends:
                return {
                    "success": False,
                    "message": "No trends generated",
                    "count": 0
                }

            # Step 2: Create TrendReport objects
            trend_reports = []
            for trend_data in trends:
                try:
                    trend_report = TrendReport(
                        genre=trend_data.get("genre", "Unknown"),
                        details=trend_data.get("details", "No details"),
                        viral_potential=trend_data.get("viral_potential", 5)
                    )
                    trend_reports.append(trend_report)
                except Exception as e:
                    logger.warning(f"Error creating TrendReport: {e}. Skipping trend.")
                    continue

            # Step 3: Store in Google Sheets
            stored_count = self._store_trends_in_sheets(trend_reports)

            logger.info(f"Agent 1 completed: Stored {stored_count}/{count} trend reports")

            return {
                "success": True,
                "message": f"Successfully generated and stored {stored_count} trend reports",
                "count": stored_count,
                "trends": [report.model_dump() for report in trend_reports]
            }

        except Exception as e:
            error_msg = f"Agent 1 failed: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "count": 0
            }

    def _generate_trends_with_gemini(self, count: int) -> List[Dict[str, Any]]:
        """
        Use Gemini to generate trend reports.

        Args:
            count: Number of trends to generate

        Returns:
            List of trend dictionaries
        """
        system_prompt = f"""You are Agent 1: Trend Detective.
Your mission is to identify {count} current viral music trends (as of November 2025) that are perfect for Suno AI music generation.

Focus on:
- Emerging genres and sub-genres
- Viral TikTok/Instagram music trends
- Cross-genre fusions
- Production styles that are gaining traction
- Specific sonic characteristics that are trending

For each trend, provide:
- genre: The genre or style name (concise, 2-5 words)
- details: Detailed description including sonic characteristics, typical BPM range, instrumentation, and cultural context (50-100 words)
- viral_potential: Score from 1-10 indicating viral potential (10 = extremely viral)

Return ONLY a valid JSON array of objects matching this structure:
[
  {{
    "genre": "Genre Name",
    "details": "Detailed description...",
    "viral_potential": 8
  }}
]

DO NOT include any markdown formatting, explanations, or extra text. Return ONLY the JSON array."""

        user_prompt = f"Generate {count} current music trends for Suno AI."

        try:
            trends = self.gemini.generate_json(
                prompt=user_prompt,
                system_instruction=system_prompt,
                temperature=0.85
            )

            # Validate it's a list
            if not isinstance(trends, list):
                logger.error("Gemini did not return a list")
                return []

            logger.info(f"Gemini generated {len(trends)} trends")
            return trends

        except Exception as e:
            logger.error(f"Error generating trends with Gemini: {e}")
            return []

    def _store_trends_in_sheets(self, trend_reports: List[TrendReport]) -> int:
        """
        Store trend reports in Google Sheets.

        Args:
            trend_reports: List of TrendReport objects

        Returns:
            Number of successfully stored reports
        """
        stored_count = 0

        try:
            # Batch append for better performance
            data_list = [report.model_dump() for report in trend_reports]
            self.sheets.batch_append(self.SHEET_NAME, data_list)
            stored_count = len(data_list)

        except Exception as e:
            logger.error(f"Error batch storing trends: {e}")
            # Fallback to individual append
            for report in trend_reports:
                try:
                    self.sheets.append_to_sheet(
                        self.SHEET_NAME,
                        report.model_dump()
                    )
                    stored_count += 1
                except Exception as append_error:
                    logger.error(f"Error storing individual trend: {append_error}")
                    continue

        return stored_count


# ============================================================
# SINGLETON INSTANCE
# ============================================================

_trend_detective_service = None


def get_trend_detective_service() -> TrendDetectiveService:
    """Get or create singleton instance of TrendDetectiveService"""
    global _trend_detective_service
    if _trend_detective_service is None:
        _trend_detective_service = TrendDetectiveService()
    return _trend_detective_service
