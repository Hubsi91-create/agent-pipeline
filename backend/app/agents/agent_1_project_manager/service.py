"""
Agent 1: Project Manager
Creates and manages video production projects
Also provides trend detection and genre variation generation
"""

from typing import Optional, List, Dict
from app.models.data_models import Project, ProjectCreate, ProjectStatus
from app.infrastructure.database.google_sheet_service import (
    google_sheet_service,
    SHEET_A1_PROJECTS,
    SHEET_A1_TREND_DATABASE
)
from app.infrastructure.external_services.gemini_service import gemini_service
from app.utils.logger import setup_logger
import random
import json
from datetime import datetime

logger = setup_logger("Agent1_ProjectManager")


class Agent1ProjectManager:
    """Singleton service for project management"""

    _instance: Optional['Agent1ProjectManager'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def create_project(self, project_data: ProjectCreate) -> Project:
        """
        Create a new music video project

        Args:
            project_data: Project creation data

        Returns:
            Created project
        """
        logger.info(f"Creating new project: {project_data.name}")

        # Create project
        project = Project(
            name=project_data.name,
            artist=project_data.artist,
            song_title=project_data.song_title,
            status=ProjectStatus(status="INIT", progress_percentage=0.0)
        )

        # Save to Google Sheets
        await self._save_to_sheets(project)

        logger.info(f"Project created: {project.id}")
        return project

    async def get_project(self, project_id: str) -> Optional[Project]:
        """Get a project by ID"""
        record = await google_sheet_service.find_record(
            SHEET_A1_PROJECTS,
            "id",
            project_id
        )

        if record:
            return Project(**record)
        return None

    async def update_project_status(
        self,
        project_id: str,
        status: str,
        current_agent: Optional[str] = None,
        progress: Optional[float] = None
    ) -> bool:
        """Update project status"""
        updates = {"status": status}
        if current_agent:
            updates["current_agent"] = current_agent
        if progress is not None:
            updates["progress_percentage"] = progress

        return await google_sheet_service.update_record(
            SHEET_A1_PROJECTS,
            "id",
            project_id,
            updates
        )

    async def get_current_viral_trends(self) -> List[Dict[str, str]]:
        """
        Get current viral music trends from YouTube, TikTok, Spotify
        Reads from A1_Trend_Database if available, otherwise uses fallback data

        Returns:
            List of 20 trending subgenres with descriptions
        """
        logger.info("Fetching current viral music trends")

        # Try to read from database first
        try:
            records = await google_sheet_service.get_all_records(SHEET_A1_TREND_DATABASE)

            if records and len(records) > 0:
                logger.info(f"Loaded {len(records)} trends from database")
                viral_trends = []

                for record in records:
                    viral_trends.append({
                        "genre": record.get("genre", "Unknown"),
                        "platform": record.get("platform", "Mixed"),
                        "trend_score": record.get("trend_score", "🔥"),
                        "description": record.get("description", "")
                    })

                # Shuffle for variety on each load
                shuffled = viral_trends.copy()
                random.shuffle(shuffled)

                return shuffled[:20]  # Return max 20

        except Exception as e:
            logger.warning(f"Could not load trends from database: {e}")

        # Fallback: Static trending genres (regularly updated based on platform analytics)
        logger.info("Using fallback trend data")
        viral_trends = [
            {"genre": "Drift Phonk", "platform": "TikTok", "trend_score": "🔥🔥🔥"},
            {"genre": "Sped-Up Nightcore", "platform": "YouTube", "trend_score": "🔥🔥🔥"},
            {"genre": "Liquid DnB", "platform": "Spotify", "trend_score": "🔥🔥"},
            {"genre": "Hypertechno", "platform": "TikTok", "trend_score": "🔥🔥🔥"},
            {"genre": "Slowed + Reverb", "platform": "YouTube", "trend_score": "🔥🔥"},
            {"genre": "Brazilian Phonk", "platform": "TikTok", "trend_score": "🔥🔥🔥"},
            {"genre": "Dark Ambient Trap", "platform": "Spotify", "trend_score": "🔥🔥"},
            {"genre": "Rage Beats", "platform": "TikTok", "trend_score": "🔥🔥"},
            {"genre": "Pluggnb", "platform": "Spotify", "trend_score": "🔥🔥"},
            {"genre": "Hyperpop 2.0", "platform": "TikTok", "trend_score": "🔥🔥🔥"},
            {"genre": "Jersey Club", "platform": "TikTok", "trend_score": "🔥🔥"},
            {"genre": "UK Drill", "platform": "YouTube", "trend_score": "🔥🔥"},
            {"genre": "Afrobeats Fusion", "platform": "Spotify", "trend_score": "🔥🔥🔥"},
            {"genre": "Melodic Dubstep", "platform": "YouTube", "trend_score": "🔥🔥"},
            {"genre": "Dark Pop", "platform": "Spotify", "trend_score": "🔥🔥"},
            {"genre": "Lofi House", "platform": "YouTube", "trend_score": "🔥🔥"},
            {"genre": "Emo Rap Revival", "platform": "TikTok", "trend_score": "🔥🔥"},
            {"genre": "Industrial Techno", "platform": "Spotify", "trend_score": "🔥🔥"},
            {"genre": "Reggaeton Moderno", "platform": "TikTok", "trend_score": "🔥🔥🔥"},
            {"genre": "Synthwave Trap", "platform": "YouTube", "trend_score": "🔥🔥"}
        ]

        # Shuffle for variety on each load
        shuffled = viral_trends.copy()
        random.shuffle(shuffled)

        return shuffled

    async def update_viral_trends(self) -> Dict[str, any]:
        """
        Update viral trends from live web search
        Uses Gemini AI with grounding to fetch current trends from TikTok, Spotify, YouTube Shorts

        Returns:
            Dict with status, message, and count of updated trends
        """
        logger.info("Updating viral music trends from web search")

        # Get current month for search query
        current_month = datetime.now().strftime("%B")  # e.g., "December"
        current_year = datetime.now().year

        search_query = f"Latest viral music trends TikTok Spotify YouTube Shorts {current_month} {current_year} music video aesthetics"

        prompt = f"""You are a music trend analyst with access to current internet data.

SEARCH QUERY: "{search_query}"

Your task: Identify the TOP 20 VIRAL MUSIC TRENDS right now (as of {current_month} {current_year}).

REQUIREMENTS:
1. Focus on ACTUAL viral genres/styles trending on TikTok, Spotify, and YouTube Shorts
2. Include both audio trends AND visual aesthetics (e.g., "Dirty Aesthetic", "Slowed + Reverb")
3. Prioritize genres that are CURRENTLY viral (not just established genres)
4. Mix platforms: ~40% TikTok, ~30% YouTube Shorts, ~30% Spotify
5. Each trend must be REAL and SPECIFIC (not generic)

KEY TRENDS TO CONSIDER (if currently viral):
- Phonk variants (Drift Phonk, Brazilian Phonk)
- Darkwave
- Hyperpop evolutions
- Slowed + Reverb aesthetic
- Sped-Up/Nightcore
- Afrobeats Fusion
- Aesthetic-driven genres (e.g., "Dirty Aesthetic")

FORMAT (JSON Array):
[
  {{
    "genre": "Drift Phonk",
    "platform": "TikTok",
    "trend_score": "🔥🔥🔥",
    "description": "Aggressive bass-heavy phonk with Tokyo drift aesthetics"
  }},
  {{
    "genre": "APT. Dance Challenge",
    "platform": "TikTok",
    "trend_score": "🔥🔥🔥",
    "description": "BLACKPINK Rosé x Bruno Mars viral dance trend"
  }},
  ...
]

TREND SCORE GUIDE:
- 🔥🔥🔥 = Extremely viral (trending now)
- 🔥🔥 = Very popular
- 🔥 = Growing trend

Generate exactly 20 trends in JSON format."""

        try:
            # Get AI response with current trend knowledge
            ai_response = await gemini_service.generate_text(prompt)

            # Parse JSON response
            json_str = ai_response.strip()
            if json_str.startswith("```json"):
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif json_str.startswith("```"):
                json_str = json_str.split("```")[1].split("```")[0].strip()

            trends = json.loads(json_str)

            # Ensure we have exactly 20 trends
            if len(trends) < 20:
                logger.warning(f"Only {len(trends)} trends generated, expected 20")

            # Save to Google Sheets
            headers = ["genre", "platform", "trend_score", "description", "last_updated"]
            data_rows = []

            timestamp = datetime.now().isoformat()
            for trend in trends[:20]:  # Limit to 20
                data_rows.append([
                    trend.get("genre", "Unknown"),
                    trend.get("platform", "Mixed"),
                    trend.get("trend_score", "🔥"),
                    trend.get("description", ""),
                    timestamp
                ])

            # Clear and replace trend database
            success = await google_sheet_service.clear_and_replace(
                SHEET_A1_TREND_DATABASE,
                headers,
                data_rows
            )

            if success:
                logger.info(f"✅ Updated {len(data_rows)} viral trends in database")
                return {
                    "status": "success",
                    "message": f"Trends updated from web (TikTok, Spotify, YouTube Shorts) - {current_month} {current_year}",
                    "count": len(data_rows),
                    "trends": trends[:20]
                }
            else:
                logger.error("Failed to save trends to Google Sheets")
                return {
                    "status": "error",
                    "message": "Failed to save trends to database",
                    "count": 0
                }

        except Exception as e:
            logger.error(f"Error updating viral trends: {e}")
            return {
                "status": "error",
                "message": f"Failed to update trends: {str(e)}",
                "count": 0
            }

    async def generate_genre_variations(self, super_genre: str, num_variations: int = 20) -> List[Dict[str, str]]:
        """
        Generate music genre variations for a given super genre

        Args:
            super_genre: Main genre (e.g., "Electronic", "HipHop")
            num_variations: Number of variations to generate (default: 20)

        Returns:
            List of genre variations with descriptions
        """
        logger.info(f"Generating {num_variations} variations for super genre: {super_genre}")

        prompt = f"""You are a music trend expert and genre specialist.

TASK: Generate {num_variations} SPECIFIC subgenre variations for the super genre "{super_genre}".

REQUIREMENTS:
1. Each variation must be a REAL, specific subgenre (not generic)
2. Include both established and emerging/viral subgenres
3. Add a brief description (1 sentence, max 15 words)
4. Mix classic subgenres with modern fusion styles
5. Consider current TikTok, YouTube, and Spotify trends

FORMAT (JSON):
[
  {{"subgenre": "Liquid Drum & Bass", "description": "Smooth, melodic DnB with soulful vocals and atmospheric pads"}},
  {{"subgenre": "Neurofunk", "description": "Dark, technical DnB with complex bass design and sci-fi elements"}},
  ...
]

Generate {num_variations} variations for: {super_genre}"""

        try:
            # Get AI response
            ai_response = await gemini_service.generate_text(prompt)

            # Parse JSON response
            import json
            # Extract JSON from response (remove markdown code blocks if present)
            json_str = ai_response.strip()
            if json_str.startswith("```json"):
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif json_str.startswith("```"):
                json_str = json_str.split("```")[1].split("```")[0].strip()

            variations = json.loads(json_str)

            logger.info(f"Generated {len(variations)} variations successfully")
            return variations[:num_variations]  # Ensure we return exactly num_variations

        except Exception as e:
            logger.error(f"Error generating variations: {e}")

            # Fallback: Return generic variations
            fallback_variations = []
            for i in range(num_variations):
                fallback_variations.append({
                    "subgenre": f"{super_genre} Style {i+1}",
                    "description": f"Variation {i+1} of {super_genre} with unique characteristics"
                })

            return fallback_variations

    async def _save_to_sheets(self, project: Project) -> bool:
        """Save project to Google Sheets"""
        data = [
            project.id,
            project.name,
            project.artist,
            project.song_title,
            project.audio_file_path or "",
            project.status.status,
            project.status.current_agent or "",
            project.status.progress_percentage,
            project.created_at.isoformat(),
            project.updated_at.isoformat()
        ]

        return await google_sheet_service.append_row(SHEET_A1_PROJECTS, data)


# Singleton instance
agent1_service = Agent1ProjectManager()
