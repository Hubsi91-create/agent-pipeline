"""
Screenplay Routes - API Endpoints for Screenplay Storyboard Workflow
====================================================================
Handles all screenplay-related API endpoints.

Endpoints:
- Screenplay Upload & Parsing (PDF/DOCX/TXT)
- Scene Management (list, update, delete)
- Visual References (upload, list, delete)
- Image Generation (Vertex AI/Imagen)
- Export (PDF, video)
- API Key Validation

Author: Music Video Production System
Version: 1.0.0
"""

from flask import Blueprint, request, jsonify
import logging
import uuid
import json
import io
from datetime import datetime
from typing import Dict, Any

# Import services
from services.screenplay_parser import get_screenplay_parser
from services.image_generation_service import get_image_generation_service
from services.storyboard_export_service import get_export_service
from services.gemini_service import generate_song_lyrics
from database import get_db

logger = logging.getLogger(__name__)

# Create Blueprint
screenplay_bp = Blueprint('screenplay', __name__)

# Get service instances
db = get_db()


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def get_user_id() -> str:
    """
    Get user ID from request (placeholder - implement auth)

    Returns:
        User ID string
    """
    # In production, get from JWT token or session
    return request.headers.get('X-User-ID', 'default_user')


def create_error_response(
    error_code: str,
    message: str,
    details: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Create standardized error response"""
    response = {
        'error': error_code,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    if details:
        response['details'] = details
    return response


# ============================================================
# SCREENPLAY UPLOAD & PARSING ENDPOINTS
# ============================================================

@screenplay_bp.route('/parse', methods=['POST'])
def parse_screenplay():
    """
    Parse uploaded screenplay file (PDF, DOCX, or TXT)

    Request:
        - file: Uploaded file (multipart/form-data)

    Returns:
        - screenplay_id: Unique ID for the screenplay
        - title: Extracted title
        - scenes: List of parsed scenes
        - metadata: Parsing metadata
    """
    try:
        user_id = get_user_id()

        # Check if file is present
        if 'file' not in request.files:
            return jsonify(create_error_response(
                'missing_file',
                'No file uploaded'
            )), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify(create_error_response(
                'empty_filename',
                'No file selected'
            )), 400

        # Get file extension
        filename = file.filename
        file_ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

        # Read file data
        file_data = file.read()

        # Parse based on file type
        parser = get_screenplay_parser()

        if file_ext == 'pdf':
            parsed_data = parser.parse_pdf(file_data)
        elif file_ext == 'docx':
            parsed_data = parser.parse_docx(file_data)
        elif file_ext in ['txt', 'text']:
            parsed_data = parser.parse_txt(file_data)
        else:
            return jsonify(create_error_response(
                'unsupported_format',
                f'File format .{file_ext} is not supported'
            )), 400

        # Generate IDs
        screenplay_id = f"screenplay_{uuid.uuid4().hex[:12]}"

        # Save screenplay to database
        with db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO screenplays (
                    id, user_id, title, filename, file_type,
                    scene_count, status, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                screenplay_id,
                user_id,
                parsed_data['title'],
                filename,
                file_ext,
                len(parsed_data['scenes']),
                'parsed',
                json.dumps(parsed_data['metadata'])
            ))

            # Save scenes
            for scene in parsed_data['scenes']:
                scene_id = f"scene_{uuid.uuid4().hex[:12]}"

                cursor.execute("""
                    INSERT INTO screenplay_scenes (
                        id, screenplay_id, scene_number, heading, description
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    scene_id,
                    screenplay_id,
                    scene['sceneNumber'],
                    scene['heading'],
                    scene['description']
                ))

        logger.info(f"Screenplay parsed: {screenplay_id} ({len(parsed_data['scenes'])} scenes)")

        return jsonify({
            'screenplay_id': screenplay_id,
            'title': parsed_data['title'],
            'scenes': parsed_data['scenes'],
            'metadata': {
                **parsed_data['metadata'],
                'filename': filename,
                'uploadDate': datetime.now().isoformat()
            }
        }), 200

    except ValueError as e:
        logger.error(f"Parsing error: {str(e)}")
        return jsonify(create_error_response(
            'parsing_failed',
            str(e)
        )), 400

    except Exception as e:
        logger.error(f"Screenplay parsing failed: {str(e)}")
        return jsonify(create_error_response(
            'internal_error',
            'Failed to parse screenplay'
        )), 500


