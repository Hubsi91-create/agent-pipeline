"""
Agent 5: Style Anchors & Visual Learning
"The Art Director" - Ensures visual consistency and learns new styles from images
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from app.infrastructure.external_services.gemini_service import gemini_service
from app.infrastructure.database.google_sheet_service import (
    google_sheet_service,
    SHEET_A5_STYLE_DATABASE
)
from app.utils.logger import setup_logger

logger = setup_logger("Agent5_StyleAnchors")


class Agent5StyleAnchors:
    """Singleton service for style management and visual learning"""

    _instance: Optional['Agent5StyleAnchors'] = None
    _styles_cache: Optional[List[Dict[str, str]]] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def get_available_styles(self) -> List[Dict[str, str]]:
        """
        Get all available style presets from A5_Style_Database

        Returns:
            List of style dictionaries with:
            - name: Style name (e.g., "CineStill 800T")
            - suffix: Prompt suffix for video generation
            - negative: Negative prompt (optional)
            - description: Human-readable description (optional)
        """
        logger.info("Fetching available style presets")

        # Check cache first
        if self._styles_cache:
            logger.info(f"Using cached styles ({len(self._styles_cache)} entries)")
            return self._styles_cache

        try:
            records = await google_sheet_service.get_all_records(SHEET_A5_STYLE_DATABASE)

            if records and len(records) > 0:
                logger.info(f"Loaded {len(records)} styles from database")

                styles = []
                for record in records:
                    styles.append({
                        "name": record.get("name", "Unknown Style"),
                        "suffix": record.get("suffix", ""),
                        "negative": record.get("negative", ""),
                        "description": record.get("description", ""),
                        "created_at": record.get("created_at", "")
                    })

                # Cache results
                self._styles_cache = styles
                return styles

        except Exception as e:
            logger.warning(f"Could not load styles from database: {e}")

        # Fallback: Default style presets
        logger.info("Using fallback style presets")
        fallback_styles = [
            {
                "name": "CineStill 800T",
                "suffix": "shot on CineStill 800T film, soft neon lighting with high contrast, teal and orange color grading, cinematic bokeh, moody urban aesthetic",
                "negative": "oversaturated, blown highlights, poor grain structure",
                "description": "Tungsten-balanced film with characteristic red halation around light sources"
            },
            {
                "name": "Portra 400",
                "suffix": "shot on Kodak Portra 400 film, natural soft lighting, warm skin tones, pastel colors, fine grain, professional portrait aesthetic",
                "negative": "harsh shadows, oversaturated colors, digital look",
                "description": "Professional portrait film known for accurate skin tones and fine grain"
            },
            {
                "name": "Blade Runner 2049",
                "suffix": "cinematography inspired by Blade Runner 2049, dramatic side lighting, deep orange and teal color grading, volumetric fog, ultra-wide composition, desolate futuristic aesthetic",
                "negative": "bright lighting, flat colors, cluttered composition",
                "description": "Denis Villeneuve's neo-noir sci-fi aesthetic with Roger Deakins cinematography"
            },
            {
                "name": "Music Video - Neon",
                "suffix": "music video aesthetic, vibrant neon lights, high contrast, fast cuts, dynamic camera movements, colorful gels, club lighting, energetic urban vibe",
                "negative": "static shots, muted colors, slow pacing",
                "description": "High-energy music video style with neon club aesthetics"
            },
            {
                "name": "Analog VHS",
                "suffix": "shot on VHS camcorder, analog video artifacts, color bleeding, scan lines, vintage 80s/90s home video aesthetic, nostalgic lo-fi look",
                "negative": "sharp digital, clean image, modern look",
                "description": "Retro VHS aesthetic with characteristic artifacts and degradation"
            },
            {
                "name": "Anamorphic Flares",
                "suffix": "shot with anamorphic lenses, horizontal lens flares, 2.39:1 aspect ratio, shallow depth of field, creamy bokeh, cinematic widescreen aesthetic",
                "negative": "spherical bokeh, no lens character, flat image",
                "description": "Widescreen cinematic look with characteristic anamorphic lens flares"
            },
            {
                "name": "Noir Shadow Play",
                "suffix": "film noir cinematography, dramatic chiaroscuro lighting, venetian blind shadows, high contrast black and white aesthetic, moody crime thriller style",
                "negative": "flat lighting, color footage, low contrast",
                "description": "Classic film noir with dramatic shadow play and high contrast"
            },
            {
                "name": "Golden Hour Natural",
                "suffix": "shot during golden hour, warm natural sunlight, soft shadows, rich golden tones, shallow depth of field, organic bokeh, dreamy cinematic aesthetic",
                "negative": "artificial lighting, harsh shadows, cool tones",
                "description": "Natural golden hour cinematography with warm, soft light"
            }
        ]

        self._styles_cache = fallback_styles
        return fallback_styles

    async def learn_style_from_image(
        self,
        image_bytes: bytes,
        style_name: str,
        mime_type: str = "image/jpeg"
    ) -> Dict[str, Any]:
        """
        Learn a new visual style from an uploaded image using Gemini Vision

        Process:
        1. Send image to Gemini 1.5 Pro (Vision)
        2. AI analyzes lighting, color grading, film stock, composition
        3. Generates a compact "prompt suffix" (30-50 words)
        4. Saves to A5_Style_Database as a new preset

        Args:
            image_bytes: Image file bytes
            style_name: Name for the new style (e.g., "My Custom Look")
            mime_type: MIME type (image/jpeg, image/png, etc.)

        Returns:
            Dict with:
            - name: Style name
            - suffix: Generated prompt suffix
            - status: "success" or "error"
        """
        logger.info(f"Learning new style from image: {style_name}")

        try:
            # Step 1: Analyze image with Gemini Vision
            style_suffix = await gemini_service.analyze_image_style(
                image_bytes=image_bytes,
                mime_type=mime_type
            )

            logger.info(f"Gemini generated style suffix: {style_suffix}")

            # Step 2: Save to Google Sheets
            timestamp = datetime.now().isoformat()
            data = [
                style_name,
                style_suffix,
                "",  # negative prompt (empty for learned styles)
                f"AI-learned style from uploaded image",  # description
                timestamp
            ]

            success = await google_sheet_service.append_row(SHEET_A5_STYLE_DATABASE, data)

            if success:
                # Clear cache to force reload
                self._styles_cache = None

                logger.info(f"✅ Style '{style_name}' saved to database")
                return {
                    "name": style_name,
                    "suffix": style_suffix,
                    "status": "success",
                    "message": f"Style '{style_name}' learned and saved successfully"
                }
            else:
                logger.error("Failed to save style to database")
                return {
                    "name": style_name,
                    "suffix": style_suffix,
                    "status": "error",
                    "message": "Failed to save to database"
                }

        except Exception as e:
            logger.error(f"Error learning style from image: {e}")
            return {
                "name": style_name,
                "suffix": "",
                "status": "error",
                "message": f"Failed to analyze image: {str(e)}"
            }

    def clear_cache(self):
        """Clear the styles cache to force reload from database"""
        self._styles_cache = None
        logger.info("Styles cache cleared")


# Singleton instance
agent5_service = Agent5StyleAnchors()
