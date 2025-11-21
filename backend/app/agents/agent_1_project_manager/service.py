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
import re
from datetime import datetime

logger = setup_logger("Agent1_ProjectManager")


# Static curated subgenres for common super genres
# Hybrid Strategy: Check here first before calling AI
STATIC_SUBGENRES = {
    "Reggaeton": [
        {"subgenre": "Neoperreo", "description": "Dark, industrial aesthetic with glitchy textures (95 BPM)"},
        {"subgenre": "Dembow Dominicano", "description": "Fast, repetitive loop with high energy (120 BPM)"},
        {"subgenre": "Romantiqueo", "description": "Slow, melodic reggaeton with emotional lyrics (85 BPM)"},
        {"subgenre": "Malianteo", "description": "Street lyrics, aggressive bass, trap influence (90 BPM)"},
        {"subgenre": "Reggaeton Mexa", "description": "Raw, lo-fi reggaeton with cumbia influences (92 BPM)"},
        {"subgenre": "Perreo Galáctico", "description": "Futuristic synths with space-themed aesthetics (100 BPM)"},
        {"subgenre": "Old School Reggaeton", "description": "Classic Daddy Yankee style with heavy dembow (95 BPM)"},
        {"subgenre": "Reggaeton Pop", "description": "Commercial, radio-friendly with pop hooks (96 BPM)"},
        {"subgenre": "Reggaeton Trap Fusion", "description": "Hybrid with trap 808s and reggaeton rhythm (88 BPM)"},
        {"subgenre": "Reggaeton Electrónico", "description": "EDM influences with electronic drops (128 BPM)"},
        {"subgenre": "Reggaeton Romántico", "description": "Love ballads with soft dembow beat (90 BPM)"},
        {"subgenre": "Moombahton", "description": "Reggaeton-house fusion with Dutch house elements (110 BPM)"},
        {"subgenre": "Cubaton", "description": "Cuban reggaeton with salsa and timba elements (92 BPM)"},
        {"subgenre": "Reggaeton Cristiano", "description": "Christian lyrics with traditional reggaeton beat (94 BPM)"},
        {"subgenre": "Perreo Intenso", "description": "Explicit, club-focused with heavy bass (96 BPM)"},
    ],
    "Electronic": [
        {"subgenre": "Drift Phonk", "description": "Distorted cowbells, Memphis rap vocals (140 BPM)"},
        {"subgenre": "Liquid DnB", "description": "Soulful drum and bass with smooth melodies (174 BPM)"},
        {"subgenre": "Stutter House", "description": "Vocal chops with emotional progressive house (126 BPM)"},
        {"subgenre": "Hyperpop", "description": "Maximalist, distorted, experimental pop (160 BPM)"},
        {"subgenre": "Brazilian Phonk", "description": "Aggressive bass with Brazilian funk samples (130 BPM)"},
        {"subgenre": "Future Bass", "description": "Colorful synths with emotional chord progressions (150 BPM)"},
        {"subgenre": "Melodic Dubstep", "description": "Emotional drops with heavy bass design (140 BPM)"},
        {"subgenre": "Tech House", "description": "Minimal, groovy with percussive elements (128 BPM)"},
        {"subgenre": "Psytrance", "description": "Psychedelic, fast-paced with trippy effects (145 BPM)"},
        {"subgenre": "Hardstyle", "description": "Reverse bass, euphoric melodies (150 BPM)"},
        {"subgenre": "Synthwave", "description": "80s-inspired retro aesthetics with analog synths (120 BPM)"},
        {"subgenre": "Deep House", "description": "Warm, atmospheric with soulful vocals (120 BPM)"},
        {"subgenre": "Neurofunk", "description": "Dark, technical DnB with complex sound design (174 BPM)"},
        {"subgenre": "Glitch Hop", "description": "Broken beats with digital glitches (90 BPM)"},
        {"subgenre": "Complextro", "description": "Complex, aggressive electro house (128 BPM)"},
    ],
    "HipHop": [
        {"subgenre": "Rage Rap", "description": "High-energy, distorted 808s with punk attitude (140 BPM)"},
        {"subgenre": "Pluggnb", "description": "Melodic, plug beats with R&B vocals (140 BPM)"},
        {"subgenre": "UK Drill", "description": "Dark, sliding 808s with menacing atmosphere (140 BPM)"},
        {"subgenre": "Emo Rap", "description": "Emotional lyrics with guitar melodies (120 BPM)"},
        {"subgenre": "Trap Metal", "description": "Screamed vocals with heavy distortion (150 BPM)"},
        {"subgenre": "Boom Bap", "description": "Classic 90s drums with jazz samples (90 BPM)"},
        {"subgenre": "Cloud Rap", "description": "Dreamy, ethereal production with laid-back flow (70 BPM)"},
        {"subgenre": "Jersey Club", "description": "Fast bed-squeaking samples (140 BPM)"},
        {"subgenre": "Phonk", "description": "Memphis samples with lo-fi aesthetic (130 BPM)"},
        {"subgenre": "Afroswing", "description": "Afrobeats rhythm with UK rap (100 BPM)"},
        {"subgenre": "Glitchcore Rap", "description": "Digital glitches with experimental production (160 BPM)"},
        {"subgenre": "Jazz Rap", "description": "Live jazz instrumentation with conscious lyrics (95 BPM)"},
        {"subgenre": "Industrial Hip Hop", "description": "Harsh, mechanical sounds with aggressive delivery (100 BPM)"},
        {"subgenre": "Lo-Fi Hip Hop", "description": "Chill, nostalgic beats with vinyl crackle (80 BPM)"},
        {"subgenre": "Drill", "description": "Chicago-style menacing beats (65 BPM)"},
    ],
    "Pop": [
        {"subgenre": "Dark Pop", "description": "Moody, atmospheric with alternative influences (100 BPM)"},
        {"subgenre": "Electropop", "description": "Synth-driven with electronic production (120 BPM)"},
        {"subgenre": "Indie Pop", "description": "Lo-fi, DIY aesthetic with authentic vocals (110 BPM)"},
        {"subgenre": "K-Pop", "description": "Korean pop with genre-blending production (130 BPM)"},
        {"subgenre": "Synth-Pop", "description": "80s-inspired synthesizer melodies (115 BPM)"},
        {"subgenre": "Dream Pop", "description": "Ethereal, reverb-heavy with shoegaze elements (90 BPM)"},
        {"subgenre": "Alt-Pop", "description": "Alternative, experimental with unconventional structures (105 BPM)"},
        {"subgenre": "Bedroom Pop", "description": "Home-recorded, intimate with lo-fi production (95 BPM)"},
        {"subgenre": "Power Pop", "description": "High-energy with rock guitars and catchy hooks (140 BPM)"},
        {"subgenre": "Hyperpop", "description": "Maximalist, auto-tuned, genre-defying (170 BPM)"},
        {"subgenre": "Art Pop", "description": "Avant-garde, conceptual with experimental sounds (100 BPM)"},
        {"subgenre": "Bubblegum Pop", "description": "Upbeat, innocent with simple melodies (128 BPM)"},
        {"subgenre": "Sophisti-Pop", "description": "Jazz-influenced with polished production (110 BPM)"},
        {"subgenre": "Synthpop 2.0", "description": "Modern synth revival with analog warmth (122 BPM)"},
        {"subgenre": "Chamber Pop", "description": "Orchestral arrangements with baroque influences (85 BPM)"},
    ],
    "Rock": [
        {"subgenre": "Post-Punk Revival", "description": "Angular guitars with danceable rhythms (120 BPM)"},
        {"subgenre": "Shoegaze", "description": "Wall of distortion with dreamy vocals (100 BPM)"},
        {"subgenre": "Math Rock", "description": "Complex time signatures with technical playing (140 BPM)"},
        {"subgenre": "Garage Rock", "description": "Raw, lo-fi with punk energy (150 BPM)"},
        {"subgenre": "Indie Rock", "description": "Alternative, DIY ethos with authentic sound (110 BPM)"},
        {"subgenre": "Post-Rock", "description": "Instrumental, atmospheric with slow builds (80 BPM)"},
        {"subgenre": "Psychedelic Rock", "description": "Trippy effects with experimental structures (90 BPM)"},
        {"subgenre": "Noise Rock", "description": "Dissonant, abrasive with feedback (130 BPM)"},
        {"subgenre": "Stoner Rock", "description": "Heavy, fuzzy riffs with sludgy tempo (70 BPM)"},
        {"subgenre": "Emo", "description": "Emotional lyrics with punk-influenced sound (160 BPM)"},
        {"subgenre": "Surf Rock", "description": "Reverb-drenched guitars with beachy vibes (140 BPM)"},
        {"subgenre": "Art Rock", "description": "Experimental, progressive with conceptual themes (95 BPM)"},
        {"subgenre": "Grunge", "description": "Heavy distortion with angst-filled vocals (90 BPM)"},
        {"subgenre": "Britpop", "description": "British-influenced with catchy melodies (120 BPM)"},
        {"subgenre": "Metalcore", "description": "Heavy breakdowns with screamed vocals (180 BPM)"},
    ],
    "Latin": [
        {"subgenre": "Cumbia", "description": "Colombian rhythms with accordion melodies (100 BPM)"},
        {"subgenre": "Salsa", "description": "Afro-Cuban percussion with brass sections (180 BPM)"},
        {"subgenre": "Bachata", "description": "Dominican guitar with romantic lyrics (120 BPM)"},
        {"subgenre": "Merengue", "description": "Fast, 2/4 time with accordion (140 BPM)"},
        {"subgenre": "Corridos Tumbados", "description": "Mexican ballads with trap beats (90 BPM)"},
        {"subgenre": "Regional Mexicano", "description": "Banda, norteño with traditional instruments (110 BPM)"},
        {"subgenre": "Samba", "description": "Brazilian percussion with syncopated rhythms (180 BPM)"},
        {"subgenre": "Bossa Nova", "description": "Smooth jazz-influenced with Portuguese lyrics (120 BPM)"},
        {"subgenre": "Tango", "description": "Argentine passion with bandoneón (120 BPM)"},
        {"subgenre": "Bolero", "description": "Romantic ballads with Cuban origins (60 BPM)"},
        {"subgenre": "Vallenato", "description": "Colombian accordion with narrative lyrics (110 BPM)"},
        {"subgenre": "Ranchera", "description": "Mexican mariachi with emotional vocals (90 BPM)"},
        {"subgenre": "Champeta", "description": "Afro-Colombian with Caribbean influences (100 BPM)"},
        {"subgenre": "Son Cubano", "description": "Traditional Cuban with tres guitar (130 BPM)"},
        {"subgenre": "Timba", "description": "Modern Cuban salsa with funk elements (200 BPM)"},
    ],
    "R&B": [
        {"subgenre": "Contemporary R&B", "description": "Modern production with hip hop influences (90 BPM)"},
        {"subgenre": "Alternative R&B", "description": "Experimental, moody with unconventional sounds (75 BPM)"},
        {"subgenre": "Neo-Soul", "description": "Organic instruments with conscious lyrics (85 BPM)"},
        {"subgenre": "Trap Soul", "description": "Trap beats with R&B melodies (70 BPM)"},
        {"subgenre": "PBR&B", "description": "Post-dubstep influences with R&B vocals (80 BPM)"},
        {"subgenre": "Quiet Storm", "description": "Smooth, romantic with soft grooves (65 BPM)"},
        {"subgenre": "New Jack Swing", "description": "90s fusion of R&B and hip hop (100 BPM)"},
        {"subgenre": "Funk-Soul", "description": "Groovy basslines with soulful vocals (110 BPM)"},
        {"subgenre": "Electro-Soul", "description": "Electronic production with soul vocals (95 BPM)"},
        {"subgenre": "Bedroom R&B", "description": "Intimate, home-recorded with minimal production (80 BPM)"},
        {"subgenre": "Gospel-Soul Fusion", "description": "Church influences with secular themes (75 BPM)"},
        {"subgenre": "Psychedelic Soul", "description": "Trippy effects with soulful grooves (90 BPM)"},
        {"subgenre": "Progressive R&B", "description": "Experimental structures with complex harmonies (88 BPM)"},
        {"subgenre": "Retro-Soul", "description": "60s/70s-inspired with vintage production (95 BPM)"},
        {"subgenre": "UK R&B", "description": "British take on R&B with grime influences (130 BPM)"},
    ],
}