# ============================================================
# SCENE MANAGEMENT ENDPOINTS
# ============================================================

@screenplay_bp.route('/scenes/<screenplay_id>', methods=['GET'])
def get_scenes(screenplay_id: str):
    """
    Get all scenes for a screenplay

    Args:
        screenplay_id: Screenplay ID

    Returns:
        List of scenes with metadata
    """
    try:
        user_id = get_user_id()

        with db.get_connection() as conn:
            cursor = conn.cursor()

            # Get screenplay
            cursor.execute("""
                SELECT * FROM screenplays
                WHERE id = ? AND user_id = ?
            """, (screenplay_id, user_id))

            screenplay = cursor.fetchone()

            if not screenplay:
                return jsonify(create_error_response(
                    'not_found',
                    'Screenplay not found'
                )), 404

            # Get scenes
            cursor.execute("""
                SELECT * FROM screenplay_scenes
                WHERE screenplay_id = ?
                ORDER BY scene_number ASC
            """, (screenplay_id,))

            scenes = [dict(row) for row in cursor.fetchall()]

        return jsonify({
            'screenplay_id': screenplay_id,
            'scenes': scenes
        }), 200

    except Exception as e:
        logger.error(f"Failed to get scenes: {str(e)}")
        return jsonify(create_error_response(
            'internal_error',
            'Failed to retrieve scenes'
        )), 500


@screenplay_bp.route('/scenes/<scene_id>', methods=['PATCH'])
def update_scene(scene_id: str):
    """
    Update a scene's prompt or settings

    Args:
        scene_id: Scene ID

    Request Body:
        - prompt: Updated prompt (optional)
        - settings: Updated settings (optional)

    Returns:
        Updated scene data
    """
    try:
        user_id = get_user_id()
        data = request.get_json()

        with db.get_connection() as conn:
            cursor = conn.cursor()

            # Build update query
            updates = []
            values = []

            if 'prompt' in data:
                updates.append('prompt = ?')
                values.append(data['prompt'])

            if 'settings' in data:
                updates.append('settings = ?')
                values.append(json.dumps(data['settings']))

            if not updates:
                return jsonify(create_error_response(
                    'no_updates',
                    'No valid fields to update'
                )), 400

            updates.append('updated_at = CURRENT_TIMESTAMP')
            values.append(scene_id)

            query = f"""
                UPDATE screenplay_scenes
                SET {', '.join(updates)}
                WHERE id = ?
            """

            cursor.execute(query, values)

            if cursor.rowcount == 0:
                return jsonify(create_error_response(
                    'not_found',
                    'Scene not found'
                )), 404

            # Get updated scene
            cursor.execute("""
                SELECT * FROM screenplay_scenes WHERE id = ?
            """, (scene_id,))

            scene = dict(cursor.fetchone())

        logger.info(f"Scene updated: {scene_id}")

        return jsonify({
            'scene': scene,
            'message': 'Scene updated successfully'
        }), 200

    except Exception as e:
        logger.error(f"Failed to update scene: {str(e)}")
        return jsonify(create_error_response(
            'internal_error',
            'Failed to update scene'
        )), 500


# ============================================================
# VISUAL REFERENCES ENDPOINTS
# ============================================================

@screenplay_bp.route('/references', methods=['POST'])
def upload_reference():
    """
    Upload a visual reference image

    Request Body (JSON):
        - name: Reference name
        - category: Category (character/location/style)
        - base64_data: Base64-encoded image data
        - tags: Comma-separated tags
        - screenplay_id: Optional screenplay ID

    Returns:
        Reference ID and metadata
    """
    try:
        user_id = get_user_id()
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'category', 'base64_data']
        for field in required_fields:
            if field not in data:
                return jsonify(create_error_response(
                    'missing_field',
                    f'Missing required field: {field}'
                )), 400

        # Generate reference ID
        reference_id = f"ref_{uuid.uuid4().hex[:12]}"

        # Save to database
        with db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO visual_references (
                    id, user_id, screenplay_id, name, category, base64_data, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                reference_id,
                user_id,
                data.get('screenplay_id'),
                data['name'],
                data['category'],
                data['base64_data'],
                data.get('tags', '')
            ))

        logger.info(f"Reference uploaded: {reference_id}")

        return jsonify({
            'reference_id': reference_id,
            'name': data['name'],
            'category': data['category'],
            'message': 'Reference uploaded successfully'
        }), 201

    except Exception as e:
        logger.error(f"Failed to upload reference: {str(e)}")
        return jsonify(create_error_response(
            'internal_error',
            'Failed to upload reference'
        )), 500


