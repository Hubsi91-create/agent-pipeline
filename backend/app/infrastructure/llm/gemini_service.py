"""
Gemini Service - Vertex AI Integration
Provides LLM capabilities for the 11-Agent System
Optimized for Google Cloud Run deployment
"""

import vertexai
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig
import os
import logging
import json
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class GeminiService:
    """
    Service for interacting with Google's Gemini models via Vertex AI.
    Uses Application Default Credentials for Cloud Run deployment.
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        region: Optional[str] = None,
        model_name: str = "gemini-2.5-pro"
    ):
        """
        Initialize Gemini Service.

        Args:
            project_id: GCP Project ID. If None, reads from GOOGLE_PROJECT_ID env var.
            region: GCP Region. If None, reads from GOOGLE_REGION env var.
            model_name: Gemini model to use (default: gemini-2.5-pro)
        """
        self.project_id = project_id or os.getenv("GOOGLE_PROJECT_ID", "music-agents-prod")
        self.region = region or os.getenv("GOOGLE_REGION", "global")
        self.model_name = model_name
        self.model = None

        self._initialize()

    def _initialize(self):
        """Initialize Vertex AI and load the model"""
        try:
            if self.project_id and self.project_id != "dein-gcp-projekt-id":
                vertexai.init(project=self.project_id, location=self.region)
                self.model = GenerativeModel(self.model_name)
                logger.info(
                    f"Vertex AI (Gemini) initialized: {self.project_id} / {self.region} / {self.model_name}"
                )
            else:
                logger.warning(
                    "Vertex AI (Gemini) NOT initialized. GOOGLE_PROJECT_ID not properly set."
                )
        except Exception as e:
            logger.error(f"CRITICAL ERROR: Could not initialize Vertex AI: {e}")
            raise

    def generate(
        self,
        prompt: str,
        temperature: float = 0.8,
        top_p: float = 0.95,
        max_output_tokens: int = 8192,
        system_instruction: Optional[str] = None
    ) -> str:
        """
        Generate text using Gemini model.

        Args:
            prompt: The user prompt
            temperature: Creativity (0.0 = deterministic, 1.0 = very creative)
            top_p: Nucleus sampling parameter
            max_output_tokens: Maximum tokens in response
            system_instruction: Optional system-level instructions

        Returns:
            Generated text from model

        Raises:
            Exception: If model is not initialized or API call fails
        """
        if self.model is None:
            error_msg = "Gemini model not initialized. Check GOOGLE_PROJECT_ID."
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        try:
            # Combine system instruction with prompt if provided
            full_prompt = prompt
            if system_instruction:
                full_prompt = f"System Instructions:\n{system_instruction}\n\nUser Request:\n{prompt}"

            logger.info(f"Calling Gemini with prompt length: {len(full_prompt)} chars")

            # Create generation config
            config = GenerationConfig(
                temperature=temperature,
                top_p=top_p,
                max_output_tokens=max_output_tokens
            )

            # Generate content with streaming
            response_stream = self.model.generate_content(
                [Part.from_text(full_prompt)],
                generation_config=config,
                stream=True
            )

            # Collect streamed response
            full_text = ""
            for chunk in response_stream:
                try:
                    if chunk.candidates and chunk.candidates[0].content.parts:
                        full_text += chunk.candidates[0].content.parts[0].text
                except (AttributeError, IndexError, ValueError) as e:
                    logger.warning(f"Error processing chunk: {e}")
                    continue

            if full_text:
                logger.info(f"Gemini response received: {len(full_text)} chars")
                return full_text.strip()
            else:
                error_msg = "Gemini stream was empty or in wrong format."
                logger.warning(error_msg)
                raise ValueError(error_msg)

        except Exception as e:
            error_msg = f"Error calling Gemini: {str(e)}"
            logger.error(error_msg)
            raise

    def generate_json(
        self,
        prompt: str,
        temperature: float = 0.8,
        system_instruction: Optional[str] = None
    ) -> Any:
        """
        Generate JSON response from Gemini.
        Includes robust JSON parsing with fallback mechanisms.

        Args:
            prompt: The user prompt (should request JSON output)
            temperature: Creativity parameter
            system_instruction: Optional system-level instructions

        Returns:
            Parsed JSON object (dict or list)

        Raises:
            ValueError: If response is not valid JSON
        """
        response_text = self.generate(
            prompt=prompt,
            temperature=temperature,
            system_instruction=system_instruction
        )

        # Try to parse JSON with multiple strategies
        return self._parse_json_robust(response_text)

    def _parse_json_robust(self, text: str) -> Any:
        """
        Robustly parse JSON from LLM response.
        Handles markdown code blocks and extra whitespace.

        Args:
            text: Raw text from LLM

        Returns:
            Parsed JSON object

        Raises:
            ValueError: If JSON cannot be parsed
        """
        # Remove markdown code blocks if present
        text = text.strip()

        # Try to extract JSON from markdown code blocks
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end != -1:
                text = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            if end != -1:
                text = text[start:end].strip()

        # Try direct JSON parse
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            logger.error(f"Raw text: {text[:500]}...")  # Log first 500 chars
            raise ValueError(f"Failed to parse JSON from Gemini response: {e}")


# ============================================================
# SINGLETON INSTANCE
# ============================================================

_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """
    Get or create singleton instance of GeminiService.

    Returns:
        GeminiService instance
    """
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
