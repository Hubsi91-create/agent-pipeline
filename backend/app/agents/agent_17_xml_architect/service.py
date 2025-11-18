"""
Agent 17: XML Architect

Generates FCPXML (Final Cut Pro XML) files for timeline import.
Compatible with DaVinci Resolve, Premiere Pro, and Final Cut Pro.
"""

import logging
from typing import Dict, Any, List, Optional
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime

logger = logging.getLogger(__name__)


class XMLArchitectService:
    """Agent 17: Generate edit-ready XML timelines"""

    def __init__(self):
        logger.info("Agent 17 (XML Architect) initialized")

    async def generate_fcpxml(
        self,
        assets: Dict[str, Any],
        script: Optional[Dict[str, Any]] = None,
        frame_rate: str = "24"
    ) -> Dict[str, Any]:
        """
        Generate FCPXML timeline from assets

        Args:
            assets: {
                "voiceover": {"file_path": str, "duration": float},
                "music": {"file_path": str, "duration": float},
                "videos": [{"file_path": str, "duration": float, "start_time": float}],
                "images": [{"file_path": str, "duration": float, "start_time": float}]
            }
            script: Optional script for chapter markers
            frame_rate: "24", "25", "30", or "60"

        Returns:
            {
                "success": bool,
                "xml_content": str,
                "timeline_duration": float,
                "tracks": int
            }
        """
        try:
            # Build FCPXML structure
            xml_root = self._create_fcpxml_root(frame_rate)

            # Create resources section
            resources = ET.SubElement(xml_root, "resources")
            self._add_resources(resources, assets)

            # Create timeline (sequence)
            library = ET.SubElement(xml_root, "library")
            event = ET.SubElement(library, "event", name="Documentary")
            project = ET.SubElement(event, "project", name="Main Timeline")

            sequence = ET.SubElement(project, "sequence", {
                "format": "r1",
                "duration": self._seconds_to_timecode(self._calculate_total_duration(assets), frame_rate)
            })

            spine = ET.SubElement(sequence, "spine")

            # Add assets to timeline
            self._add_voiceover_track(spine, assets.get("voiceover"), frame_rate)
            self._add_music_track(spine, assets.get("music"), frame_rate)
            self._add_video_track(spine, assets.get("videos", []), frame_rate)
            self._add_image_track(spine, assets.get("images", []), frame_rate)

            # Add chapter markers if script provided
            if script and "chapters" in script:
                self._add_chapter_markers(spine, script["chapters"], frame_rate)

            # Convert to pretty XML string
            xml_content = self._prettify_xml(xml_root)

            timeline_duration = self._calculate_total_duration(assets)
            track_count = self._count_tracks(assets)

            logger.info(f"Generated FCPXML: {timeline_duration:.1f}s, {track_count} tracks")

            return {
                "success": True,
                "xml_content": xml_content,
                "timeline_duration": timeline_duration,
                "tracks": track_count,
                "frame_rate": frame_rate
            }

        except Exception as e:
            logger.error(f"Error generating FCPXML: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "xml_content": ""
            }

    def _create_fcpxml_root(self, frame_rate: str) -> ET.Element:
        """Create root FCPXML element with proper namespaces"""
        root = ET.Element("fcpxml", {
            "version": "1.11"
        })

        # Add format definitions
        resources = ET.SubElement(root, "resources")
        ET.SubElement(resources, "format", {
            "id": "r1",
            "name": f"FFVideoFormat1080p{frame_rate}",
            "frameDuration": self._get_frame_duration(frame_rate),
            "width": "1920",
            "height": "1080"
        })

        return root

    def _get_frame_duration(self, frame_rate: str) -> str:
        """Get frame duration for given frame rate"""
        durations = {
            "24": "100/2400s",
            "25": "100/2500s",
            "30": "100/3000s",
            "60": "100/6000s"
        }
        return durations.get(frame_rate, "100/2400s")

    def _add_resources(self, resources: ET.Element, assets: Dict[str, Any]) -> None:
        """Add media resources to XML"""
        resource_id = 1

        # Add voiceover
        if assets.get("voiceover"):
            voiceover = assets["voiceover"]
            ET.SubElement(resources, "asset", {
                "id": f"r{resource_id}",
                "name": "Voiceover",
                "src": f"file://{voiceover.get('file_path', 'voiceover.mp3')}",
                "format": "r1"
            })
            resource_id += 1

        # Add music
        if assets.get("music"):
            music = assets["music"]
            ET.SubElement(resources, "asset", {
                "id": f"r{resource_id}",
                "name": "Background Music",
                "src": f"file://{music.get('file_path', 'music.mp3')}",
                "format": "r1"
            })
            resource_id += 1

        # Add videos
        for i, video in enumerate(assets.get("videos", [])):
            ET.SubElement(resources, "asset", {
                "id": f"r{resource_id}",
                "name": f"Video_{i+1}",
                "src": f"file://{video.get('file_path', f'video_{i+1}.mp4')}",
                "format": "r1"
            })
            resource_id += 1

        # Add images
        for i, image in enumerate(assets.get("images", [])):
            ET.SubElement(resources, "asset", {
                "id": f"r{resource_id}",
                "name": f"Image_{i+1}",
                "src": f"file://{image.get('file_path', f'image_{i+1}.jpg')}",
                "format": "r1"
            })
            resource_id += 1

    def _add_voiceover_track(
        self,
        spine: ET.Element,
        voiceover: Optional[Dict[str, Any]],
        frame_rate: str
    ) -> None:
        """Add voiceover to timeline (Track 1)"""
        if not voiceover:
            return

        duration = voiceover.get("duration", 0)

        audio_clip = ET.SubElement(spine, "audio", {
            "ref": "r2",  # Voiceover resource
            "offset": "0s",
            "duration": f"{duration}s",
            "name": "Narrator"
        })

    def _add_music_track(
        self,
        spine: ET.Element,
        music: Optional[Dict[str, Any]],
        frame_rate: str
    ) -> None:
        """Add background music to timeline (Track 2)"""
        if not music:
            return

        duration = music.get("duration", 0)

        audio_clip = ET.SubElement(spine, "audio", {
            "ref": "r3",  # Music resource
            "offset": "0s",
            "duration": f"{duration}s",
            "name": "Background Music",
            "volume": "0.3"  # Lower volume for background
        })

    def _add_video_track(
        self,
        spine: ET.Element,
        videos: List[Dict[str, Any]],
        frame_rate: str
    ) -> None:
        """Add B-roll videos to timeline (Track 3)"""
        if not videos:
            return

        resource_id = 4  # Start after voiceover and music

        for video in videos:
            start_time = video.get("start_time", 0)
            duration = video.get("duration", 5)

            video_clip = ET.SubElement(spine, "video", {
                "ref": f"r{resource_id}",
                "offset": f"{start_time}s",
                "duration": f"{duration}s",
                "name": video.get("title", "B-Roll")
            })
            resource_id += 1

    def _add_image_track(
        self,
        spine: ET.Element,
        images: List[Dict[str, Any]],
        frame_rate: str
    ) -> None:
        """Add still images to timeline (Track 4)"""
        if not images:
            return

        # Resource IDs start after videos
        video_count = len(images)
        resource_id = 4 + video_count

        for image in images:
            start_time = image.get("start_time", 0)
            duration = image.get("duration", 3)

            image_clip = ET.SubElement(spine, "video", {
                "ref": f"r{resource_id}",
                "offset": f"{start_time}s",
                "duration": f"{duration}s",
                "name": image.get("title", "Image")
            })
            resource_id += 1

    def _add_chapter_markers(
        self,
        spine: ET.Element,
        chapters: List[Dict[str, Any]],
        frame_rate: str
    ) -> None:
        """Add chapter markers to timeline"""
        current_time = 0.0

        for chapter in chapters:
            chapter_title = chapter.get("title", f"Chapter {chapter.get('chapter_number', '')}")

            marker = ET.SubElement(spine, "marker", {
                "start": f"{current_time}s",
                "value": chapter_title
            })

            # Estimate chapter duration (words / WPM * 60)
            narration = chapter.get("narration", "")
            word_count = len(narration.split())
            chapter_duration = (word_count / 150) * 60  # 150 WPM average

            current_time += chapter_duration

    def _calculate_total_duration(self, assets: Dict[str, Any]) -> float:
        """Calculate total timeline duration"""
        durations = []

        if assets.get("voiceover"):
            durations.append(assets["voiceover"].get("duration", 0))

        if assets.get("music"):
            durations.append(assets["music"].get("duration", 0))

        for video in assets.get("videos", []):
            end_time = video.get("start_time", 0) + video.get("duration", 0)
            durations.append(end_time)

        for image in assets.get("images", []):
            end_time = image.get("start_time", 0) + image.get("duration", 0)
            durations.append(end_time)

        return max(durations) if durations else 0

    def _count_tracks(self, assets: Dict[str, Any]) -> int:
        """Count number of tracks in timeline"""
        track_count = 0

        if assets.get("voiceover"):
            track_count += 1
        if assets.get("music"):
            track_count += 1
        if assets.get("videos"):
            track_count += 1
        if assets.get("images"):
            track_count += 1

        return track_count

    def _seconds_to_timecode(self, seconds: float, frame_rate: str) -> str:
        """Convert seconds to timecode format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        frames = int((seconds - int(seconds)) * int(frame_rate))

        return f"{hours:02d}:{minutes:02d}:{secs:02d}:{frames:02d}"

    def _prettify_xml(self, elem: ET.Element) -> str:
        """Return pretty-printed XML string"""
        rough_string = ET.tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    async def generate_edl(self, assets: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate EDL (Edit Decision List) format as alternative to FCPXML

        EDL is a simpler format supported by most editing software
        """
        try:
            edl_lines = [
                "TITLE: Documentary Timeline",
                f"FCM: NON-DROP FRAME",
                ""
            ]

            event_number = 1

            # Add voiceover
            if assets.get("voiceover"):
                voiceover = assets["voiceover"]
                duration = voiceover.get("duration", 0)
                edl_lines.append(f"{event_number:03d}  AX       AA/V  C        00:00:00:00 00:00:{int(duration):02d}:00 00:00:00:00 00:00:{int(duration):02d}:00")
                edl_lines.append(f"* FROM CLIP NAME: Voiceover")
                event_number += 1

            # Add music
            if assets.get("music"):
                music = assets["music"]
                duration = music.get("duration", 0)
                edl_lines.append(f"{event_number:03d}  AX       AA    C        00:00:00:00 00:00:{int(duration):02d}:00 00:00:00:00 00:00:{int(duration):02d}:00")
                edl_lines.append(f"* FROM CLIP NAME: Background Music")
                event_number += 1

            edl_content = "\n".join(edl_lines)

            return {
                "success": True,
                "edl_content": edl_content,
                "format": "CMX3600"
            }

        except Exception as e:
            logger.error(f"Error generating EDL: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance
xml_architect_service = XMLArchitectService()
