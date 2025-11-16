"""
Agent 4: Scene Breakdown
Creates scene breakdown based on audio analysis
"""

from typing import Optional, List
from app.models.data_models import Scene, AudioAnalysis
from app.infrastructure.external_services.gemini_service import gemini_service
from app.infrastructure.database.google_sheet_service import google_sheet_service, SHEET_A4_SCENES
from app.utils.logger import setup_logger

logger = setup_logger("Agent4_SceneBreakdown")


class Agent4SceneBreakdown:
    """Singleton service for scene breakdown"""

    _instance: Optional['Agent4SceneBreakdown'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def create_scene_breakdown(
        self,
        project_id: str,
        audio_analysis: AudioAnalysis
    ) -> List[Scene]:
        """
        Create scene breakdown based on audio analysis

        Args:
            project_id: Project ID
            audio_analysis: Audio analysis results

        Returns:
            List of scenes
        """
        logger.info(f"Creating scene breakdown for project {project_id}")

        # Create prompt for Gemini
        prompt = self._create_breakdown_prompt(audio_analysis)

        # Get AI scene suggestions
        ai_response = await gemini_service.generate_text(prompt, temperature=0.7)

        # Parse and create scenes
        scenes = self._create_scenes_from_response(project_id, audio_analysis, ai_response)

        # Save all scenes
        for scene in scenes:
            await self._save_to_sheets(scene)

        logger.info(f"Created {len(scenes)} scenes for project {project_id}")
        return scenes

    def _create_breakdown_prompt(self, audio_analysis: AudioAnalysis) -> str:
        """Create prompt for scene breakdown"""
        return f"""
Create a detailed scene breakdown for a music video with the following audio structure:

Duration: {audio_analysis.duration} seconds
BPM: {audio_analysis.bpm}
Key: {audio_analysis.key}
Structure: {', '.join(audio_analysis.structure)}
Peak Moments: {audio_analysis.peak_moments}

For each section, provide:
- Scene description
- Visual mood
- Key visual elements
- Camera movement suggestions

Make it cinematic and engaging.
"""

    def _create_scenes_from_response(
        self,
        project_id: str,
        audio_analysis: AudioAnalysis,
        ai_response: str
    ) -> List[Scene]:
        """Parse AI response and create scenes"""
        scenes = []

        # Calculate scene timing based on structure
        total_duration = audio_analysis.duration
        section_count = len(audio_analysis.structure)
        avg_duration = total_duration / section_count

        current_time = 0.0

        for idx, section_name in enumerate(audio_analysis.structure):
            scene_duration = avg_duration
            end_time = current_time + scene_duration

            scene = Scene(
                project_id=project_id,
                scene_number=idx + 1,
                start_time=current_time,
                end_time=end_time,
                duration=scene_duration,
                music_section=section_name,
                description=f"Visual interpretation of {section_name}",
                visual_style_ref="default_style",
                mood=self._get_mood_for_section(section_name),
                key_elements=[section_name.lower(), "dynamic", "cinematic"],
                camera_movement=self._get_camera_movement(section_name)
            )

            scenes.append(scene)
            current_time = end_time

        return scenes

    def _get_mood_for_section(self, section: str) -> str:
        """Determine mood based on section type"""
        section_lower = section.lower()
        if "intro" in section_lower:
            return "mysterious"
        elif "verse" in section_lower:
            return "contemplative"
        elif "chorus" in section_lower:
            return "energetic"
        elif "bridge" in section_lower:
            return "emotional"
        elif "outro" in section_lower:
            return "resolving"
        else:
            return "dynamic"

    def _get_camera_movement(self, section: str) -> str:
        """Suggest camera movement for section"""
        section_lower = section.lower()
        if "intro" in section_lower:
            return "slow zoom in"
        elif "chorus" in section_lower:
            return "dynamic tracking shot"
        elif "bridge" in section_lower:
            return "slow pan"
        else:
            return "steady cam"

    async def get_scenes_for_project(self, project_id: str) -> List[Scene]:
        """Get all scenes for a project"""
        records = await google_sheet_service.get_all_records(SHEET_A4_SCENES)
        scenes = [Scene(**r) for r in records if r.get("project_id") == project_id]
        return sorted(scenes, key=lambda s: s.scene_number)

    async def _save_to_sheets(self, scene: Scene) -> bool:
        """Save scene to Google Sheets"""
        data = [
            scene.id,
            scene.project_id,
            scene.scene_number,
            scene.start_time,
            scene.end_time,
            scene.duration,
            scene.music_section,
            scene.description,
            scene.visual_style_ref,
            scene.mood,
            ", ".join(scene.key_elements),
            scene.camera_movement or "",
            scene.created_at.isoformat()
        ]

        return await google_sheet_service.append_row(SHEET_A4_SCENES, data)


# Singleton instance
agent4_service = Agent4SceneBreakdown()