@screenplay_bp.route('/references', methods=['GET'])
def list_references():
    """
    List all visual references for the user

    Query Params:
        - screenplay_id: Filter by screenplay (optional)
        - category: Filter by category (optional)

    Returns:
        List of references
    """
    try:
        user_id = get_user_id()
        screenplay_id = request.args.get('screenplay_id')
        category = request.args.get('category')

        with db.get_connection() as conn:
            cursor = conn.cursor()

            # Build query
            query = "SELECT * FROM visual_references WHERE user_id = ?"
            params = [user_id]

            if screenplay_id:
                query += " AND screenplay_id = ?"
                params.append(screenplay_id)

            if category:
                query += " AND category = ?"
                params.append(category)

            query += " ORDER BY created_at DESC"

            cursor.execute(query, params)
            references = [dict(row) for row in cursor.fetchall()]

        return jsonify({
            'references': references,
            'count': len(references)
        }), 200

    except Exception as e:
        logger.error(f"Failed to list references: {str(e)}")
        return jsonify(create_error_response(
            'internal_error',
            'Failed to list references'
        )), 500


@screenplay_bp.route('/references/<reference_id>', methods=['DELETE'])
def delete_reference(reference_id: str):
    """
    Delete a visual reference

    Args:
        reference_id: Reference ID

    Returns:
        Success message
    """
    try:
        user_id = get_user_id()

        with db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM visual_references
                WHERE id = ? AND user_id = ?
            """, (reference_id, user_id))

            if cursor.rowcount == 0:
                return jsonify(create_error_response(
                    'not_found',
                    'Reference not found'
                )), 404

        logger.info(f"Reference deleted: {reference_id}")

        return jsonify({
            'message': 'Reference deleted successfully'
        }), 200

    except Exception as e:
        logger.error(f"Failed to delete reference: {str(e)}")
        return jsonify(create_error_response(
            'internal_error',
            'Failed to delete reference'
        )), 500


# ============================================================
# IMAGE GENERATION ENDPOINTS
# ============================================================

@screenplay_bp.route('/generate-image', methods=['POST'])
def generate_image():
    """
    Generate an image for a scene

    Request Body:
        - scene_id: Scene ID
        - prompt: Text prompt for image generation
        - model: AI model (imagen-4, dall-e-3, etc.)
        - format: Aspect ratio (16:9, 1:1, 9:16)
        - quality: Quality level (standard, hd)

    Returns:
        Generated image data and metadata
    """
    try:
        user_id = get_user_id()
        data = request.get_json()

        # Validate required fields
        if 'scene_id' not in data or 'prompt' not in data:
            return jsonify(create_error_response(
                'missing_field',
                'Missing required fields: scene_id, prompt'
            )), 400

        scene_id = data['scene_id']
        prompt = data['prompt']
        model = data.get('model', 'imagen-4')
        format = data.get('format', '16:9')
        quality = data.get('quality', 'standard')

        # Generate image
        image_service = get_image_generation_service()
        result = image_service.generate_image(prompt, model, format, quality)

        if result.get('status') == 'error':
            return jsonify(create_error_response(
                'generation_failed',
                result.get('error_message', 'Image generation failed')
            )), 500

        # Save to database
        image_id = f"img_{uuid.uuid4().hex[:12]}"

        with db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO generated_images (
                    id, scene_id, user_id, model, prompt, base64_data,
                    format, quality, status, generation_time_ms, cost
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                image_id,
                scene_id,
                user_id,
                model,
                prompt,
                result.get('base64_data'),
                format,
                quality,
                'completed',
                result.get('generation_time_ms'),
                result.get('cost')
            ))

            # Update scene with generated image
            cursor.execute("""
                UPDATE screenplay_scenes
                SET generated_image_id = ?
                WHERE id = ?
            """, (image_id, scene_id))

        logger.info(f"Image generated: {image_id} for scene {scene_id}")

        return jsonify({
            'image_id': image_id,
            'base64_data': result.get('base64_data'),
            'model': model,
            'generation_time_ms': result.get('generation_time_ms'),
            'cost': result.get('cost')
        }), 200

    except Exception as e:
        logger.error(f"Image generation failed: {str(e)}")
        return jsonify(create_error_response(
            'internal_error',
            'Failed to generate image'
        )), 500


@screenplay_bp.route('/generate-batch', methods=['POST'])
def generate_batch():
    """
    Generate images for multiple scenes in batch

    Request Body:
        - scenes: List of {scene_id, prompt} objects
        - model: AI model
        - format: Aspect ratio
        - quality: Quality level

    Returns:
        List of generation results
    """
    try:
        user_id = get_user_id()
        data = request.get_json()

        if 'scenes' not in data or not isinstance(data['scenes'], list):
            return jsonify(create_error_response(
                'invalid_request',
                'scenes must be a list'
            )), 400

        model = data.get('model', 'imagen-4')
        format = data.get('format', '16:9')
        quality = data.get('quality', 'standard')

        results = []
        image_service = get_image_generation_service()

        with db.get_connection() as conn:
            cursor = conn.cursor()

            for scene_data in data['scenes']:
                scene_id = scene_data.get('scene_id')
                prompt = scene_data.get('prompt')

                if not scene_id or not prompt:
                    continue

                # Generate image
                result = image_service.generate_image(prompt, model, format, quality)

                if result.get('status') == 'success':
                    image_id = f"img_{uuid.uuid4().hex[:12]}"

                    cursor.execute("""
                        INSERT INTO generated_images (
                            id, scene_id, user_id, model, prompt, base64_data,
                            format, quality, status, generation_time_ms, cost
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        image_id,
                        scene_id,
                        user_id,
                        model,
                        prompt,
                        result.get('base64_data'),
                        format,
                        quality,
                        'completed',
                        result.get('generation_time_ms'),
                        result.get('cost')
                    ))

                    cursor.execute("""
                        UPDATE screenplay_scenes
                        SET generated_image_id = ?
                        WHERE id = ?
                    """, (image_id, scene_id))

                    results.append({
                        'scene_id': scene_id,
                        'image_id': image_id,
                        'status': 'success'
                    })
                else:
                    results.append({
                        'scene_id': scene_id,
                        'status': 'error',
                        'error': result.get('error_message')
                    })

        logger.info(f"Batch generation completed: {len(results)} scenes")

        return jsonify({
            'results': results,
            'total': len(results),
            'successful': len([r for r in results if r['status'] == 'success'])
        }), 200

    except Exception as e:
        logger.error(f"Batch generation failed: {str(e)}")
        return jsonify(create_error_response(
            'internal_error',
            'Failed to generate batch'
        )), 500


