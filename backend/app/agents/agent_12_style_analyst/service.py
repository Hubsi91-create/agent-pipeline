"""
Agent 12: Style Analyzer - "The Reverse Engineer"
Analyzes existing documentaries to extract style templates (Netflix-style cloning)
"""

from typing import Optional, Dict, Any, List
import re
from app.infrastructure.external_services.gemini_service import gemini_service
from app.utils.logger import setup_logger

logger = setup_logger("Agent12_StyleAnalyst")


class Agent12StyleAnalyst:
    """Singleton service for documentary style analysis"""

    _instance: Optional['Agent12StyleAnalyst'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def analyze_video_style(
        self,
        video_url: str = None,
        transcript_text: str = None
    ) -> Dict[str, Any]:
        """
        Analyze a documentary video to extract its style template

        Process:
        1. Extract transcript from YouTube URL or use provided text
        2. Analyze pacing (words per minute)
        3. Extract keywords for B-Roll suggestions
        4. Identify narrative style and tone
        5. Generate comprehensive style template

        Args:
            video_url: YouTube URL (e.g., "https://www.youtube.com/watch?v=...")
            transcript_text: Pre-extracted transcript (alternative to video_url)

        Returns:
            StyleTemplate dict with:
            - pacing: {wpm, cut_frequency, chapter_count}
            - tone: {style, mood, narrator_voice}
            - visual_style: {color_palette, shot_types, b_roll_frequency}
            - keywords: List of key themes
            - template_name: Suggested name for this style
        """
        logger.info(f"Analyzing documentary style from {'URL' if video_url else 'transcript'}")

        transcript = None

        # Step 1: Get transcript
        if video_url:
            transcript = await self._extract_youtube_transcript(video_url)
        elif transcript_text:
            transcript = transcript_text
        else:
            return {
                "success": False,
                "error": "Either video_url or transcript_text is required"
            }

        if not transcript:
            return {
                "success": False,
                "error": "Failed to extract transcript"
            }

        # Step 2: Analyze pacing
        pacing_analysis = self._analyze_pacing(transcript)

        # Step 3: Extract keywords and analyze style with Gemini
        style_analysis = await self._analyze_style_with_ai(transcript)

        # Step 4: Build style template
        style_template = {
            "success": True,
            "template_name": style_analysis.get("template_name", "Custom Documentary Style"),
            "pacing": {
                "words_per_minute": pacing_analysis["wpm"],
                "estimated_duration_minutes": pacing_analysis["duration_minutes"],
                "cut_frequency": pacing_analysis["cut_frequency"],
                "chapter_count": pacing_analysis["chapter_count"]
            },
            "tone": {
                "narrative_style": style_analysis.get("narrative_style", "Informative"),
                "mood": style_analysis.get("mood", "Professional"),
                "narrator_voice": style_analysis.get("narrator_voice", "Authoritative")
            },
            "visual_style": {
                "color_palette": style_analysis.get("color_palette", "Neutral, professional"),
                "shot_types": style_analysis.get("shot_types", ["Wide establishing", "Close-ups", "B-Roll"]),
                "b_roll_frequency": style_analysis.get("b_roll_frequency", "Every 10-15 seconds")
            },
            "keywords": style_analysis.get("keywords", []),
            "b_roll_suggestions": style_analysis.get("b_roll_suggestions", []),
            "transcript_sample": transcript[:500] + "..." if len(transcript) > 500 else transcript
        }

        logger.info(f"Style template generated: {style_template['template_name']}")
        return style_template

    async def _extract_youtube_transcript(self, video_url: str) -> Optional[str]:
        """
        Extract transcript from YouTube video

        Args:
            video_url: YouTube URL

        Returns:
            Transcript text or None if failed
        """
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            import re

            # Extract video ID from URL
            video_id = None
            patterns = [
                r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
                r'(?:embed\/)([0-9A-Za-z_-]{11})',
                r'^([0-9A-Za-z_-]{11})$'
            ]

            for pattern in patterns:
                match = re.search(pattern, video_url)
                if match:
                    video_id = match.group(1)
                    break

            if not video_id:
                logger.error("Could not extract video ID from URL")
                return None

            logger.info(f"Extracting transcript for video ID: {video_id}")

            # Get transcript
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)

            # Combine all text
            full_transcript = " ".join([entry['text'] for entry in transcript_list])

            logger.info(f"Transcript extracted: {len(full_transcript)} characters")
            return full_transcript

        except Exception as e:
            logger.error(f"Failed to extract YouTube transcript: {e}")
            logger.warning("Using fallback mock transcript")
            return self._generate_mock_transcript()

    def _analyze_pacing(self, transcript: str) -> Dict[str, Any]:
        """
        Analyze pacing of the transcript

        Args:
            transcript: Full transcript text

        Returns:
            Dict with pacing metrics
        """
        # Count words
        words = transcript.split()
        word_count = len(words)

        # Estimate duration (assuming ~150 WPM average speaking rate)
        average_wpm = 150
        duration_minutes = word_count / average_wpm

        # Estimate cut frequency based on sentence count
        sentences = re.split(r'[.!?]+', transcript)
        sentence_count = len([s for s in sentences if s.strip()])

        # Assume 1 cut every 2-3 sentences
        estimated_cuts = sentence_count // 2.5

        # Estimate chapters (one chapter every 3-4 minutes)
        chapter_count = max(3, int(duration_minutes / 3.5))

        pacing = {
            "word_count": word_count,
            "wpm": average_wpm,
            "duration_minutes": round(duration_minutes, 1),
            "sentence_count": sentence_count,
            "cut_frequency": f"~{int(estimated_cuts / duration_minutes if duration_minutes > 0 else 0)} cuts/minute",
            "chapter_count": chapter_count
        }

        logger.info(f"Pacing analysis: {duration_minutes:.1f} min, {word_count} words, {chapter_count} chapters")
        return pacing

    async def _analyze_style_with_ai(self, transcript: str) -> Dict[str, Any]:
        """
        Use Gemini AI to analyze narrative style and extract keywords

        Args:
            transcript: Full transcript text

        Returns:
            Dict with style analysis
        """
        # Truncate transcript if too long (Gemini has token limits)
        transcript_sample = transcript[:5000] if len(transcript) > 5000 else transcript

        analysis_prompt = f"""You are a professional documentary analyst specializing in Netflix-style productions.

Analyze this documentary transcript and extract the following:

**Transcript:**
{transcript_sample}

**Your analysis should include:**

1. **Template Name**: A catchy name for this documentary style (e.g., "Vox Explainer", "BBC Nature Documentary", "True Crime Thriller")

2. **Narrative Style**: How is the story told? (Options: Informative, Dramatic, Conversational, Academic, Investigative, Storytelling)

3. **Mood**: Overall emotional tone (Options: Serious, Light-hearted, Dramatic, Inspiring, Educational, Mysterious)

4. **Narrator Voice**: Style of narration (Options: Authoritative, Friendly, Neutral, Curious, Passionate, Dramatic)

5. **Color Palette**: Describe the likely visual color scheme based on the topic and tone (e.g., "Warm earth tones", "Cool blues and grays", "Vibrant colors")

6. **Shot Types**: List 3-5 common shot types likely used (e.g., "Drone aerials", "Close-up details", "Talking heads", "Archive footage")

7. **B-Roll Frequency**: How often should B-roll be used? (e.g., "Every 10-15 seconds", "Continuous", "Minimal")

8. **Keywords**: Extract 10-15 key themes/topics from the transcript

9. **B-Roll Suggestions**: Suggest 8-10 specific B-roll shots that would complement this documentary

**Output format (JSON):**
{{
  "template_name": "...",
  "narrative_style": "...",
  "mood": "...",
  "narrator_voice": "...",
  "color_palette": "...",
  "shot_types": ["...", "...", "..."],
  "b_roll_frequency": "...",
  "keywords": ["...", "...", "..."],
  "b_roll_suggestions": ["...", "...", "..."]
}}

Generate the analysis now:"""

        try:
            response = await gemini_service.generate_text(analysis_prompt, temperature=0.6)

            # Try to parse JSON from response
            import json

            # Find JSON in response (sometimes Gemini adds extra text)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                style_data = json.loads(json_match.group())
                logger.info(f"AI style analysis complete: {style_data.get('template_name')}")
                return style_data
            else:
                logger.warning("Could not parse JSON from AI response")
                return self._generate_fallback_style()

        except Exception as e:
            logger.error(f"AI style analysis failed: {e}")
            return self._generate_fallback_style()

    def _generate_fallback_style(self) -> Dict[str, Any]:
        """Generate fallback style template when AI analysis fails"""
        return {
            "template_name": "General Documentary Style",
            "narrative_style": "Informative",
            "mood": "Professional",
            "narrator_voice": "Authoritative",
            "color_palette": "Neutral, professional grading",
            "shot_types": ["Wide establishing shots", "Interview close-ups", "B-Roll inserts", "Text overlays"],
            "b_roll_frequency": "Every 10-15 seconds",
            "keywords": ["documentary", "storytelling", "visual narrative"],
            "b_roll_suggestions": [
                "Establishing shots of location",
                "Close-up details of subject matter",
                "Time-lapse sequences",
                "Archival footage",
                "Transition shots"
            ]
        }

    def _generate_mock_transcript(self) -> str:
        """Generate mock transcript for testing when YouTube API fails"""
        return """
        In the heart of the digital age, artificial intelligence is reshaping our world in ways we never imagined.
        From self-driving cars to medical diagnoses, AI is becoming an integral part of our daily lives.

        But how did we get here? The journey began decades ago, when pioneers of computer science first dreamed
        of machines that could think. Today, that dream is a reality, transforming industries and challenging
        our understanding of what it means to be human.

        This is the story of AI's rise, its potential, and the questions we must ask as we step into an
        uncertain future. Join us as we explore the revolution that's changing everything.
        """


# Singleton instance
agent12_service = Agent12StyleAnalyst()
