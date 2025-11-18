"""
Agent 14: Narrator (Voiceover Service)

Prepares voiceover scripts for documentary narration.
Supports hybrid workflow: API automation (ElevenLabs) or manual download.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import tempfile

logger = logging.getLogger(__name__)


class NarratorService:
    """Agent 14: Voiceover preparation with hybrid mode support"""

    def __init__(self):
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        logger.info("Agent 14 (Narrator) initialized")

    async def prepare_voiceover_script(
        self,
        script: Dict[str, Any],
        mode: str = "manual",
        voice_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Prepare voiceover from documentary script

        Args:
            script: Complete script from Agent 13
            mode: "manual" (download text) or "api" (ElevenLabs)
            voice_id: ElevenLabs voice ID (for API mode)

        Returns:
            {
                "success": bool,
                "mode": str,
                "script_text": str,  # For manual download
                "audio_url": str,    # For API mode (future)
                "duration_estimate": float,  # Estimated minutes
                "word_count": int
            }
        """
        try:
            # Extract narration text from all chapters
            script_text = self._extract_narration_text(script)

            # Calculate duration estimate (average speaking rate: 150 WPM)
            word_count = len(script_text.split())
            duration_minutes = word_count / 150

            if mode == "manual":
                # Manual mode: Create clean text file for download
                result = {
                    "success": True,
                    "mode": "manual",
                    "script_text": script_text,
                    "duration_estimate": round(duration_minutes, 1),
                    "word_count": word_count,
                    "instructions": self._get_manual_instructions()
                }
                logger.info(f"Voiceover script prepared (Manual mode): {word_count} words, ~{duration_minutes:.1f} min")
                return result

            elif mode == "api":
                # API mode: Call ElevenLabs (mockup for now)
                if not self.elevenlabs_api_key:
                    logger.warning("ElevenLabs API key not configured, falling back to manual mode")
                    return await self.prepare_voiceover_script(script, mode="manual")

                # Future: Call ElevenLabs API
                audio_url = await self._generate_with_elevenlabs(script_text, voice_id)

                result = {
                    "success": True,
                    "mode": "api",
                    "audio_url": audio_url,
                    "duration_estimate": round(duration_minutes, 1),
                    "word_count": word_count,
                    "script_text": script_text  # Include text as backup
                }
                logger.info(f"Voiceover generated via API: {word_count} words")
                return result

            else:
                raise ValueError(f"Invalid mode: {mode}. Use 'manual' or 'api'")

        except Exception as e:
            logger.error(f"Error preparing voiceover: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "mode": mode
            }

    def _extract_narration_text(self, script: Dict[str, Any]) -> str:
        """Extract clean narration text from script structure"""
        narration_parts = []

        # Add title and logline as intro context
        if "title" in script:
            narration_parts.append(f"# {script['title']}\n")

        # Extract narration from each chapter
        if "chapters" in script:
            for chapter in script["chapters"]:
                chapter_num = chapter.get("chapter_number", "")
                chapter_title = chapter.get("title", "")
                narration = chapter.get("narration", "")

                # Format chapter header
                if chapter_title:
                    narration_parts.append(f"\n## Chapter {chapter_num}: {chapter_title}\n")

                # Add narration text
                if narration:
                    narration_parts.append(narration.strip())

        return "\n\n".join(narration_parts)

    def _get_manual_instructions(self) -> str:
        """Get instructions for manual ElevenLabs workflow"""
        return """
**Manual Voiceover Workflow:**

1. **Download** the script text below
2. **Go to** https://elevenlabs.io
3. **Select** a professional narrator voice (recommended: "Josh" or "Bella")
4. **Paste** the script into the text input
5. **Generate** the audio
6. **Download** the MP3 file
7. **Upload** the finished MP3 back to this interface

**Settings Recommendation:**
- Stability: 50-60%
- Clarity: 70-80%
- Style Exaggeration: 0-10%
        """.strip()

    async def _generate_with_elevenlabs(
        self,
        text: str,
        voice_id: Optional[str] = None
    ) -> str:
        """
        Generate voiceover using ElevenLabs API

        NOTE: This is a mockup implementation for future API integration
        """
        # TODO: Implement actual ElevenLabs API call
        # For now, return a placeholder
        logger.info("ElevenLabs API call (mockup) - Future implementation")

        # Mockup return
        return "https://api.elevenlabs.io/mockup/audio.mp3"

    async def analyze_uploaded_audio(
        self,
        audio_file_path: str
    ) -> Dict[str, Any]:
        """
        Analyze uploaded voiceover audio

        Args:
            audio_file_path: Path to uploaded MP3/WAV file

        Returns:
            {
                "success": bool,
                "duration": float,  # seconds
                "sample_rate": int,
                "channels": int,
                "file_size_mb": float
            }
        """
        try:
            # Get file size
            file_size = os.path.getsize(audio_file_path)
            file_size_mb = file_size / (1024 * 1024)

            # Basic analysis (future: use librosa or pydub for detailed analysis)
            result = {
                "success": True,
                "file_path": audio_file_path,
                "file_size_mb": round(file_size_mb, 2),
                "format": os.path.splitext(audio_file_path)[1],
                "message": "Audio file uploaded successfully"
            }

            logger.info(f"Audio analyzed: {file_size_mb:.2f} MB")
            return result

        except Exception as e:
            logger.error(f"Error analyzing audio: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance
narrator_service = NarratorService()
