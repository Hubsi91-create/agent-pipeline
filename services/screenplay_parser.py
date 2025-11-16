"""
Screenplay Parser Service
=========================
Parses PDF, DOCX, and TXT screenplay files into structured scene data.

Supports:
- PDF files (via PyPDF2)
- DOCX files (via python-docx)
- TXT files (plain text)

Author: Music Video Production System
Version: 1.0.0
"""

import re
import logging
from typing import List, Dict, Any, Optional
from PyPDF2 import PdfReader
from docx import Document
import io

logger = logging.getLogger(__name__)


class ScreenplayParser:
    """
    Parses screenplay files and extracts scene information.

    Detects scene headings (INT./EXT.) and descriptions.
    """

    def __init__(self):
        """Initialize the screenplay parser"""
        self.scene_heading_pattern = re.compile(
            r'^(INT\.|EXT\.|INT/EXT\.)[\s]+(.+?)[\s]*(?:-[\s]*(.+))?$',
            re.IGNORECASE | re.MULTILINE
        )

    def parse_pdf(self, file_data: bytes) -> Dict[str, Any]:
        """
        Parse PDF screenplay file

        Args:
            file_data: PDF file content as bytes

        Returns:
            Dictionary with title, scenes, and metadata
        """
        try:
            pdf_file = io.BytesIO(file_data)
            reader = PdfReader(pdf_file)

            # Extract all text from PDF
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"

            # Parse the extracted text
            return self._parse_text(text)

        except Exception as e:
            logger.error(f"Failed to parse PDF: {str(e)}")
            raise ValueError(f"PDF parsing failed: {str(e)}")

    def parse_docx(self, file_data: bytes) -> Dict[str, Any]:
        """
        Parse DOCX screenplay file

        Args:
            file_data: DOCX file content as bytes

        Returns:
            Dictionary with title, scenes, and metadata
        """
        try:
            docx_file = io.BytesIO(file_data)
            doc = Document(docx_file)

            # Extract all text from paragraphs
            text = "\n".join([para.text for para in doc.paragraphs])

            # Parse the extracted text
            return self._parse_text(text)

        except Exception as e:
            logger.error(f"Failed to parse DOCX: {str(e)}")
            raise ValueError(f"DOCX parsing failed: {str(e)}")

    def parse_txt(self, file_data: bytes) -> Dict[str, Any]:
        """
        Parse TXT screenplay file

        Args:
            file_data: TXT file content as bytes

        Returns:
            Dictionary with title, scenes, and metadata
        """
        try:
            # Decode text (try UTF-8, fallback to latin-1)
            try:
                text = file_data.decode('utf-8')
            except UnicodeDecodeError:
                text = file_data.decode('latin-1')

            # Parse the text
            return self._parse_text(text)

        except Exception as e:
            logger.error(f"Failed to parse TXT: {str(e)}")
            raise ValueError(f"TXT parsing failed: {str(e)}")

    def _parse_text(self, text: str) -> Dict[str, Any]:
        """
        Parse screenplay text and extract scenes

        Args:
            text: Screenplay text content

        Returns:
            Dictionary with title, scenes, and metadata
        """
        lines = text.split('\n')
        scenes = []
        current_scene = None
        title = "Untitled Screenplay"

        # Try to extract title from first non-empty line
        for line in lines[:10]:
            line = line.strip()
            if line and not line.upper().startswith(('INT.', 'EXT.', 'INT/EXT.')):
                title = line
                break

        # Parse scenes
        scene_number = 1
        for i, line in enumerate(lines):
            line = line.strip()

            # Check if this is a scene heading
            match = self.scene_heading_pattern.match(line)
            if match:
                # Save previous scene if exists
                if current_scene:
                    scenes.append(current_scene)

                # Start new scene
                location_type = match.group(1)
                location = match.group(2) if match.group(2) else ""
                time = match.group(3) if match.group(3) else ""

                heading = f"{location_type} {location}"
                if time:
                    heading += f" - {time}"

                current_scene = {
                    'sceneNumber': scene_number,
                    'heading': heading.strip(),
                    'description': ''
                }
                scene_number += 1

            elif current_scene and line:
                # Add description to current scene
                # Skip action lines that are character names (all caps)
                if not line.isupper() or len(line) < 3:
                    if current_scene['description']:
                        current_scene['description'] += ' '
                    current_scene['description'] += line

        # Save last scene
        if current_scene:
            scenes.append(current_scene)

        # If no scenes detected, create a default scene
        if not scenes:
            scenes = [{
                'sceneNumber': 1,
                'heading': 'Scene 1',
                'description': text[:500] if len(text) > 500 else text
            }]

        return {
            'title': title,
            'scenes': scenes,
            'metadata': {
                'sceneCount': len(scenes),
                'parsedSuccessfully': True
            }
        }


# Singleton instance
_parser_instance = None


def get_screenplay_parser() -> ScreenplayParser:
    """Get singleton screenplay parser instance"""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = ScreenplayParser()
    return _parser_instance
