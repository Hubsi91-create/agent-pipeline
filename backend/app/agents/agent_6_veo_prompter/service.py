"""
Agent 6: Veo Prompter
Generates video prompts optimized for Google Veo
"""

from typing import Optional, List
from app.models.data_models import VideoPrompt, Scene, StyleAnchor
from app.infrastructure.external_services.gemini_service import gemini_service
from app.infrastructure.database.google_sheet_service import google_sheet_service, SHEET_A6_VEO_PROMPTS
from app.utils.logger import setup_logger

logger = setup_logger("Agent6_VeoPrompter")


class Agent6VeoPrompter:
    """Singleton service for Veo prompt generation"""

    _instance: Optional['Agent6VeoPrompter'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def generate_prompt(
        self,
        scene: Scene,
        style_anchor: StyleAnchor
    ) -> VideoPrompt:
        """
        Generate Veo-optimized video prompt for a scene

        Args:
            scene: Scene to generate prompt for
            style_anchor: Style anchor for consistency

        Returns:
            Video prompt
        """
        logger.info(f"Generating Veo prompt for scene {scene.scene_number}")

        # Create prompt for Gemini
        gemini_prompt = self._create_prompt_generation_request(scene, style_anchor)

        # Get AI-generated prompt
        prompt_text = await gemini_service.generate_text(gemini_prompt, temperature=0.7)

        # Create video prompt
        video_prompt = VideoPrompt(
            project_id=scene.project_id,
            scene_id=scene.id,
            scene_number=scene.scene_number,
            generator="veo",
            prompt_text=prompt_text.strip(),
            style_anchor_id=style_anchor.id,
            technical_params={
                "duration": scene.duration,
                "aspect_ratio": "16:9",
                "resolution": "1080p",
                "fps": 30
            },
            status="PENDING_QC"
        )

        # Save to Google Sheets
        await self._save_to_sheets(video_prompt)

        logger.info(f"Veo prompt generated: {video_prompt.id}")
        return video_prompt

    def _create_prompt_generation_request(
        self,
        scene: Scene,
        style_anchor: StyleAnchor
    ) -> str:
        """Create prompt for generating the video prompt"""
        return f"""
Generate a detailed video generation prompt for Google Veo.

Scene Information:
- Scene {scene.scene_number}: {scene.music_section}
- Duration: {scene.duration:.1f}s
- Mood: {scene.mood}
- Description: {scene.description}
- Camera: {scene.camera_movement}

Visual Style:
- Style: {style_anchor.style_name}
- {style_anchor.description}
- Keywords: {', '.join(style_anchor.keywords)}

Create a single, detailed paragraph prompt (max 300 words) that:
1. Describes the visual scene clearly
2. Incorporates the style and mood
3. Includes camera movement
4. Optimizes for Veo's video generation capabilities

Prompt:
"""

    async def get_prompts_for_scene(self, scene_id: str) -> List[VideoPrompt]:
        """Get all Veo prompts for a scene"""
        records = await google_sheet_service.get_all_records(SHEET_A6_VEO_PROMPTS)
        prompts = [VideoPrompt(**r) for r in records if r.get("scene_id") == scene_id]
        return prompts

    async def _save_to_sheets(self, prompt: VideoPrompt) -> bool:
        """Save video prompt to Google Sheets"""
        data = [
            prompt.id,
            prompt.project_id,
            prompt.scene_id,
            prompt.scene_number,
            prompt.generator,
            prompt.prompt_text[:500],  # Truncate for sheet display
            prompt.negative_prompt or "",
            prompt.style_anchor_id,
            prompt.status,
            prompt.iteration,
            prompt.created_at.isoformat()
        ]

        return await google_sheet_service.append_row(SHEET_A6_VEO_PROMPTS, data)


# Singleton instance
agent6_service = Agent6VeoPrompter()