# ============================================================
# EXPORT ENDPOINTS
# ============================================================

@screenplay_bp.route('/export/pdf', methods=['POST'])
def export_pdf():
    """
    Export storyboard to PDF

    Request Body:
        - screenplay_id: Screenplay ID
        - layout: Layout type (1-scene or 6-scenes)

    Returns:
        PDF file (binary)
    """
    try:
        user_id = get_user_id()
        data = request.get_json()

        if 'screenplay_id' not in data:
            return jsonify(create_error_response(
                'missing_field',
                'screenplay_id is required'
            )), 400

        screenplay_id = data['screenplay_id']
        layout = data.get('layout', '6-scenes')

        # Get screenplay and scenes from database
        with db.get_connection() as conn:
            cursor = conn.cursor()

            # Get screenplay
            cursor.execute("""
                SELECT * FROM screenplays
                WHERE id = ? AND user_id = ?
            """, (screenplay_id, user_id))

            screenplay = cursor.fetchone()

            if not screenplay:
                return jsonify(create_error_response(
                    'not_found',
                    'Screenplay not found'
                )), 404

            screenplay_title = screenplay['title']

            # Get scenes with images
            cursor.execute("""
                SELECT
                    s.*,
                    g.base64_data as imageData
                FROM screenplay_scenes s
                LEFT JOIN generated_images g ON s.generated_image_id = g.id
                WHERE s.screenplay_id = ?
                ORDER BY s.scene_number ASC
            """, (screenplay_id,))

            scenes = [dict(row) for row in cursor.fetchall()]

        # Generate PDF
        export_service = get_export_service()
        pdf_bytes = export_service.export_to_pdf(
            screenplay_title,
            scenes,
            layout
        )

        # Save export record
        export_id = f"export_{uuid.uuid4().hex[:12]}"

        with db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO storyboard_exports (
                    id, screenplay_id, user_id, export_type, layout, status, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                export_id,
                screenplay_id,
                user_id,
                'pdf',
                layout,
                'completed',
                datetime.now().isoformat()
            ))

        logger.info(f"PDF exported: {export_id} ({len(pdf_bytes)} bytes)")

        # Return PDF as binary response
        from flask import send_file
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"{screenplay_title}_storyboard.pdf"
        )

    except Exception as e:
        logger.error(f"PDF export failed: {str(e)}")
        return jsonify(create_error_response(
            'internal_error',
            'Failed to export PDF'
        )), 500