def extract_json(text: str):
    """
    Robust JSON extractor for AI responses
    Tries multiple parsing strategies to extract valid JSON from messy AI output

    Args:
        text: Raw AI response text

    Returns:
        Parsed JSON object (list or dict)

    Raises:
        ValueError: If no valid JSON could be extracted
    """
    if not text or not text.strip():
        raise ValueError("Empty or whitespace-only text provided")

    # Strategy 1: Pure JSON (fastest path)
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        pass  # Continue to next strategy

    # Strategy 2: Markdown Code Blocks ```json ... ``` or ``` ... ```
    match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Strategy 3: Find JSON array [ ... ] (for lists)
    try:
        start = text.find('[')
        end = text.rfind(']') + 1
        if start != -1 and end > start:
            json_str = text[start:end]
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass

    # Strategy 4: Find JSON object { ... } (for objects)
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end > start:
            json_str = text[start:end]
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass

    # Strategy 5: Try to clean common AI response patterns
    # Remove common prefixes like "Here is the JSON:", "```json", etc.
    cleaned = re.sub(r'^.*?(\[|\{)', r'\1', text, flags=re.DOTALL)
    cleaned = re.sub(r'(\]|\}).*?$', r'\1', cleaned, flags=re.DOTALL)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    raise ValueError(f"No valid JSON found in AI response. Text preview: {text[:200]}")


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

        prompt = f"""You are a music trend analyst with REAL-TIME access to Google Search data.

CRITICAL: You MUST use the Google Search tool to find CURRENT, LIVE data. Do NOT rely on training data.

SEARCH QUERY: "{search_query}"

Your task: Identify the TOP 20 VIRAL MUSIC TRENDS right now (as of {current_month} {current_year}).

REQUIREMENTS:
1. USE GOOGLE SEARCH to find ACTUAL viral genres/styles trending on TikTok, Spotify, and YouTube Shorts RIGHT NOW
2. Include both audio trends AND visual aesthetics (e.g., "Dirty Aesthetic", "Slowed + Reverb")
3. Prioritize genres that are CURRENTLY viral in {current_month} {current_year} (not just established genres)
4. Mix platforms: ~40% TikTok, ~30% YouTube Shorts, ~30% Spotify
5. Each trend must be REAL and SPECIFIC (not generic) - verify with Google Search results

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
            # Get AI response with Google Search Grounding for real-time data
            logger.info("🤖 Calling Gemini AI with Google Search grounding...")
            ai_response = await gemini_service.generate_text(
                prompt,
                use_search=True,
                response_mime_type="application/json"
            )

            logger.info(f"📥 Received AI response ({len(ai_response)} chars)")

            # Parse JSON response with robust extractor
            trends = extract_json(ai_response)

            # Validate it's a list
            if not isinstance(trends, list):
                raise ValueError(f"Expected list, got {type(trends)}")

            # Ensure we have trends
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

    async def _clean_json_with_ai(self, raw_text: str) -> str:
        """
        Use AI to clean and extract valid JSON from messy text output
        Refinement Pattern: Fast, cheap model (Gemini Flash) for pure formatting task

        Args:
            raw_text: Messy AI response that might contain JSON

        Returns:
            Clean JSON string (array or object)

        Raises:
            Exception: If AI cleaner fails
        """
        logger.info("🧹 Calling AI JSON Cleaner (Gemini Flash)...")

        clean_prompt = f"""You are a JSON formatter. Your ONLY job is to extract the data array from the following text and return ONLY valid JSON.

