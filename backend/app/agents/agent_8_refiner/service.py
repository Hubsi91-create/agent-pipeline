"""
Agent 8: QC Refiner - "The Quality Controller"
Validates and auto-corrects video prompts for Veo and Runway
"""

from typing import Optional, Dict, Any, List
from app.infrastructure.database.google_sheet_service import (
    google_sheet_service,
    SHEET_A5_STYLE_DATABASE
)
from app.utils.logger import setup_logger
import re

logger = setup_logger("Agent8_QCRefiner")


class Agent8QCRefiner:
    """Singleton service for prompt validation and auto-correction"""

    _instance: Optional['Agent8QCRefiner'] = None
    _negative_keywords_cache: Optional[List[str]] = None

    # Platform-specific limits
    MAX_LENGTH_VEO = 500
    MAX_LENGTH_RUNWAY = 300

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def validate_prompt(
        self,
        prompt_dict: Dict[str, Any],
        style: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Validate and auto-correct a video prompt

        Args:
            prompt_dict: Prompt dict with 'prompt', 'model', 'negative', 'scene_id'
            style: Style dict with 'name', 'suffix', 'negative' (optional)

        Returns:
            Dict with:
            - status: "valid", "corrected", or "error"
            - prompt: Original or corrected prompt text
            - negative: Negative prompt
            - model: Model type
            - scene_id: Scene ID
            - issues_found: List of issues detected
            - corrections_made: List of corrections applied
        """
        logger.info(f"Validating prompt for model '{prompt_dict.get('model', 'unknown')}'")

        issues_found = []
        corrections_made = []
        prompt_text = prompt_dict.get("prompt", "")
        model = prompt_dict.get("model", "veo").lower()
        negative_prompt = prompt_dict.get("negative", "")

        # Issue 1: Check length limits
        max_length = self.MAX_LENGTH_VEO if model == "veo" else self.MAX_LENGTH_RUNWAY
        if len(prompt_text) > max_length:
            issues_found.append(f"Prompt too long ({len(prompt_text)} chars, max {max_length})")
            prompt_text = prompt_text[:max_length - 3] + "..."
            corrections_made.append(f"Trimmed to {max_length} characters")
            logger.warning(f"Trimmed prompt from {len(prompt_dict.get('prompt', ''))} to {max_length} chars")

        # Issue 2: Check for negative/forbidden keywords from style
        if style and style.get("negative"):
            forbidden_words = await self._extract_forbidden_keywords(style.get("negative", ""))

            for word in forbidden_words:
                # Case-insensitive search
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                if pattern.search(prompt_text):
                    issues_found.append(f"Contains forbidden keyword: '{word}'")
                    # Remove the word (with surrounding spaces cleaned up)
                    prompt_text = pattern.sub("", prompt_text)
                    # Clean up multiple spaces
                    prompt_text = re.sub(r'\s+', ' ', prompt_text).strip()
                    # Clean up orphaned commas
                    prompt_text = re.sub(r',\s*,', ',', prompt_text)
                    prompt_text = re.sub(r'^\s*,|,\s*$', '', prompt_text).strip()
                    corrections_made.append(f"Removed forbidden keyword: '{word}'")
                    logger.info(f"Removed forbidden keyword: '{word}'")

        # Issue 3: Basic quality checks
        if len(prompt_text.strip()) < 20:
            issues_found.append("Prompt too short (less than 20 characters)")
            logger.error("Prompt is too short after corrections")

        # Issue 4: Check for common prompt anti-patterns
        antipatterns = [
            (r'\b(ugly|bad|worst|horrible)\b', "negative descriptors"),
            (r'\b(NSFW|nude|naked)\b', "inappropriate content"),
        ]

        for pattern, description in antipatterns:
            if re.search(pattern, prompt_text, re.IGNORECASE):
                issues_found.append(f"Contains {description}")
                prompt_text = re.sub(pattern, "", prompt_text, flags=re.IGNORECASE)
                prompt_text = re.sub(r'\s+', ' ', prompt_text).strip()
                corrections_made.append(f"Removed {description}")
                logger.info(f"Removed {description}")

        # Determine status
        if len(issues_found) == 0:
            status = "valid"
            logger.info("✅ Prompt passed all validation checks")
        elif len(corrections_made) > 0 and len(prompt_text.strip()) >= 20:
            status = "corrected"
            logger.info(f"⚠️ Prompt corrected ({len(corrections_made)} fixes applied)")
        else:
            status = "error"
            logger.error(f"❌ Prompt validation failed with {len(issues_found)} critical issues")

        return {
            "status": status,
            "prompt": prompt_text,
            "negative": negative_prompt,
            "model": model,
            "scene_id": prompt_dict.get("scene_id"),
            "duration": prompt_dict.get("duration"),
            "issues_found": issues_found,
            "corrections_made": corrections_made
        }

    async def validate_batch(
        self,
        prompts: List[Dict[str, Any]],
        style: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Validate multiple prompts at once

        Args:
            prompts: List of prompt dicts
            style: Style dict (optional)

        Returns:
            Dict with:
            - total: Total prompts processed
            - valid: Number of valid prompts
            - corrected: Number of corrected prompts
            - errors: Number of failed prompts
            - results: List of validated prompt dicts
        """
        logger.info(f"Batch validating {len(prompts)} prompts")

        results = []
        stats = {"valid": 0, "corrected": 0, "errors": 0}

        for prompt_dict in prompts:
            validated = await self.validate_prompt(prompt_dict, style)
            results.append(validated)

            # Update stats
            stats[validated["status"]] = stats.get(validated["status"], 0) + 1

        logger.info(f"Batch validation complete: {stats['valid']} valid, {stats['corrected']} corrected, {stats['errors']} errors")

        return {
            "total": len(prompts),
            "valid": stats["valid"],
            "corrected": stats["corrected"],
            "errors": stats["errors"],
            "results": results
        }

    async def _extract_forbidden_keywords(self, negative_prompt: str) -> List[str]:
        """
        Extract individual forbidden keywords from negative prompt string

        Args:
            negative_prompt: Comma or space-separated negative keywords

        Returns:
            List of forbidden keywords
        """
        if not negative_prompt:
            return []

        # Split by commas and clean up
        keywords = [
            keyword.strip()
            for keyword in negative_prompt.replace(",", " ").split()
            if keyword.strip() and len(keyword.strip()) > 2  # Ignore very short words
        ]

        return keywords

    async def get_style_negative_keywords(self, style_name: str) -> List[str]:
        """
        Get negative keywords for a specific style from A5_Style_Database

        Args:
            style_name: Name of the style

        Returns:
            List of negative keywords
        """
        try:
            records = await google_sheet_service.get_all_records(SHEET_A5_STYLE_DATABASE)

            for record in records:
                if record.get("name") == style_name:
                    negative = record.get("negative", "")
                    return await self._extract_forbidden_keywords(negative)

        except Exception as e:
            logger.warning(f"Could not load style negative keywords: {e}")

        return []


# Singleton instance
agent8_service = Agent8QCRefiner()