# ============================================================
# API KEY VALIDATION ENDPOINT
# ============================================================

@screenplay_bp.route('/validate-api-key', methods=['POST'])
def validate_api_key():
    """
    Validate an API key

    Request Body:
        - service: Service name (google_cloud, vertex_ai, runway)
        - api_key: API key to validate

    Returns:
        Validation result
    """
    try:
        data = request.get_json()

        if 'service' not in data or 'api_key' not in data:
            return jsonify(create_error_response(
                'missing_field',
                'service and api_key are required'
            )), 400

        service = data['service']
        api_key = data['api_key']

        # Validate based on service
        if service in ['google_cloud', 'vertex_ai']:
            image_service = get_image_generation_service(api_key)
            result = image_service.validate_api_key(api_key)
        else:
            result = {
                'valid': False,
                'message': f'Service {service} validation not implemented'
            }

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"API key validation failed: {str(e)}")
        return jsonify(create_error_response(
            'internal_error',
            'Failed to validate API key'
        )), 500


# ============================================================
# NEW WORKFLOW ENDPOINTS - JUST-IN-TIME WORKFLOW
# ============================================================

def calculate_lyrics_length(bpm: int, target_duration_minutes: float, genre: str) -> tuple:
    """
    Berechnet erforderliche Lyrics-Länge basierend auf BPM und Dauer.

    Args:
        bpm: Beats per minute
        target_duration_minutes: Zieldauer in Minuten (als float)
        genre: Musikgenre (für genre-spezifische Anpassungen)

    Returns:
        Tuple (total_words, wpm) - Gesamtanzahl Wörter und Words per Minute
    """
    wpm = 150  # Standard-WpM (Mittel)

    # BPM-basierte WPM-Anpassung
    if bpm <= 90:
        wpm = 130  # Langsam (70-90 BPM)
    elif bpm <= 115:
        wpm = 150  # Mittel (95-115 BPM)
    else:
        wpm = 170  # Schnell (120-150 BPM)

    # Genre-spezifische Ausnahmen
    genre_lower = genre.lower()

    if "reggaeton" in genre_lower or "hip-hop" in genre_lower or "trap" in genre_lower:
        wpm = 160
    elif "house" in genre_lower:
        wpm = 170
    elif "jazz" in genre_lower:
        wpm = 130
    elif "techno" in genre_lower:
        return 20, wpm  # Techno hat fast keine Lyrics

    total_words = int(wpm * target_duration_minutes)
    return total_words, wpm