RULES:
1. Return ONLY the JSON array/object - no markdown blocks, no text before/after
2. Do NOT add explanations or comments
3. Ensure the JSON is valid and parseable
4. Preserve all data from the original text

TEXT:
{raw_text}

Respond with pure JSON only:"""

        try:
            # Use Gemini Flash (fast, cheap, good for formatting tasks)
            # Temperature 0.0 for maximum precision (no creativity needed)
            clean_response = await gemini_service.generate_text(
                clean_prompt,
                model_name="gemini-1.5-flash",
                temperature=0.0,
                max_tokens=4096,
                response_mime_type="application/json"
            )

            logger.info(f"✅ AI Cleaner returned {len(clean_response)} chars")
            return clean_response

        except Exception as e:
            logger.error(f"❌ AI Cleaner failed: {e}")
            raise

    async def generate_genre_variations(self, super_genre: str, num_variations: int = 20) -> List[Dict[str, str]]:
        """
        Generate music genre variations for a given super genre
        Hybrid Strategy: Check static database first, then use AI for unknown genres

        Args:
            super_genre: Main genre (e.g., "Electronic", "HipHop")
            num_variations: Number of variations to generate (default: 20)

        Returns:
            List of genre variations with descriptions
        """
        logger.info(f"🎵 Generating {num_variations} variations for: {super_genre}")

        # Always use AI generation for fresh ideas
        logger.info(f"🤖 Calling AI for generation of {super_genre} variations")

        prompt = f"""You are a music trend expert and genre specialist with deep knowledge of subgenres.

