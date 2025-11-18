"""
Agent 3: Audio Analyzer with Smart Scene Splitting
Analyzes audio files for structure, energy, and automatically splits into 8s chunks
"""

from typing import Optional, List, Dict, Any
from pydub import AudioSegment
from pydub.utils import make_chunks
import numpy as np
from app.models.data_models import AudioAnalysis
from app.infrastructure.database.google_sheet_service import google_sheet_service, SHEET_A3_AUDIO_ANALYSIS
from app.utils.logger import setup_logger
import io

logger = setup_logger("Agent3_AudioAnalyzer")


class Agent3AudioAnalyzer:
    """Singleton service for audio analysis with smart scene splitting"""

    _instance: Optional['Agent3AudioAnalyzer'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def analyze_audio_file(
        self,
        audio_file_bytes: bytes,
        filename: str,
        project_id: Optional[str] = None,
        max_scene_duration: float = 8.0
    ) -> Dict[str, Any]:
        """
        Analyze audio file and create smart scene breakdown

        Args:
            audio_file_bytes: Audio file content (WAV/MP3)
            filename: Original filename
            project_id: Optional project ID
            max_scene_duration: Maximum duration per scene (default: 8.0s for Veo/Runway)

        Returns:
            Dict with scenes, energy_profile, bpm, duration, etc.
        """
        logger.info(f"Analyzing audio: {filename}")

        try:
            # Load audio file
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_file_bytes))

            # Convert to mono for analysis
            if audio_segment.channels > 1:
                audio_segment = audio_segment.set_channels(1)

            # Get basic properties
            duration = len(audio_segment) / 1000.0  # Convert ms to seconds
            sample_rate = audio_segment.frame_rate

            logger.info(f"Audio loaded: {duration:.2f}s @ {sample_rate}Hz")

            # Analyze energy over time
            energy_profile = self._analyze_energy(audio_segment)

            # Detect sections (Intro, Verse, Chorus) based on energy changes
            sections = self._detect_sections(energy_profile, duration)

            # Smart split sections into 8s chunks (Veo/Runway limit)
            scenes = self._smart_split(sections, max_scene_duration)

            # Estimate BPM (simple peak detection)
            bpm = self._estimate_bpm(audio_segment)

            result = {
                "filename": filename,
                "duration": duration,
                "bpm": bpm,
                "scenes": scenes,
                "energy_profile": energy_profile,
                "total_scenes": len(scenes),
                "project_id": project_id
            }

            logger.info(f"✅ Analysis complete: {len(scenes)} scenes created")
            return result

        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            raise

    def _analyze_energy(self, audio_segment: AudioSegment, chunk_size_ms: int = 500) -> List[Dict[str, float]]:
        """
        Analyze RMS energy over time

        Args:
            audio_segment: Audio to analyze
            chunk_size_ms: Size of analysis windows (default: 500ms)

        Returns:
            List of {time, energy} dictionaries
        """
        chunks = make_chunks(audio_segment, chunk_size_ms)
        energy_profile = []

        for i, chunk in enumerate(chunks):
            time = (i * chunk_size_ms) / 1000.0  # Convert to seconds

            # Calculate RMS energy
            samples = np.array(chunk.get_array_of_samples())
            rms = np.sqrt(np.mean(samples**2))

            # Normalize to 0-1 range (approximate)
            normalized_energy = min(1.0, rms / 5000.0)

            energy_profile.append({
                "time": time,
                "energy": normalized_energy
            })

        return energy_profile

    def _detect_sections(self, energy_profile: List[Dict[str, float]], total_duration: float) -> List[Dict[str, Any]]:
        """
        Detect song sections (Intro, Verse, Chorus) based on energy changes

        Args:
            energy_profile: Energy over time
            total_duration: Total audio duration

        Returns:
            List of section dictionaries
        """
        sections = []

        if not energy_profile:
            return sections

        # Simple heuristic: Detect energy level changes
        # Low energy -> Intro/Verse
        # High energy -> Chorus
        # Very low -> Outro

        energies = [e["energy"] for e in energy_profile]
        avg_energy = np.mean(energies)
        high_threshold = avg_energy * 1.2
        low_threshold = avg_energy * 0.8

        current_section = None
        section_start = 0.0

        for i, point in enumerate(energy_profile):
            time = point["time"]
            energy = point["energy"]

            # Determine section type
            if energy > high_threshold:
                section_type = "Chorus"
            elif energy < low_threshold:
                section_type = "Verse" if time < total_duration * 0.9 else "Outro"
            else:
                section_type = "Intro" if time < total_duration * 0.15 else "Verse"

            # Detect section changes
            if current_section != section_type:
                # Save previous section
                if current_section is not None:
                    sections.append({
                        "type": current_section,
                        "start": section_start,
                        "end": time,
                        "avg_energy": np.mean([e["energy"] for e in energy_profile
                                              if section_start <= e["time"] < time])
                    })

                # Start new section
                current_section = section_type
                section_start = time

        # Add final section
        if current_section is not None:
            sections.append({
                "type": current_section,
                "start": section_start,
                "end": total_duration,
                "avg_energy": np.mean([e["energy"] for e in energy_profile
                                      if section_start <= e["time"]])
            })

        logger.info(f"Detected {len(sections)} sections")
        return sections

    def _smart_split(self, sections: List[Dict[str, Any]], max_duration: float = 8.0) -> List[Dict[str, Any]]:
        """
        Smart split sections into scenes (max 8s each for Veo/Runway)

        Args:
            sections: Detected song sections
            max_duration: Maximum scene duration (default: 8.0s)

        Returns:
            List of scene dictionaries with id, start, end, energy, type
        """
        scenes = []
        scene_id = 1

        for section in sections:
            section_duration = section["end"] - section["start"]

            if section_duration <= max_duration:
                # Section fits in one scene
                scenes.append({
                    "id": scene_id,
                    "start": round(section["start"], 2),
                    "end": round(section["end"], 2),
                    "duration": round(section_duration, 2),
                    "energy": self._classify_energy(section["avg_energy"]),
                    "type": section["type"]
                })
                scene_id += 1
            else:
                # Split into multiple scenes
                num_chunks = int(np.ceil(section_duration / max_duration))
                chunk_duration = section_duration / num_chunks

                for i in range(num_chunks):
                    chunk_start = section["start"] + (i * chunk_duration)
                    chunk_end = min(chunk_start + chunk_duration, section["end"])

                    scenes.append({
                        "id": scene_id,
                        "start": round(chunk_start, 2),
                        "end": round(chunk_end, 2),
                        "duration": round(chunk_end - chunk_start, 2),
                        "energy": self._classify_energy(section["avg_energy"]),
                        "type": f"{section['type']} (Part {i+1}/{num_chunks})"
                    })
                    scene_id += 1

        logger.info(f"Created {len(scenes)} scenes (max {max_duration}s each)")
        return scenes

    def _classify_energy(self, energy: float) -> str:
        """Classify energy level as Low/Medium/High"""
        if energy < 0.4:
            return "Low"
        elif energy < 0.7:
            return "Medium"
        else:
            return "High"

    def _estimate_bpm(self, audio_segment: AudioSegment) -> int:
        """
        Estimate BPM using simple peak detection

        Args:
            audio_segment: Audio to analyze

        Returns:
            Estimated BPM (default: 120 if detection fails)
        """
        try:
            # Simple implementation - analyze first 30 seconds
            sample_segment = audio_segment[:30000]  # First 30s
            samples = np.array(sample_segment.get_array_of_samples())

            # Find peaks in energy
            from scipy.signal import find_peaks

            # Low-pass filter to focus on beat range
            peaks, _ = find_peaks(np.abs(samples), distance=int(sample_segment.frame_rate * 0.3))

            if len(peaks) > 10:
                # Calculate average time between peaks
                peak_times = peaks / sample_segment.frame_rate
                intervals = np.diff(peak_times)
                avg_interval = np.median(intervals)

                # Convert to BPM
                bpm = int(60 / avg_interval) if avg_interval > 0 else 120
                bpm = min(180, max(60, bpm))  # Clamp to reasonable range

                logger.info(f"Estimated BPM: {bpm}")
                return bpm

        except Exception as e:
            logger.warning(f"BPM estimation failed: {e}")

        return 120  # Default fallback

    async def analyze_audio(self, project_id: str, filename: str) -> AudioAnalysis:
        """
        Legacy method for backward compatibility

        Note: This method is deprecated. Use analyze_audio_file() instead.
        """
        logger.warning("Using deprecated analyze_audio method")

        # Simulate analysis for backward compatibility
        analysis = AudioAnalysis(
            project_id=project_id,
            filename=filename,
            duration=180.0,
            bpm=120,
            key="C minor",
            structure=["Intro", "Verse 1", "Chorus", "Verse 2", "Chorus", "Bridge", "Chorus", "Outro"],
            peak_moments=[15.0, 45.0, 90.0, 135.0, 165.0],
            energy_profile=[
                {"time": 0.0, "energy": 0.3},
                {"time": 15.0, "energy": 0.7},
                {"time": 45.0, "energy": 0.9},
                {"time": 90.0, "energy": 0.6},
                {"time": 135.0, "energy": 0.95},
                {"time": 180.0, "energy": 0.2}
            ]
        )

        await self._save_to_sheets(analysis)
        return analysis

    async def get_analysis(self, project_id: str) -> Optional[AudioAnalysis]:
        """Get audio analysis for a project"""
        record = await google_sheet_service.find_record(
            SHEET_A3_AUDIO_ANALYSIS,
            "project_id",
            project_id
        )

        if record:
            return AudioAnalysis(**record)
        return None

    async def _save_to_sheets(self, analysis: AudioAnalysis) -> bool:
        """Save audio analysis to Google Sheets"""
        data = [
            analysis.id,
            analysis.project_id,
            analysis.filename,
            analysis.duration,
            analysis.bpm,
            analysis.key,
            ", ".join(analysis.structure),
            ", ".join(map(str, analysis.peak_moments)),
            analysis.analyzed_at.isoformat()
        ]

        return await google_sheet_service.append_row(SHEET_A3_AUDIO_ANALYSIS, data)


# Singleton instance
agent3_service = Agent3AudioAnalyzer()