@screenplay_bp.route('/suno-prompt', methods=['POST'])
def generate_suno_prompt():
    """
    Generate Suno music prompt with BPM-based lyric generation

    Request Body:
        - theme: Text description of the project (required)
        - genre: Music genre (default: 'Pop')
        - bpm: Beats per minute (default: 100)
        - duration: Target duration as "MM:SS" (default: '3:00')
        - mood: Mood/Instrumentation description (default: 'happy')
        - vocalStyle: Vocal style description (default: 'Male')

    Returns:
        - sunoPrompt: Complete Suno Custom Mode prompt (Style + Lyrics + Advanced Options)
    """
    try:
        data = request.get_json()

        # 1. Daten aus dem Frontend extrahieren
        theme = data.get('theme', 'No theme provided')
        genre = data.get('genre', 'Pop')
        bpm = int(data.get('bpm', 100))
        duration_str = data.get('duration', '3:00')
        mood = data.get('mood', 'happy')
        vocals = data.get('vocalStyle', 'Male')

        # Validierung
        if not theme or theme == 'No theme provided':
            return jsonify(create_error_response(
                'missing_field',
                'theme is required'
            )), 400

        # 2. Dauer-String in Minuten (float) umwandeln
        try:
            parts = duration_str.split(':')
            minutes = int(parts[0])
            seconds = int(parts[1])
            duration_float = minutes + (seconds / 60.0)
        except (ValueError, IndexError):
            return jsonify(create_error_response(
                'invalid_duration',
                'duration must be in format MM:SS (e.g., "3:00")'
            )), 400

        # 3. Ziel-Wortanzahl berechnen
        target_words, wpm = calculate_lyrics_length(bpm, duration_float, genre)

        logger.info(f"Calculated lyrics length: {target_words} words at {wpm} WPM for {genre} @ {bpm} BPM")

        # 4. Echter LLM-Aufruf zur Lyric-Generierung via Gemini
        try:
            logger.info(f"Calling Gemini to generate lyrics for theme: {theme[:50]}...")

            real_lyrics = generate_song_lyrics(
                theme=theme,
                genre=genre,
                mood=mood,
                target_words=target_words,
                bpm=bpm,
                vocal_style=vocals
            )

            logger.info(f"Lyrics generated successfully: {len(real_lyrics)} characters")

        except Exception as gemini_error:
            # Fallback: Wenn Gemini fehlschlägt, verwende Platzhalter
            logger.error(f"Gemini lyrics generation failed: {gemini_error}")

            # Calculate word distribution for fallback
            intro_words = int(target_words * 0.05)
            verse_words = int(target_words * 0.20)
            chorus_words = int(target_words * 0.25)
            bridge_words = int(target_words * 0.05)
            outro_words = int(target_words * 0.05)

            real_lyrics = f"""⚠️ FALLBACK MODE - Gemini API nicht verfügbar

[Intro]
(Instrumental intro starts, {bpm} BPM)

[Verse 1]
(Lyrics zum Thema '{theme}' - ca. {verse_words} Wörter)
Platzhalter-Lyrics für Verse 1...

[Chorus]
(Eingängiger Chorus - ca. {chorus_words} Wörter)
Platzhalter-Lyrics für Chorus...

[Verse 2]
(Mehr Lyrics - ca. {verse_words} Wörter)
Platzhalter-Lyrics für Verse 2...

[Chorus]
(Chorus-Wiederholung - ca. {chorus_words} Wörter)
Platzhalter-Lyrics für Chorus...

[Bridge]
(Bridge - ca. {bridge_words} Wörter)
Platzhalter-Lyrics für Bridge...

[Final Chorus]
(Final Chorus - ca. {chorus_words} Wörter)
Platzhalter-Lyrics für Final Chorus...

[Outro]
(Outro - ca. {outro_words} Wörter)
Platzhalter-Lyrics für Outro...

ERROR: {str(gemini_error)}
Bitte überprüfen Sie die Gemini-Konfiguration in services/gemini_service.py"""

        # 5. Finalen Prompt im "Custom Mode"-Format zusammenbauen
        style_of_music = f"{genre}, {bpm} BPM, {mood}, {vocals}"

        # 6. Kombinierten String zurück an das Frontend senden
        output_text = f"""--- STYLE OF MUSIC ---
{style_of_music}

--- LYRICS ---
{real_lyrics}

--- ADVANCED OPTIONS ---
Vocal Gender: {vocals}
Lyrics Mode: Manual
Weirdness: 50
Style Influence: 60

--- METADATA ---
Target Words: {target_words}
Words Per Minute: {wpm}
Duration: {duration_str}
BPM: {bpm}
Theme: {theme}"""

        logger.info(f"Generated Suno prompt for theme: {theme[:50]}... ({target_words} words)")

        return jsonify({
            'sunoPrompt': output_text
        }), 200

    except Exception as e:
        logger.error(f"Suno prompt generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify(create_error_response(
            'internal_error',
            f'Failed to generate Suno prompt: {str(e)}'
        )), 500


