"""
Google Gemini AI Service
Singleton service for interacting with Gemini API (Text, Vision, Image Generation)
"""

import os
import base64
import google.generativeai as genai
from typing import Optional, Dict, Any
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
            self.imagen_model = None
            return

        try:
            genai.configure(api_key=api_key)
            # Use gemini-3.0-pro for better tool support (including Google Search Grounding)
            self.model = genai.GenerativeModel('gemini-3.0-pro')
            self.vision_model = genai.GenerativeModel('gemini-3.0-pro')  # Vision support

            # Try to initialize Imagen model (if available in API)
            try:
                # Imagen 3.0 model for image generation
                self.imagen_model = genai.ImageGenerationModel("imagen-3.0-generate-001")
                logger.info("Gemini API initialized successfully (text + vision + imagen)")
            except (AttributeError, Exception) as img_err:
                logger.warning(f"Imagen model not available: {img_err}. Image generation will use mock mode.")
                self.imagen_model = None
                logger.info("Gemini API initialized successfully (text + vision only)")

        except Exception as e:
            logger.error(f"Failed to initialize Gemini API: {e}")
            self.model = None
            self.vision_model = None
            self.imagen_model = None

    async def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        use_search: bool = False
    ) -> str:
        """
        Generate text using Gemini

        Args:
            prompt: The prompt to send to Gemini
            temperature: Creativity level (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            use_search: If True, enables Google Search Grounding for real-time web data

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

            # Configure Google Search Grounding if requested
            tools = None
            if use_search:
                try:
                    # Google Search Grounding for real-time web data
                    from google.generativeai import protos
                    tools = [protos.Tool(google_search_retrieval=protos.GoogleSearchRetrieval())]
                    logger.info("Google Search Grounding enabled for this request")
                except Exception as search_err:
                    logger.warning(f"Could not enable Google Search Grounding: {search_err}")
                    tools = None

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                tools=tools
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

    async def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "1:1",
        number_of_images: int = 1
    ) -> Dict[str, Any]:
        """
        Generate image using Imagen 3.0 / Imagen 4

        Args:
            prompt: Text description of the image to generate
            aspect_ratio: Image aspect ratio ("1:1", "16:9", "9:16", "4:3", "3:4")
            number_of_images: Number of images to generate (1-4)

        Returns:
            Dict with:
            - success: bool
            - images: list of base64-encoded images
            - prompt: original prompt
            - model: model name used
        """
        if not self.imagen_model:
            logger.warning("Imagen model not available. Returning placeholder image.")
            return self._generate_placeholder_image(prompt, aspect_ratio)

        try:
            logger.info(f"Generating image with Imagen: {prompt[:100]}...")

            # Generate image with Imagen
            result = self.imagen_model.generate_images(
                prompt=prompt,
                number_of_images=number_of_images,
                aspect_ratio=aspect_ratio,
                safety_filter_level="block_few",  # Moderate safety filter
                person_generation="allow_adult"   # Allow people in images
            )

            # Convert images to base64
            images_base64 = []
            for img in result.images:
                # Get image bytes
                img_bytes = img._pil_image.tobytes() if hasattr(img, '_pil_image') else img.data

                # Encode to base64
                img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                images_base64.append(img_base64)

            logger.info(f"Successfully generated {len(images_base64)} image(s) with Imagen")

            return {
                "success": True,
                "images": images_base64,
                "prompt": prompt,
                "model": "imagen-3.0-generate-001",
                "aspect_ratio": aspect_ratio
            }

        except Exception as e:
            logger.error(f"Imagen generation failed: {e}")
            return self._generate_placeholder_image(prompt, aspect_ratio)

    def _generate_placeholder_image(self, prompt: str, aspect_ratio: str) -> Dict[str, Any]:
        """
        Generate a placeholder image when Imagen is not available

        Creates a simple base64-encoded SVG placeholder
        """
        logger.info("Generating placeholder image (Imagen not available)")

        # Determine dimensions based on aspect ratio
        dimensions = {
            "1:1": (512, 512),
            "16:9": (768, 432),
            "9:16": (432, 768),
            "4:3": (640, 480),
            "3:4": (480, 640)
        }
        width, height = dimensions.get(aspect_ratio, (512, 512))

        # Create SVG placeholder
        svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="100%" height="100%" fill="url(#grad1)"/>
  <text x="50%" y="45%" font-family="Arial, sans-serif" font-size="20" fill="white" text-anchor="middle" opacity="0.9">
    AI Generated Style
  </text>
  <text x="50%" y="55%" font-family="Arial, sans-serif" font-size="14" fill="white" text-anchor="middle" opacity="0.7">
    {prompt[:50]}{"..." if len(prompt) > 50 else ""}
  </text>
  <text x="50%" y="65%" font-family="Arial, sans-serif" font-size="12" fill="white" text-anchor="middle" opacity="0.5">
    (Placeholder - Imagen not configured)
  </text>
</svg>'''

        # Encode SVG to base64
        svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')

        return {
            "success": False,
            "images": [svg_base64],
            "prompt": prompt,
            "model": "placeholder",
            "aspect_ratio": aspect_ratio,
            "note": "Placeholder image generated. Configure GEMINI_API_KEY with Imagen access for real image generation."
        }

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
