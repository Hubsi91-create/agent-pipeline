"""
Agent 5: Style Anchors
Creates consistent visual style anchors for the video
"""

from typing import Optional, List
from app.models.data_models import StyleAnchor, Scene
from app.infrastructure.external_services.gemini_service import gemini_service
from app.infrastructure.database.google_sheet_service import google_sheet_service, SHEET_A5_STYLES
from app.utils.logger import setup_logger

logger = setup_logger("Agent5_StyleAnchors")


class Agent5StyleAnchors:
    """Singleton service for style anchor creation"""

    _instance: Optional['Agent5StyleAnchors'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def create_style_anchors(
        self,
        project_id: str,
        scenes: List[Scene],
        artist: str,
        song_title: str
    ) -> List[StyleAnchor]:
        """
        Create visual style anchors for consistent aesthetic

        Args:
            project_id: Project ID
            scenes: List of scenes
            artist: Artist name
            song_title: Song title

        Returns:
            List of style anchors
        """
        logger.info(f"Creating style anchors for project {project_id}")

        # Create prompt for Gemini
        prompt = self._create_style_prompt(scenes, artist, song_title)

        # Get AI style recommendations
        ai_response = await gemini_service.generate_text(prompt, temperature=0.8)

        # Create style anchor
        style_anchor = self._create_style_from_response(project_id, ai_response)

        # Save to Google Sheets
        await self._save_to_sheets(style_anchor)

        logger.info(f"Created style anchor: {style_anchor.id}")
        return [style_anchor]

    def _create_style_prompt(self, scenes: List[Scene], artist: str, song_title: str) -> str:
        """Create prompt for style anchor generation"""
        moods = list(set([s.mood for s in scenes]))

        return f"""
Create a cohesive visual style guide for a music video:

Artist: {artist}
Song: {song_title}
Moods: {', '.join(moods)}
Number of scenes: {len(scenes)}

Provide:
1. Overall visual style description (2-3 sentences)
2. Color palette (5-7 hex colors)
3. Visual keywords
4. Consistency notes

Make it cinematic and distinctive.
"""

    def _create_style_from_response(self, project_id: str, ai_response: str) -> StyleAnchor:
        """Parse AI response and create style anchor"""
        # Default values (in production, parse AI response more thoroughly)
        style_anchor = StyleAnchor(
            project_id=project_id,
            style_name="Cinematic Urban",
            description="High-contrast cinematic visuals with vibrant neon accents. Urban landscapes meet artistic abstraction.",
            color_palette=[
                "#1a1a2e",  # Dark blue-black
                "#16213e",  # Deep navy
                "#0f3460",  # Ocean blue
                "#533483",  # Deep purple
                "#e94560",  # Vibrant red
                "#f39c12",  # Golden yellow
                "#00d4ff"   # Cyan
            ],
            visual_references=[
                "Blade Runner 2049 color grading",
                "Music video: The Weeknd - Blinding Lights",
                "Neo-noir cinematography"
            ],
            keywords=[
                "cinematic",
                "high-contrast",
                "neon",
                "urban",
                "moody",
                "vibrant",
                "atmospheric"
            ],
            mood="Urban Cinematic",
            consistency_notes="Maintain high contrast throughout. Use neon accents sparingly but impactfully. Keep urban elements grounded while allowing artistic freedom in transitions."
        )

        return style_anchor

    async def get_style_anchors_for_project(self, project_id: str) -> List[StyleAnchor]:
        """Get all style anchors for a project"""
        records = await google_sheet_service.get_all_records(SHEET_A5_STYLES)
        styles = [StyleAnchor(**r) for r in records if r.get("project_id") == project_id]
        return styles

    async def _save_to_sheets(self, style_anchor: StyleAnchor) -> bool:
        """Save style anchor to Google Sheets"""
        data = [
            style_anchor.id,
            style_anchor.project_id,
            style_anchor.style_name,
            style_anchor.description,
            ", ".join(style_anchor.color_palette),
            ", ".join(style_anchor.visual_references),
            ", ".join(style_anchor.keywords),
            style_anchor.mood,
            style_anchor.consistency_notes,
            style_anchor.created_at.isoformat()
        ]

        return await google_sheet_service.append_row(SHEET_A5_STYLES, data)


# Singleton instance
agent5_service = Agent5StyleAnchors()