TASK: Generate {num_variations} SPECIFIC subgenre variations for "{super_genre}".

REQUIREMENTS:
1. Each variation must be a REAL, specific subgenre (not generic)
2. Include both established and emerging/viral subgenres
3. Add a brief description (1 sentence, max 15 words)
4. Mix classic subgenres with modern fusion styles
5. Consider current TikTok, YouTube, and Spotify trends
6. Respond ONLY with a raw JSON array. Do not use Markdown code blocks.

FORMAT (exactly like this):
[
  {{"subgenre": "Liquid Drum & Bass", "description": "Smooth, melodic DnB with soulful vocals and atmospheric pads"}},
  {{"subgenre": "Neurofunk", "description": "Dark, technical DnB with complex bass design and sci-fi elements"}},
  {{"subgenre": "Jump Up", "description": "High-energy DnB with bouncy basslines and crowd-hyping drops"}}
]

Generate exactly {num_variations} variations for: {super_genre}

Return ONLY the JSON array, nothing else."""

        try:
            # Get AI response with JSON mode enabled
            logger.info("🤖 Calling Gemini AI with JSON response mode...")
            ai_response = await gemini_service.generate_text(
                prompt,
                temperature=0.7,
                response_mime_type="application/json"
            )

            if not ai_response:
                raise ValueError("Empty response from Gemini CLI wrapper")

            logger.info(f"📥 Received AI response ({len(ai_response)} chars)")

            # Parse JSON using robust extractor with AI Cleaner fallback
            variations = None
            parsing_error = None

            # STEP 1: Try local JSON parsing first (fastest)
            try:
                variations = extract_json(ai_response)
                logger.info("✅ Local JSON parsing successful")
            except Exception as local_parse_error:
                logger.warning(f"⚠️ Local JSON parsing failed: {local_parse_error}")
                logger.error(f"📄 RAW AI RESPONSE:\n{ai_response[:1000]}")  # Log first 1000 chars
                parsing_error = local_parse_error

                # STEP 2: Try AI JSON Cleaner (Refinement Pattern)
                try:
                    logger.info("🔄 Attempting AI JSON Cleaner (Gemini Flash)...")
                    cleaned_response = await self._clean_json_with_ai(ai_response)
                    logger.info(f"🧹 Cleaned response ({len(cleaned_response)} chars)")
                    variations = extract_json(cleaned_response)
                    logger.info("✅ AI Cleaner successfully repaired JSON")
                except Exception as cleaner_error:
                    logger.error(f"❌ AI Cleaner also failed: {cleaner_error}")
                    logger.error(f"📄 CLEANED RESPONSE:\n{cleaned_response[:500] if 'cleaned_response' in locals() else 'N/A'}")
                    # Re-raise original error for fallback
                    raise parsing_error

            # Validation: Ensure it's a list with valid items
            if not isinstance(variations, list):
                raise ValueError(f"Expected list, got {type(variations)}")

            if len(variations) == 0:
                raise ValueError("Empty variations list")

            # Validate structure of each variation
            valid_variations = []
            for item in variations:
                if isinstance(item, dict) and "subgenre" in item:
                    # Ensure description exists
                    if "description" not in item:
                        item["description"] = f"A unique style of {super_genre}"
                    valid_variations.append(item)

            if len(valid_variations) == 0:
                raise ValueError("No valid variations found")

            logger.info(f"✅ Successfully parsed {len(valid_variations)} AI-generated variations")
            return valid_variations[:num_variations]

        except Exception as e:
            logger.error(f"❌ AI generation completely failed: {e}")
            logger.error(f"❌ Exception type: {type(e).__name__}")
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"❌ Full traceback:\n{error_trace}")
            logger.error(f"🔍 SUPER_GENRE: {super_genre}")
            logger.error(f"🔍 NUM_VARIATIONS: {num_variations}")

            # DO NOT USE FALLBACK - Raise exception so we can see the actual problem
            raise Exception(f"AI generation failed for genre '{super_genre}': {str(e)}")

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
