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
            self.vision_model = None
            return

        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.vision_model = genai.GenerativeModel('gemini-1.5-pro')  # Vision support
            logger.info("Gemini API initialized successfully (text + vision)")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API: {e}")
            self.model = None
            self.vision_model = None

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

    async def analyze_image_style(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg"
    ) -> str:
        """
        Analyze visual style of an image using Gemini Vision

        Args:
            image_bytes: Image file bytes
            mime_type: MIME type (image/jpeg, image/png, etc.)

        Returns:
            Style analysis as prompt suffix
        """
        if not self.vision_model:
            logger.warning("Gemini vision model not initialized. Returning mock style analysis.")
            return "Cinematic look with natural lighting, warm color grading, shallow depth of field, shot on vintage film stock"

        try:
            # Create image part for Gemini
            image_part = {
                "mime_type": mime_type,
                "data": image_bytes
            }

            system_prompt = """You are a professional Colorist and Director of Photography.

Analyze the visual style of this image and extract technical attributes that define its aesthetic.

Focus on:
1. **Lighting**: Type, direction, quality (hard/soft), color temperature
2. **Color Grading**: Dominant colors, contrast, saturation, color palette
3. **Film Stock/Camera Aesthetic**: Digital vs. film look, grain, texture
4. **Depth of Field**: Shallow/deep focus, bokeh characteristics
5. **Composition**: Framing style, visual weight

Your output should be a COMPACT PROMPT SUFFIX (30-50 words) that could be used with a video generator like Veo or Runway.

Format: "shot on [camera/filmstock], [lighting description], [color grading], [mood/aesthetic]"

Example: "shot on CineStill 800T film, soft neon lighting with high contrast, teal and orange color grading, cinematic bokeh, moody urban aesthetic"

Generate ONLY the prompt suffix, no additional explanation."""

            response = self.vision_model.generate_content([
                system_prompt,
                image_part
            ])

            style_suffix = response.text.strip()
            logger.info(f"Gemini Vision analyzed style: {style_suffix[:100]}...")

            return style_suffix

        except Exception as e:
            logger.error(f"Gemini Vision analysis failed: {e}")
            return "Cinematic look with natural lighting, warm color grading, shallow depth of field, shot on vintage film stock"

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
