"""
Storyboard Export Service
=========================
Exports storyboards to PDF format with scenes and images.

Supports:
- PDF export with customizable layouts
- 1 scene per page or 6 scenes per page
- Embedded images and text

Author: Music Video Production System
Version: 1.0.0
"""

import logging
import base64
import io
from typing import List, Dict, Any, Optional
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from PIL import Image as PILImage

logger = logging.getLogger(__name__)


class StoryboardExportService:
    """
    Service for exporting storyboards to various formats.
    """

    def __init__(self):
        """Initialize the export service"""
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()

    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='SceneHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#8b5cf6'),
            spaceAfter=6,
            spaceBefore=12
        ))

        self.styles.add(ParagraphStyle(
            name='SceneDescription',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            spaceAfter=12
        ))

        self.styles.add(ParagraphStyle(
            name='Title',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#0f1419'),
            alignment=TA_CENTER,
            spaceAfter=30
        ))

    def export_to_pdf(
        self,
        screenplay_title: str,
        scenes: List[Dict[str, Any]],
        layout: str = '6-scenes',
        output_path: Optional[str] = None
    ) -> bytes:
        """
        Export storyboard to PDF

        Args:
            screenplay_title: Title of the screenplay
            scenes: List of scene dictionaries with heading, description, and optional image
            layout: Layout type ('1-scene' or '6-scenes')
            output_path: Optional file path to save PDF

        Returns:
            PDF file content as bytes
        """
        try:
            # Create PDF buffer
            buffer = io.BytesIO()

            # Create document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )

            # Build content
            story = []

            # Add title page
            story.append(Paragraph(screenplay_title, self.styles['Title']))
            story.append(Spacer(1, 0.5 * inch))
            story.append(Paragraph(
                f"Storyboard - {len(scenes)} Scenes",
                self.styles['Heading3']
            ))
            story.append(Spacer(1, 0.3 * inch))
            story.append(Paragraph(
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                self.styles['Normal']
            ))
            story.append(PageBreak())

            # Add scenes based on layout
            if layout == '1-scene':
                story.extend(self._create_one_per_page_layout(scenes))
            else:  # 6-scenes
                story.extend(self._create_grid_layout(scenes))

            # Build PDF
            doc.build(story)

            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()

            # Optionally save to file
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(pdf_bytes)
                logger.info(f"PDF saved to {output_path}")

            logger.info(f"PDF generated successfully ({len(pdf_bytes)} bytes)")
            return pdf_bytes

        except Exception as e:
            logger.error(f"PDF export failed: {str(e)}")
            raise ValueError(f"PDF export failed: {str(e)}")

    def _create_one_per_page_layout(self, scenes: List[Dict[str, Any]]) -> list:
        """
        Create layout with one scene per page

        Args:
            scenes: List of scene dictionaries

        Returns:
            List of PDF elements
        """
        elements = []

        for i, scene in enumerate(scenes):
            # Scene heading
            heading = scene.get('heading', f"Scene {scene.get('sceneNumber', i+1)}")
            elements.append(Paragraph(heading, self.styles['SceneHeading']))

            # Scene image (if available)
            if 'imageData' in scene and scene['imageData']:
                try:
                    image = self._create_image_from_base64(
                        scene['imageData'],
                        max_width=5 * inch,
                        max_height=3 * inch
                    )
                    if image:
                        elements.append(image)
                        elements.append(Spacer(1, 0.2 * inch))
                except Exception as e:
                    logger.warning(f"Failed to add image for scene {i+1}: {str(e)}")

            # Scene description
            description = scene.get('description', '')
            if description:
                elements.append(Paragraph(description, self.styles['SceneDescription']))

            # Prompt (if available)
            prompt = scene.get('prompt', '')
            if prompt:
                elements.append(Spacer(1, 0.1 * inch))
                elements.append(Paragraph(
                    f"<i>Prompt: {prompt}</i>",
                    self.styles['Normal']
                ))

            # Page break after each scene (except last)
            if i < len(scenes) - 1:
                elements.append(PageBreak())

        return elements

    def _create_grid_layout(self, scenes: List[Dict[str, Any]]) -> list:
        """
        Create layout with 6 scenes per page (2x3 grid)

        Args:
            scenes: List of scene dictionaries

        Returns:
            List of PDF elements
        """
        elements = []
        scenes_per_page = 6

        for page_start in range(0, len(scenes), scenes_per_page):
            page_scenes = scenes[page_start:page_start + scenes_per_page]

            # Create table data
            table_data = []
            row = []

            for i, scene in enumerate(page_scenes):
                cell_content = self._create_scene_cell(scene)
                row.append(cell_content)

                # Start new row after 2 cells
                if len(row) == 2:
                    table_data.append(row)
                    row = []

            # Add remaining cells if any
            if row:
                # Fill remaining cells with empty content
                while len(row) < 2:
                    row.append("")
                table_data.append(row)

            # Create table
            if table_data:
                table = Table(table_data, colWidths=[3.5 * inch, 3.5 * inch])
                table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('PADDING', (0, 0), (-1, -1), 12),
                ]))
                elements.append(table)

            # Page break after each page (except last)
            if page_start + scenes_per_page < len(scenes):
                elements.append(PageBreak())

        return elements

    def _create_scene_cell(self, scene: Dict[str, Any]) -> Paragraph:
        """
        Create content for a single scene cell in grid layout

        Args:
            scene: Scene dictionary

        Returns:
            Paragraph element with scene content
        """
        heading = scene.get('heading', f"Scene {scene.get('sceneNumber', 1)}")
        description = scene.get('description', '')

        # Truncate description if too long
        if len(description) > 150:
            description = description[:150] + "..."

        content = f"<b>{heading}</b><br/><br/>{description}"

        return Paragraph(content, ParagraphStyle(
            'CellStyle',
            parent=self.styles['Normal'],
            fontSize=8,
            leading=10
        ))

    def _create_image_from_base64(
        self,
        base64_data: str,
        max_width: float,
        max_height: float
    ) -> Optional[Image]:
        """
        Create ReportLab Image from base64 data

        Args:
            base64_data: Base64-encoded image data
            max_width: Maximum width in points
            max_height: Maximum height in points

        Returns:
            ReportLab Image object or None if failed
        """
        try:
            # Remove data URL prefix if present
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]

            # Decode base64
            image_data = base64.b64decode(base64_data)

            # Create PIL Image
            pil_image = PILImage.open(io.BytesIO(image_data))

            # Calculate dimensions maintaining aspect ratio
            aspect = pil_image.width / pil_image.height
            if aspect > max_width / max_height:
                width = max_width
                height = max_width / aspect
            else:
                height = max_height
                width = max_height * aspect

            # Create ReportLab Image
            img_buffer = io.BytesIO(image_data)
            return Image(img_buffer, width=width, height=height)

        except Exception as e:
            logger.warning(f"Failed to create image: {str(e)}")
            return None


# Singleton instance
_export_service_instance = None


def get_export_service() -> StoryboardExportService:
    """Get singleton export service instance"""
    global _export_service_instance
    if _export_service_instance is None:
        _export_service_instance = StoryboardExportService()
    return _export_service_instance