@screenplay_bp.route('/export-prompts/image', methods=['POST'])
def export_image_prompts():
    """
    Export all image prompts as a TXT file

    Request Body:
        - project_id: Project/screenplay ID

    Returns:
        Text file with all image prompts
    """
    try:
        data = request.get_json()

        if 'project_id' not in data:
            return jsonify(create_error_response(
                'missing_field',
                'project_id is required'
            )), 400

        project_id = data['project_id']

        # Get scenes from database
        with db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT scene_number, heading, description
                FROM screenplay_scenes
                WHERE screenplay_id = ?
                ORDER BY scene_number
            """, (project_id,))

            scenes = cursor.fetchall()

        if not scenes:
            return jsonify(create_error_response(
                'not_found',
                'No scenes found for this project'
            )), 404

        # Generate prompts text
        prompts_text = "IMAGE GENERATION PROMPTS\n"
        prompts_text += "=" * 50 + "\n\n"

        for scene in scenes:
            scene_number, heading, description = scene
            prompts_text += f"SCENE {scene_number}\n"
            prompts_text += f"{heading}\n"
            prompts_text += f"\nPrompt: {description}\n"
            prompts_text += "-" * 50 + "\n\n"

        # Return as file download
        from flask import send_file
        output = io.BytesIO()
        output.write(prompts_text.encode('utf-8'))
        output.seek(0)

        return send_file(
            output,
            mimetype='text/plain',
            as_attachment=True,
            download_name='image-prompts.txt'
        )

    except Exception as e:
        logger.error(f"Image prompts export failed: {str(e)}")
        return jsonify(create_error_response(
            'internal_error',
            'Failed to export image prompts'
        )), 500


@screenplay_bp.route('/upload-manual-image', methods=['POST'])
def upload_manual_image():
    """
    Upload manually created image for a scene

    Request:
        - scene_id: Scene ID (form data)
        - image: Image file (multipart/form-data)

    Returns:
        - imageUrl: URL/path to the uploaded image
    """
    try:
        if 'scene_id' not in request.form:
            return jsonify(create_error_response(
                'missing_field',
                'scene_id is required'
            )), 400

        if 'image' not in request.files:
            return jsonify(create_error_response(
                'missing_file',
                'No image file uploaded'
            )), 400

        scene_id = request.form['scene_id']
        image_file = request.files['image']

        if image_file.filename == '':
            return jsonify(create_error_response(
                'empty_filename',
                'No file selected'
            )), 400

        # Read and encode image
        import base64
        image_data = image_file.read()
        base64_data = base64.b64encode(image_data).decode('utf-8')

        # Store in database
        with db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE screenplay_scenes
                SET image_data = ?, image_url = ?
                WHERE id = ?
            """, (base64_data, f"manual_{scene_id}.png", scene_id))

        logger.info(f"Manual image uploaded for scene: {scene_id}")

        return jsonify({
            'imageUrl': f"data:image/png;base64,{base64_data}"
        }), 200

    except Exception as e:
        logger.error(f"Manual image upload failed: {str(e)}")
        return jsonify(create_error_response(
            'internal_error',
            'Failed to upload manual image'
        )), 500


