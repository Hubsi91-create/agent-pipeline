"""
Agent 9: CapCut Instructor - "The Editor's Assistant"
Generates step-by-step editing guides for CapCut based on audio analysis
"""

from typing import Optional, Dict, Any, List
from app.infrastructure.database.google_sheet_service import (
    google_sheet_service,
    SHEET_A9_CAPCUT_EFFECTS
)
from app.utils.logger import setup_logger

logger = setup_logger("Agent9_CapCut")


class Agent9CapCutInstructor:
    """Singleton service for CapCut editing instructions"""

    _instance: Optional['Agent9CapCutInstructor'] = None
    _effects_cache: Optional[List[Dict[str, str]]] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def generate_edit_guide(
        self,
        scenes: List[Dict[str, Any]],
        audio_duration: float = None
    ) -> str:
        """
        Generate Edit Decision List (EDL) for CapCut

        Args:
            scenes: List of scene dicts with timing, energy, type
            audio_duration: Total audio duration (optional)

        Returns:
            Markdown-formatted editing guide
        """
        logger.info(f"Generating CapCut edit guide for {len(scenes)} scenes")

        # Load effects database
        effects = await self._load_effects()

        # Build EDL markdown
        guide_lines = []
        guide_lines.append("# 🎬 CapCut Editing Guide\n")
        guide_lines.append("**Step-by-step instructions for video editing**\n")
        guide_lines.append("---\n")

        # Timeline setup
        guide_lines.append("## 📋 Timeline Setup\n")
        guide_lines.append("1. **Import Audio**: Drag your master audio track to the timeline")
        guide_lines.append("2. **Lock Audio Track**: Right-click audio → Lock track")
        guide_lines.append("3. **Import Scene Videos**: Import all generated video clips")
        if audio_duration:
            guide_lines.append(f"4. **Total Duration**: {audio_duration:.2f}s\n")
        else:
            guide_lines.append("")

        guide_lines.append("---\n")

        # Scene-by-scene instructions
        guide_lines.append("## 🎞️ Scene-by-Scene Editing\n")

        for i, scene in enumerate(scenes):
            scene_num = i + 1
            start_time = scene.get('start', 0)
            end_time = scene.get('end', 0)
            duration = scene.get('duration', 0)
            energy = scene.get('energy', 'medium').lower()
            scene_type = scene.get('type', 'unknown').lower()

            guide_lines.append(f"### Scene {scene_num}: {scene_type.title()} ({start_time:.2f}s - {end_time:.2f}s)\n")
            guide_lines.append(f"**Duration**: {duration:.2f}s | **Energy**: {energy.upper()}\n")

            # Get recommendations based on energy and type
            recommendations = self._get_scene_recommendations(
                energy=energy,
                scene_type=scene_type,
                effects=effects,
                start_time=start_time
            )

            guide_lines.append("**Editing Instructions:**\n")
            for rec in recommendations:
                guide_lines.append(f"- {rec}")

            guide_lines.append("")

        guide_lines.append("---\n")

        # Final touches
        guide_lines.append("## ✨ Final Touches\n")
        guide_lines.append("1. **Color Grading**: Apply consistent color preset across all scenes")
        guide_lines.append("2. **Transitions**: Use cuts for high energy, fades for low energy")
        guide_lines.append("3. **Audio Sync**: Verify all cuts are perfectly synced to beats")
        guide_lines.append("4. **Export Settings**: 1080p, 30fps, MP4 format")
        guide_lines.append("5. **Preview**: Watch full video before export\n")

        markdown_guide = "\n".join(guide_lines)

        logger.info("CapCut edit guide generated successfully")
        return markdown_guide

    def _get_scene_recommendations(
        self,
        energy: str,
        scene_type: str,
        effects: List[Dict[str, str]],
        start_time: float
    ) -> List[str]:
        """
        Get editing recommendations for a scene

        Args:
            energy: Energy level (low, medium, high)
            scene_type: Scene type (intro, verse, chorus, drop, etc.)
            effects: List of available effects
            start_time: Scene start time

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Timing recommendation
        recommendations.append(f"**Position video clip at {start_time:.2f}s** on the timeline")

        # Energy-based recommendations
        if energy == 'low':
            # Low energy scenes
            recommendations.append("**Pacing**: Use slow, smooth transitions")
            recommendations.append("**Camera**: Prefer static or slow-moving shots")

            # Find atmospheric effects
            atmospheric_effects = [
                eff for eff in effects
                if any(keyword in eff.get('name', '').lower()
                       for keyword in ['glow', 'dreamy', 'soft', 'blur', 'vintage', 'retro'])
            ]

            if atmospheric_effects:
                effect_names = [f"'{eff['name']}'" for eff in atmospheric_effects[:3]]
                recommendations.append(f"**Effects**: Apply {' or '.join(effect_names)} for atmosphere")
            else:
                recommendations.append("**Effects**: Use 'Dreamy Glow' or 'Soft Blur' for atmosphere")

        elif energy == 'high':
            # High energy scenes
            recommendations.append(f"**CUT HARD** on the beat at {start_time:.2f}s")
            recommendations.append("**Pacing**: Use rapid cuts and dynamic transitions")
            recommendations.append("**Camera**: Emphasize fast movement and action")

            # Find energetic effects
            energetic_effects = [
                eff for eff in effects
                if any(keyword in eff.get('name', '').lower()
                       for keyword in ['shake', 'strobe', 'glitch', 'flash', 'zoom', 'shake'])
            ]

            if energetic_effects:
                effect_names = [f"'{eff['name']}'" for eff in energetic_effects[:3]]
                recommendations.append(f"**Effects**: Add {' + '.join(effect_names)} for impact")
            else:
                recommendations.append("**Effects**: Add 'Shake' + 'Strobe' or 'Glitch' for impact")

        else:
            # Medium energy
            recommendations.append("**Pacing**: Balanced rhythm matching the music")
            recommendations.append("**Camera**: Mix of static and moving shots")
            recommendations.append("**Effects**: Use subtle transitions and light color adjustments")

        # Scene type-specific recommendations
        if 'intro' in scene_type:
            recommendations.append("**Special Note**: Establish visual identity and mood")
        elif 'drop' in scene_type or 'chorus' in scene_type:
            recommendations.append("**Special Note**: This is a key moment - maximize visual impact!")
        elif 'outro' in scene_type:
            recommendations.append("**Special Note**: Wind down gracefully, consider fade to black")

        return recommendations

    async def _load_effects(self) -> List[Dict[str, str]]:
        """
        Load CapCut effects from database

        Returns:
            List of effect dicts with name, category, description
        """
        # Check cache
        if self._effects_cache:
            return self._effects_cache

        try:
            records = await google_sheet_service.get_all_records(SHEET_A9_CAPCUT_EFFECTS)

            if records and len(records) > 0:
                effects = []
                for record in records:
                    effects.append({
                        "name": record.get("name", "Unknown Effect"),
                        "category": record.get("category", "general"),
                        "energy": record.get("energy", "medium"),
                        "description": record.get("description", "")
                    })

                self._effects_cache = effects
                logger.info(f"Loaded {len(effects)} CapCut effects from database")
                return effects

        except Exception as e:
            logger.warning(f"Could not load effects from database: {e}")

        # Fallback: Hardcoded effects library
        fallback_effects = [
            {
                "name": "Dreamy Glow",
                "category": "atmosphere",
                "energy": "low",
                "description": "Soft ethereal glow effect for dreamy scenes"
            },
            {
                "name": "Retro Blue",
                "category": "color",
                "energy": "low",
                "description": "Vintage film aesthetic with blue tint"
            },
            {
                "name": "Soft Blur",
                "category": "atmosphere",
                "energy": "low",
                "description": "Gentle background blur for depth"
            },
            {
                "name": "Shake",
                "category": "motion",
                "energy": "high",
                "description": "Camera shake effect for impact"
            },
            {
                "name": "Strobe",
                "category": "lighting",
                "energy": "high",
                "description": "Strobe light flash effect"
            },
            {
                "name": "Glitch",
                "category": "distortion",
                "energy": "high",
                "description": "Digital glitch distortion"
            },
            {
                "name": "Flash Zoom",
                "category": "motion",
                "energy": "high",
                "description": "Rapid zoom with flash"
            },
            {
                "name": "Beat Sync",
                "category": "rhythm",
                "energy": "medium",
                "description": "Automated beat-synced cuts"
            },
            {
                "name": "Color Pop",
                "category": "color",
                "energy": "medium",
                "description": "Selective color highlighting"
            },
            {
                "name": "Light Leak",
                "category": "atmosphere",
                "energy": "low",
                "description": "Film-style light leaks"
            }
        ]

        logger.info(f"Using {len(fallback_effects)} fallback effects")
        return fallback_effects


# Singleton instance
agent9_service = Agent9CapCutInstructor()
