"""
Agent 4: Scene Breakdown - "The Director"
Generates precise camera, lighting, and scene descriptions based on energy mapping
"""

from typing import Optional, List, Dict, Any
from app.models.data_models import SceneBreakdown
from app.infrastructure.database.google_sheet_service import (
    google_sheet_service,
    SHEET_A4_SCENES,
    SHEET_VIDEO_PROMPT_CHEATSHEET
)
from app.infrastructure.external_services.gemini_service import gemini_service
from app.utils.logger import setup_logger
import random

logger = setup_logger("Agent4_SceneBreakdown")


class Agent4SceneBreakdown:
    """Singleton service for scene breakdown and directing"""

    _instance: Optional['Agent4SceneBreakdown'] = None
    _cheatsheet_cache: Optional[Dict[str, Any]] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def process_scenes(
        self,
        scenes: List[Dict[str, Any]],
        project_id: Optional[str] = None,
        use_ai_enhancement: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Process scenes from Agent 3 and add camera, lighting, and descriptions

        Args:
            scenes: List of scenes from audio analysis
            project_id: Optional project ID
            use_ai_enhancement: Use Gemini AI for description enhancement

        Returns:
            Enhanced scenes with camera, lighting, and description
        """
        logger.info(f"Processing {len(scenes)} scenes for directing")

        # Load cheatsheet keywords
        cheatsheet = await self._load_cheatsheet()

        enhanced_scenes = []

        for scene in scenes:
            # Map energy level to camera/lighting choices
            camera, lighting = self._map_energy_to_visuals(
                scene.get("energy", "Medium"),
                cheatsheet
            )

            # Generate description
            if use_ai_enhancement:
                description = await self._generate_ai_description(scene, camera, lighting)
            else:
                description = self._generate_template_description(scene, camera, lighting)

            enhanced_scene = {
                **scene,  # Keep original data (id, start, end, energy, type)
                "camera": camera,
                "lighting": lighting,
                "description": description,
                "project_id": project_id
            }

            enhanced_scenes.append(enhanced_scene)

        logger.info(f"✅ Enhanced {len(enhanced_scenes)} scenes with directing details")
        return enhanced_scenes

    async def _load_cheatsheet(self) -> Dict[str, Any]:
        """
        Load Video_Prompt_Cheatsheet from Google Sheets

        Returns:
            Dictionary with camera and lighting keywords organized by energy level
        """
        # Check cache first
        if self._cheatsheet_cache:
            logger.info("Using cached cheatsheet")
            return self._cheatsheet_cache

        try:
            records = await google_sheet_service.get_all_records(SHEET_VIDEO_PROMPT_CHEATSHEET)

            if records and len(records) > 0:
                logger.info(f"Loaded {len(records)} cheatsheet entries")

                # Organize by energy level
                cheatsheet = {
                    "Low": {"camera": [], "lighting": []},
                    "Medium": {"camera": [], "lighting": []},
                    "High": {"camera": [], "lighting": []}
                }

                for record in records:
                    energy = record.get("energy_level", "Medium")
                    category = record.get("category", "camera")  # camera or lighting
                    keyword = record.get("keyword", "")

                    if energy in cheatsheet and keyword:
                        if category == "camera":
                            cheatsheet[energy]["camera"].append(keyword)
                        elif category == "lighting":
                            cheatsheet[energy]["lighting"].append(keyword)

                self._cheatsheet_cache = cheatsheet
                return cheatsheet

        except Exception as e:
            logger.warning(f"Could not load cheatsheet from sheets: {e}")

        # Fallback: Hardcoded cheatsheet
        logger.info("Using fallback cheatsheet")
        fallback_cheatsheet = {
            "Low": {
                "camera": ["Slow Zoom", "Static", "Gentle Pan", "Dolly In", "Close-Up"],
                "lighting": ["Soft", "Ambient", "Blue Hour", "Moonlight", "Warm Glow"]
            },
            "Medium": {
                "camera": ["Tracking Shot", "Smooth Pan", "Medium Shot", "Over-Shoulder", "Tilt"],
                "lighting": ["Natural", "Golden Hour", "Balanced", "Studio", "Mixed"]
            },
            "High": {
                "camera": ["Whip Pan", "Shake", "Quick Cut", "Dutch Angle", "Crash Zoom"],
                "lighting": ["Strobe", "Neon", "High Contrast", "Intense", "Flash"]
            }
        }

        self._cheatsheet_cache = fallback_cheatsheet
        return fallback_cheatsheet

    def _map_energy_to_visuals(
        self,
        energy: str,
        cheatsheet: Dict[str, Any]
    ) -> tuple[str, str]:
        """
        Map energy level to camera and lighting choices

        Args:
            energy: Energy level (Low/Medium/High)
            cheatsheet: Loaded cheatsheet

        Returns:
            Tuple of (camera_movement, lighting_style)
        """
        if energy not in cheatsheet or not cheatsheet[energy]:
            energy = "Medium"  # Fallback

        # Randomly select from appropriate energy level
        camera_options = cheatsheet[energy].get("camera", ["Static"])
        lighting_options = cheatsheet[energy].get("lighting", ["Natural"])

        camera = random.choice(camera_options) if camera_options else "Static"
        lighting = random.choice(lighting_options) if lighting_options else "Natural"

        return camera, lighting

    async def _generate_ai_description(
        self,
        scene: Dict[str, Any],
        camera: str,
        lighting: str
    ) -> str:
        """
        Generate AI-enhanced scene description using Gemini

        Args:
            scene: Scene data
            camera: Selected camera movement
            lighting: Selected lighting style

        Returns:
            Enhanced description
        """
        prompt = f"""You are a music video director writing shot descriptions.

SCENE DETAILS:
- Timing: {scene.get('start', 0):.2f}s - {scene.get('end', 0):.2f}s ({scene.get('duration', 0):.2f}s)
- Section: {scene.get('type', 'Scene')}
- Energy: {scene.get('energy', 'Medium')}
- Camera: {camera}
- Lighting: {lighting}

Generate a concise, cinematic shot description (max 2 sentences, 30 words).
Focus on visual mood and action, not technical details.

Example format:
"Artist performs in a dimly lit studio, camera slowly zooming in on their intense expression. Soft blue ambient light creates an intimate atmosphere."

Your description:"""

        try:
            ai_response = await gemini_service.generate_text(prompt)
            # Clean up response
            description = ai_response.strip().replace('"', '')

            # Ensure reasonable length
            if len(description) > 200:
                description = description[:197] + "..."

            return description

        except Exception as e:
            logger.warning(f"AI description generation failed: {e}")
            return self._generate_template_description(scene, camera, lighting)

    def _generate_template_description(
        self,
        scene: Dict[str, Any],
        camera: str,
        lighting: str
    ) -> str:
        """
        Generate template-based description (fallback)

        Args:
            scene: Scene data
            camera: Selected camera movement
            lighting: Selected lighting style

        Returns:
            Template description
        """
        scene_type = scene.get("type", "Scene")
        energy = scene.get("energy", "Medium")

        # Energy-specific templates
        templates = {
            "Low": [
                f"Intimate {scene_type.lower()} with {camera.lower()}. {lighting} lighting creates a contemplative mood.",
                f"Artist in reflective moment during {scene_type.lower()}. {camera}, bathed in {lighting.lower()} light.",
            ],
            "Medium": [
                f"Dynamic {scene_type.lower()} captured with {camera.lower()}. {lighting} lighting balances energy and emotion.",
                f"Artist performs {scene_type.lower()} with controlled intensity. {camera}, {lighting.lower()} atmosphere.",
            ],
            "High": [
                f"Explosive {scene_type.lower()} with intense {camera.lower()}. {lighting} lighting amplifies the raw energy.",
                f"High-energy {scene_type.lower()} performance. Rapid {camera.lower()}, dramatic {lighting.lower()} effects.",
            ]
        }

        template_list = templates.get(energy, templates["Medium"])
        return random.choice(template_list)

    async def create_scene(self, project_id: str, scene_data: SceneBreakdown) -> SceneBreakdown:
        """
        Legacy method for backward compatibility

        Args:
            project_id: Project ID
            scene_data: Scene breakdown data

        Returns:
            Created scene breakdown
        """
        logger.info(f"Creating scene for project {project_id}")

        # Save to Google Sheets
        await self._save_to_sheets(scene_data)

        return scene_data

    async def get_scenes(self, project_id: str) -> List[SceneBreakdown]:
        """Get all scenes for a project"""
        records = await google_sheet_service.get_all_records(SHEET_A4_SCENES)

        scenes = []
        for record in records:
            if record.get("project_id") == project_id:
                scenes.append(SceneBreakdown(**record))

        return scenes

    async def _save_to_sheets(self, scene: SceneBreakdown) -> bool:
        """Save scene breakdown to Google Sheets"""
        data = [
            scene.id,
            scene.project_id,
            scene.scene_number,
            scene.timestamp_start,
            scene.timestamp_end,
            scene.music_segment,
            scene.visual_concept,
            scene.mood,
            ", ".join(scene.style_references),
            scene.created_at.isoformat()
        ]

        return await google_sheet_service.append_row(SHEET_A4_SCENES, data)


# Singleton instance
agent4_service = Agent4SceneBreakdown()
