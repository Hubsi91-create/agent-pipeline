"""
Google Gemini AI Service
Singleton service for interacting with Gemini API
"""

import os
import google.generativeai as genai
from typing import Optional
from app.utils.logger import setup_logger

logger = setup_logger("GeminiService")


class GeminiService:
    """Singleton service for Google Gemini AI"""

    _instance: Optional['GeminiService'] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialize()
            self._initialized = True

    def _initialize(self):
        """Initialize Gemini API"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not found. AI features will be limited.")
            self.model = None
            return

        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            logger.info("Gemini API initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API: {e}")
            self.model = None

    async def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """
        Generate text using Gemini

        Args:
            prompt: The prompt to send to Gemini
            temperature: Creativity level (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        if not self.model:
            logger.warning("Gemini model not initialized. Returning mock response.")
            return self._mock_response(prompt)

        try:
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )

            return response.text

        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return self._mock_response(prompt)

    def _mock_response(self, prompt: str) -> str:
        """Generate a mock response when Gemini is unavailable"""
        if "scene breakdown" in prompt.lower():
            return """
            Scene 1 (0:00-0:15): Intro - Dark, moody atmosphere with silhouettes
            Scene 2 (0:15-0:45): Verse 1 - Artist performing, urban setting
            Scene 3 (0:45-1:15): Chorus - Energetic, colorful visuals
            Scene 4 (1:15-1:45): Verse 2 - Narrative storytelling
            Scene 5 (1:45-2:15): Bridge - Abstract, artistic visuals
            Scene 6 (2:15-2:45): Final Chorus - High energy, finale
            """
        elif "style" in prompt.lower():
            return "Cinematic, high-contrast visuals with vibrant colors. Neo-noir aesthetic with modern urban elements."
        elif "prompt" in prompt.lower():
            return "A cinematic music video scene with dramatic lighting, vibrant colors, and dynamic camera movements."
        else:
            return "Generated response (mock mode)"


# Singleton instance
gemini_service = GeminiService()
