"""
Agent 10: YouTube Packager - "The Marketing Strategist"
Generates viral metadata and thumbnail prompts for YouTube uploads
"""

from typing import Optional, Dict, Any
from app.infrastructure.external_services.gemini_service import gemini_service
from app.utils.logger import setup_logger

logger = setup_logger("Agent10_YouTube")


class Agent10YouTubePackager:
    """Singleton service for YouTube upload package generation"""

    _instance: Optional['Agent10YouTubePackager'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def generate_metadata(
        self,
        song_title: str,
        artist: str,
        genre: str = None,
        mood: str = None,
        style: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Generate viral YouTube metadata

        Args:
            song_title: Song title
            artist: Artist name
            genre: Music genre (optional)
            mood: Song mood (optional)
            style: Visual style dict (optional)

        Returns:
            Dict with title, description, tags
        """
        logger.info(f"Generating YouTube metadata for '{song_title}' by {artist}")

        # Build context for AI
        context_parts = [f"Song: {song_title}", f"Artist: {artist}"]
        if genre:
            context_parts.append(f"Genre: {genre}")
        if mood:
            context_parts.append(f"Mood: {mood}")
        if style:
            context_parts.append(f"Visual Style: {style.get('name', 'N/A')}")

        context = "\n".join(context_parts)

        # Generate metadata with Gemini
        metadata_prompt = f"""You are a YouTube marketing expert specializing in music videos.

Generate viral YouTube metadata for this music video:

{context}

**Requirements:**

1. **TITLE** (max 100 chars):
   - Must be catchy and click-worthy
   - Include artist name
   - Use emojis strategically (1-2 max)
   - Optimize for YouTube search
   - Example format: "Artist Name - Song Title (Official Music Video) 🎵"

2. **DESCRIPTION** (500-1000 chars):
   - First 2 lines are CRITICAL (shown in search)
   - Include song credits and artist info
   - Add relevant timestamps if applicable
   - Social media links placeholders
   - Call to action (like, subscribe, comment)
   - SEO keywords naturally integrated
   - Professional but engaging tone

3. **TAGS** (15-20 tags):
   - Mix of broad and specific tags
   - Include: genre, mood, artist name, trending keywords
   - Format as comma-separated list
   - Focus on discoverability

**Output format:**
```
TITLE:
[your title here]

DESCRIPTION:
[your description here]

TAGS:
[tag1, tag2, tag3, ...]
```

Generate the metadata now:"""

        try:
            ai_response = await gemini_service.generate_text(metadata_prompt, temperature=0.8)

            # Parse response
            title = ""
            description = ""
            tags = []

            sections = ai_response.split('\n\n')
            current_section = None

            for section in sections:
                section = section.strip()

                if section.startswith('TITLE:'):
                    current_section = 'title'
                    title = section.replace('TITLE:', '').strip()
                elif section.startswith('DESCRIPTION:'):
                    current_section = 'description'
                    description = section.replace('DESCRIPTION:', '').strip()
                elif section.startswith('TAGS:'):
                    current_section = 'tags'
                    tags_text = section.replace('TAGS:', '').strip()
                    # Parse tags (handle both comma-separated and newline-separated)
                    tags = [tag.strip() for tag in tags_text.replace('\n', ',').split(',') if tag.strip()]
                elif current_section == 'description' and section and not section.startswith('TAGS'):
                    # Multi-paragraph description
                    description += '\n\n' + section

            # Fallback if parsing failed
            if not title:
                title = f"{artist} - {song_title} (Official Music Video)"
            if not description:
                description = self._generate_fallback_description(song_title, artist, genre, mood)
            if not tags:
                tags = self._generate_fallback_tags(genre, mood, artist)

            # Clean up title (max 100 chars)
            if len(title) > 100:
                title = title[:97] + "..."

            logger.info(f"Generated metadata: {len(tags)} tags, {len(description)} chars description")

            return {
                "title": title,
                "description": description,
                "tags": tags,
                "hashtags": self._extract_hashtags(tags)
            }

        except Exception as e:
            logger.error(f"Failed to generate metadata with AI: {e}")
            return {
                "title": f"{artist} - {song_title} (Official Music Video)",
                "description": self._generate_fallback_description(song_title, artist, genre, mood),
                "tags": self._generate_fallback_tags(genre, mood, artist),
                "hashtags": []
            }

    async def generate_thumbnail_prompt(
        self,
        song_title: str,
        artist: str,
        style: Optional[Dict[str, str]] = None,
        mood: str = None
    ) -> str:
        """
        Generate thumbnail image prompt for Imagen 3 / Midjourney

        Args:
            song_title: Song title
            artist: Artist name
            style: Visual style from Agent 5 (optional)
            mood: Song mood (optional)

        Returns:
            Image generation prompt string
        """
        logger.info(f"Generating thumbnail prompt for '{song_title}'")

        # Build context
        context_parts = [f"Music Video: {song_title} by {artist}"]
        if mood:
            context_parts.append(f"Mood: {mood}")

        style_suffix = ""
        if style and style.get('suffix'):
            style_suffix = style.get('suffix')
            context_parts.append(f"Visual Style: {style.get('name')}")

        context = "\n".join(context_parts)

        # Generate prompt with AI
        thumbnail_prompt = f"""You are a thumbnail designer for viral music videos.

Create an image generation prompt for a YouTube thumbnail:

{context}

**Thumbnail Requirements:**
- YouTube format: 1280x720px (16:9)
- Must be eye-catching and click-worthy
- Should represent the video's visual style
- Include the artist or symbolic representation
- Bold, high-contrast visuals
- Cinematic and professional

**Visual Style Context:**
{style_suffix if style_suffix else "Cinematic music video aesthetic"}

**Output:**
Generate a detailed image prompt (100-150 words) for Imagen 3 or Midjourney.
Focus on: composition, colors, lighting, subject, mood, and technical style.

Format: Just the prompt text, no explanation.

Generate the thumbnail prompt now:"""

        try:
            thumbnail_prompt_text = await gemini_service.generate_text(
                thumbnail_prompt,
                temperature=0.75
            )

            # Clean up response
            thumbnail_prompt_text = thumbnail_prompt_text.strip()

            # Ensure it includes 16:9 aspect ratio hint
            if '16:9' not in thumbnail_prompt_text and 'aspect ratio' not in thumbnail_prompt_text.lower():
                thumbnail_prompt_text += ", 16:9 aspect ratio, YouTube thumbnail format"

            logger.info("Thumbnail prompt generated successfully")
            return thumbnail_prompt_text

        except Exception as e:
            logger.error(f"Failed to generate thumbnail prompt: {e}")

            # Fallback thumbnail prompt
            if style_suffix:
                return f"Music video thumbnail for {artist} - {song_title}, {style_suffix}, cinematic composition, bold typography, high contrast, vibrant colors, 16:9 aspect ratio, YouTube thumbnail format"
            else:
                return f"Music video thumbnail for {artist} - {song_title}, cinematic lighting, bold composition, vibrant colors, artistic portrait, high contrast, 16:9 aspect ratio, YouTube thumbnail format"

    def _generate_fallback_description(
        self,
        song_title: str,
        artist: str,
        genre: str = None,
        mood: str = None
    ) -> str:
        """Generate fallback description if AI fails"""
        desc_lines = [
            f"🎵 {artist} - {song_title} (Official Music Video)",
            "",
            f"Watch the official music video for '{song_title}' by {artist}.",
        ]

        if genre:
            desc_lines.append(f"Genre: {genre}")
        if mood:
            desc_lines.append(f"Vibe: {mood}")

        desc_lines.extend([
            "",
            "🔔 Subscribe for more music videos!",
            "👍 Like if you enjoyed this video",
            "💬 Comment your favorite moment below",
            "",
            "Follow us:",
            "Instagram: [Your Instagram]",
            "TikTok: [Your TikTok]",
            "Spotify: [Your Spotify]",
            "",
            "Credits:",
            f"Artist: {artist}",
            "Video Production: [Your Production Company]",
            "",
            "#MusicVideo #NewMusic #OfficialVideo"
        ])

        return "\n".join(desc_lines)

    def _generate_fallback_tags(
        self,
        genre: str = None,
        mood: str = None,
        artist: str = None
    ) -> list:
        """Generate fallback tags if AI fails"""
        tags = [
            "music video",
            "official video",
            "new music",
            "music 2025"
        ]

        if artist:
            tags.append(artist.lower())
        if genre:
            tags.extend([genre.lower(), f"{genre.lower()} music"])
        if mood:
            tags.append(mood.lower())

        tags.extend([
            "viral music",
            "trending",
            "music clips",
            "official music video",
            "new release",
            "music premiere"
        ])

        return tags[:20]

    def _extract_hashtags(self, tags: list) -> list:
        """Convert tags to hashtags (top 5 most relevant)"""
        hashtags = []

        priority_tags = [tag for tag in tags if len(tag.split()) <= 2]  # Prefer short tags
        for tag in priority_tags[:5]:
            # Convert to hashtag format
            hashtag = "#" + tag.replace(" ", "").replace(",", "")
            hashtags.append(hashtag)

        return hashtags


# Singleton instance
agent10_service = Agent10YouTubePackager()