@screenplay_bp.route('/export-prompts/video', methods=['POST'])
def export_video_prompts():
    """
    Export all video prompts as a TXT file

    Request Body:
        - project_id: Project/screenplay ID

    Returns:
        Text file with all video prompts
    """
    try:
        data = request.get_json()

        if 'project_id' not in data:
            return jsonify(create_error_response(
                'missing_field',
                'project_id is required'
            )), 400

        project_id = data['project_id']

        # Get scenes from database
        with db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT scene_number, heading, description
                FROM screenplay_scenes
                WHERE screenplay_id = ?
                ORDER BY scene_number
            """, (project_id,))

            scenes = cursor.fetchall()

        if not scenes:
            return jsonify(create_error_response(
                'not_found',
                'No scenes found for this project'
            )), 404

        # Generate video prompts text
        prompts_text = "VIDEO GENERATION PROMPTS (Veo/Runway)\n"
        prompts_text += "=" * 50 + "\n\n"

        for scene in scenes:
            scene_number, heading, description = scene

            # Generate video prompt based on scene description
            video_prompt = f"Create a cinematic video sequence: {description}. "
            video_prompt += f"Camera movement: smooth and professional. "
            video_prompt += f"Duration: 5-10 seconds. Style: {heading}"

            prompts_text += f"SCENE {scene_number}\n"
            prompts_text += f"{heading}\n"
            prompts_text += f"\nVideo Prompt: {video_prompt}\n"
            prompts_text += "-" * 50 + "\n\n"

        # Return as file download
        from flask import send_file
        output = io.BytesIO()
        output.write(prompts_text.encode('utf-8'))
        output.seek(0)

        return send_file(
            output,
            mimetype='text/plain',
            as_attachment=True,
            download_name='video-prompts.txt'
        )

    except Exception as e:
        logger.error(f"Video prompts export failed: {str(e)}")
        return jsonify(create_error_response(
            'internal_error',
            'Failed to export video prompts'
        )), 500


@screenplay_bp.route('/upload-manual-clip', methods=['POST'])
def upload_manual_clip():
    """
    Upload manually created video clip for a scene

    Request:
        - scene_id: Scene ID (form data)
        - video: Video file (multipart/form-data)

    Returns:
        - videoUrl: URL/path to the uploaded video
    """
    try:
        if 'scene_id' not in request.form:
            return jsonify(create_error_response(
                'missing_field',
                'scene_id is required'
            )), 400

        if 'video' not in request.files:
            return jsonify(create_error_response(
                'missing_file',
                'No video file uploaded'
            )), 400

        scene_id = request.form['scene_id']
        video_file = request.files['video']

        if video_file.filename == '':
            return jsonify(create_error_response(
                'empty_filename',
                'No file selected'
            )), 400

        # For now, we'll store video reference
        # In production, upload to cloud storage (GCS, S3, etc.)
        video_filename = f"manual_{scene_id}_{video_file.filename}"

        # Store reference in database
        with db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE screenplay_scenes
                SET video_url = ?
                WHERE id = ?
            """, (video_filename, scene_id))

        logger.info(f"Manual video clip uploaded for scene: {scene_id}")

        return jsonify({
            'videoUrl': f"/uploads/videos/{video_filename}"
        }), 200

    except Exception as e:
        logger.error(f"Manual clip upload failed: {str(e)}")
        return jsonify(create_error_response(
            'internal_error',
            'Failed to upload manual clip'
        )), 500


@screenplay_bp.route('/generate-metadata', methods=['POST'])
def generate_metadata():
    """
    Generate YouTube metadata (title, description, tags)

    Request Body:
        - project_id: Project/screenplay ID

    Returns:
        - title: Array of title suggestions
        - description: Generated description
        - tags: Array of relevant tags
    """
    try:
        data = request.get_json()

        if 'project_id' not in data:
            return jsonify(create_error_response(
                'missing_field',
                'project_id is required'
            )), 400

        project_id = data['project_id']

        # Get screenplay info from database
        with db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT title, scene_count
                FROM screenplays
                WHERE id = ?
            """, (project_id,))

            screenplay = cursor.fetchone()

            if not screenplay:
                return jsonify(create_error_response(
                    'not_found',
                    'Project not found'
                )), 404

            title, scene_count = screenplay

            # Get first few scenes for context
            cursor.execute("""
                SELECT heading, description
                FROM screenplay_scenes
                WHERE screenplay_id = ?
                ORDER BY scene_number
                LIMIT 3
            """, (project_id,))

            scenes = cursor.fetchall()

        # TODO: Use AI to generate better metadata
        # For now, create template-based metadata

        title_suggestions = [
            f"{title} - Music Video",
            f"{title} | Official Music Video",
            f"{title} - Cinematic Music Video",
        ]

        description = f"""🎵 {title} - Official Music Video

This cinematic music video brings the story of {title} to life through {scene_count} visually stunning scenes.

Created with cutting-edge AI technology combining:
• Suno AI for music composition
• Imagen 4 for visual generation
• Veo for video production

🎬 Visual Storytelling
Each scene was carefully crafted to match the emotional arc of the music, creating a seamless blend of sound and vision.

📱 Follow for more:
• Subscribe for more AI-generated music videos
• Like if you enjoyed this production
• Comment your favorite scene!

#MusicVideo #AIArt #CinematicVideo #AIMusic #VisualArt"""

        tags = [
            title.lower().replace(' ', ''),
            'music video',
            'ai generated',
            'cinematic',
            'visual art',
            'ai music',
            'suno ai',
            'imagen 4',
            'veo',
            'music production',
            'ai creativity',
            'digital art'
        ]

        logger.info(f"Generated metadata for project: {project_id}")

        return jsonify({
            'title': title_suggestions,
            'description': description,
            'tags': tags
        }), 200

    except Exception as e:
        logger.error(f"Metadata generation failed: {str(e)}")
        return jsonify(create_error_response(
            'internal_error',
            'Failed to generate metadata'
        )), 500
