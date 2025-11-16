"""
Storyboard Routes - API Endpoints for Video Production Workflow
================================================================
Handles all storyboard-related API endpoints for the Music Video Production System.

Endpoints:
- Google Drive Integration (folders, files, download)
- Runway Video Generation (generate, status, cost)
- Dadan Metadata Generation (YouTube optimization)
- Recraft Thumbnail Generation (variants, comparison)

Author: Music Video Production System
Version: 1.0.0
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from typing import Dict, Any

# Import services
from services.google_drive_service import create_drive_service
from services.runway_service import create_runway_service, get_available_engines
from services.dadan_service import create_dadan_service, get_supported_genres, get_supported_moods
from services.recraft_service import create_recraft_service, get_available_variants
from services.api_key_manager import get_api_key as get_encrypted_api_key

logger = logging.getLogger(__name__)

# Create Blueprint
storyboard_bp = Blueprint('storyboard', __name__)


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def get_api_key(user_id: str, service: str) -> str:
    """
    Get API key for a service from encrypted database storage

    Args:
        user_id: User identifier
        service: Service name (google_drive, runway, dadan, recraft)

    Returns:
        Decrypted API key or empty string if not found
    """
    try:
        api_key = get_encrypted_api_key(user_id, service)
        return api_key or ""
    except Exception as e:
        logger.error(f"Failed to retrieve API key for {service}: {str(e)}")
        return ""


def create_error_response(
    error_code: str,
    message: str,
    details: Dict[str, Any] = None,
    retryable: bool = False
) -> Dict[str, Any]:
    """
    Create standardized error response

    Args:
        error_code: Error code identifier
        message: Human-readable error message
        details: Additional error details
        retryable: Whether the request can be retried

    Returns:
        Error response dictionary
    """
    response = {
        'error': error_code,
        'message': message,
        'retryable': retryable,
        'timestamp': datetime.now().isoformat()
    }

    if details:
        response['details'] = details

    return response


# ============================================================
# GOOGLE DRIVE ENDPOINTS
# ============================================================

@storyboard_bp.route('/drive/folders', methods=['GET'])
def drive_list_folders():
    """
    List folders in Google Drive

    Query Params:
        parent_id: Parent folder ID (default: 'root')
        access_token: OAuth2 access token (required)

    Returns:
        List of folders with metadata
    """
    try:
        parent_id = request.args.get('parent_id', 'root')
        access_token = request.args.get('access_token')

        if not access_token:
            return jsonify(create_error_response(
                'TOKEN_REQUIRED',
                'OAuth2 access token is required',
                retryable=False
            )), 400

        # Create Drive service
        drive_service = create_drive_service(access_token)

        # List folders
        result = drive_service.list_folders(parent_id)

        if 'error' in result:
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Drive folders endpoint error: {str(e)}")
        return jsonify(create_error_response(
            'ENDPOINT_ERROR',
            str(e),
            retryable=True
        )), 500


@storyboard_bp.route('/drive/files/<folder_id>', methods=['GET'])
def drive_list_files(folder_id: str):
    """
    List files in a folder

    Path Params:
        folder_id: Folder ID

    Query Params:
        file_type: Filter by type ('audio', 'video', 'image', 'all')
        access_token: OAuth2 access token (required)

    Returns:
        List of files with metadata
    """
    try:
        file_type = request.args.get('file_type', 'audio')
        access_token = request.args.get('access_token')

        if not access_token:
            return jsonify(create_error_response(
                'TOKEN_REQUIRED',
                'OAuth2 access token is required',
                retryable=False
            )), 400

        # Create Drive service
        drive_service = create_drive_service(access_token)

        # List files
        result = drive_service.list_files(folder_id, file_type)

        if 'error' in result:
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Drive files endpoint error: {str(e)}")
        return jsonify(create_error_response(
            'ENDPOINT_ERROR',
            str(e),
            retryable=True
        )), 500


@storyboard_bp.route('/drive/file/<file_id>/metadata', methods=['GET'])
def drive_file_metadata(file_id: str):
    """
    Get file metadata

    Path Params:
        file_id: File ID

    Query Params:
        access_token: OAuth2 access token (required)

    Returns:
        File metadata
    """
    try:
        access_token = request.args.get('access_token')

        if not access_token:
            return jsonify(create_error_response(
                'TOKEN_REQUIRED',
                'OAuth2 access token is required',
                retryable=False
            )), 400

        # Create Drive service
        drive_service = create_drive_service(access_token)

        # Get metadata
        result = drive_service.get_file_metadata(file_id)

        if 'error' in result:
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Drive metadata endpoint error: {str(e)}")
        return jsonify(create_error_response(
            'ENDPOINT_ERROR',
            str(e),
            retryable=True
        )), 500


# ============================================================
# RUNWAY VIDEO GENERATION ENDPOINTS
# ============================================================

@storyboard_bp.route('/video/generate', methods=['POST'])
def video_generate():
    """
    Generate video with Runway

    Request Body:
        prompt: Generation prompt (required)
        duration: Video duration in seconds (required)
        style: Visual style (optional)
        engine: Generation engine (optional, default: runway_standard)
        music_file: Audio file URL/path (optional)

    Returns:
        Generation task information
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify(create_error_response(
                'INVALID_REQUEST',
                'Request body is required',
                retryable=False
            )), 400

        # Validate required fields
        prompt = data.get('prompt')
        duration = data.get('duration')

        if not prompt or not duration:
            return jsonify(create_error_response(
                'MISSING_FIELDS',
                'prompt and duration are required',
                retryable=False
            )), 400

        # Optional fields
        style = data.get('style')
        engine = data.get('engine', 'runway_standard')
        music_file = data.get('music_file')

        # Get API key (from database or environment)
        api_key = get_api_key('user_1', 'runway')

        # Create Runway service
        runway_service = create_runway_service(api_key)

        # Generate video
        result = runway_service.generate_video(
            prompt=prompt,
            duration=duration,
            style=style,
            engine=engine,
            music_file=music_file
        )

        if 'error' in result:
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Video generation endpoint error: {str(e)}")
        return jsonify(create_error_response(
            'ENDPOINT_ERROR',
            str(e),
            retryable=True
        )), 500


@storyboard_bp.route('/video/<task_id>/status', methods=['GET'])
def video_status(task_id: str):
    """
    Get video generation status

    Path Params:
        task_id: Task identifier

    Returns:
        Current generation status
    """
    try:
        # Get API key
        api_key = get_api_key('user_1', 'runway')

        # Create Runway service
        runway_service = create_runway_service(api_key)

        # Poll status
        result = runway_service.poll_status(task_id)

        if 'error' in result:
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Video status endpoint error: {str(e)}")
        return jsonify(create_error_response(
            'ENDPOINT_ERROR',
            str(e),
            retryable=True
        )), 500


@storyboard_bp.route('/video/engines', methods=['GET'])
def video_engines():
    """
    Get available video generation engines

    Returns:
        List of available engines with pricing
    """
    try:
        engines = get_available_engines()
        return jsonify({
            'engines': engines,
            'count': len(engines),
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Engines endpoint error: {str(e)}")
        return jsonify(create_error_response(
            'ENDPOINT_ERROR',
            str(e),
            retryable=True
        )), 500


@storyboard_bp.route('/video/calculate-cost', methods=['POST'])
def video_calculate_cost():
    """
    Calculate video generation cost

    Request Body:
        duration: Video duration in seconds (required)
        engine: Generation engine (required)

    Returns:
        Cost breakdown
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify(create_error_response(
                'INVALID_REQUEST',
                'Request body is required',
                retryable=False
            )), 400

        duration = data.get('duration')
        engine = data.get('engine')

        if not duration or not engine:
            return jsonify(create_error_response(
                'MISSING_FIELDS',
                'duration and engine are required',
                retryable=False
            )), 400

        # Create Runway service
        runway_service = create_runway_service()

        # Calculate cost
        result = runway_service.calculate_cost(duration, engine)

        if 'error' in result:
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Cost calculation endpoint error: {str(e)}")
        return jsonify(create_error_response(
            'ENDPOINT_ERROR',
            str(e),
            retryable=True
        )), 500


# ============================================================
# DADAN METADATA GENERATION ENDPOINTS
# ============================================================

@storyboard_bp.route('/metadata/generate', methods=['POST'])
def metadata_generate():
    """
    Generate YouTube metadata

    Request Body:
        song_title: Song title (required)
        genre: Music genre (required)
        mood: Song mood (optional)

    Returns:
        YouTube metadata (title, description, tags, hashtags)
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify(create_error_response(
                'INVALID_REQUEST',
                'Request body is required',
                retryable=False
            )), 400

        song_title = data.get('song_title')
        genre = data.get('genre')
        mood = data.get('mood')

        if not song_title or not genre:
            return jsonify(create_error_response(
                'MISSING_FIELDS',
                'song_title and genre are required',
                retryable=False
            )), 400

        # Get API key
        api_key = get_api_key('user_1', 'dadan')

        # Create Dadan service
        dadan_service = create_dadan_service(api_key)

        # Generate metadata
        result = dadan_service.generate_metadata(song_title, genre, mood)

        if 'error' in result:
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Metadata generation endpoint error: {str(e)}")
        return jsonify(create_error_response(
            'ENDPOINT_ERROR',
            str(e),
            retryable=True
        )), 500


@storyboard_bp.route('/metadata/genres', methods=['GET'])
def metadata_genres():
    """
    Get supported genres

    Returns:
        List of supported genres
    """
    try:
        genres = get_supported_genres()
        return jsonify({
            'genres': genres,
            'count': len(genres),
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Genres endpoint error: {str(e)}")
        return jsonify(create_error_response(
            'ENDPOINT_ERROR',
            str(e),
            retryable=True
        )), 500


@storyboard_bp.route('/metadata/moods', methods=['GET'])
def metadata_moods():
    """
    Get supported moods

    Returns:
        List of supported moods
    """
    try:
        moods = get_supported_moods()
        return jsonify({
            'moods': moods,
            'count': len(moods),
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Moods endpoint error: {str(e)}")
        return jsonify(create_error_response(
            'ENDPOINT_ERROR',
            str(e),
            retryable=True
        )), 500


# ============================================================
# RECRAFT THUMBNAIL GENERATION ENDPOINTS
# ============================================================

@storyboard_bp.route('/thumbnails/generate', methods=['POST'])
def thumbnails_generate():
    """
    Generate thumbnail variants

    Request Body:
        video_url: Video URL or path (required)
        context: Additional context (song_title, genre, mood, etc.) (optional)
        variants: List of variant types (optional, default: all)

    Returns:
        Thumbnail variants with click predictions
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify(create_error_response(
                'INVALID_REQUEST',
                'Request body is required',
                retryable=False
            )), 400

        video_url = data.get('video_url')

        if not video_url:
            return jsonify(create_error_response(
                'MISSING_FIELDS',
                'video_url is required',
                retryable=False
            )), 400

        context = data.get('context')
        variants = data.get('variants')

        # Get API key
        api_key = get_api_key('user_1', 'recraft')

        # Create Recraft service
        recraft_service = create_recraft_service(api_key)

        # Generate thumbnails
        result = recraft_service.generate_thumbnails(video_url, context, variants)

        if 'error' in result:
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Thumbnail generation endpoint error: {str(e)}")
        return jsonify(create_error_response(
            'ENDPOINT_ERROR',
            str(e),
            retryable=True
        )), 500


@storyboard_bp.route('/thumbnails/variants', methods=['GET'])
def thumbnails_variants():
    """
    Get available thumbnail variants

    Returns:
        List of available variants with descriptions
    """
    try:
        variants = get_available_variants()
        return jsonify({
            'variants': variants,
            'count': len(variants),
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Variants endpoint error: {str(e)}")
        return jsonify(create_error_response(
            'ENDPOINT_ERROR',
            str(e),
            retryable=True
        )), 500


@storyboard_bp.route('/thumbnails/extract-frame', methods=['POST'])
def thumbnails_extract_frame():
    """
    Extract frame from video

    Request Body:
        video_url: Video URL or path (required)
        timestamp: Timestamp in seconds (optional, default: 5)

    Returns:
        Extracted frame URL
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify(create_error_response(
                'INVALID_REQUEST',
                'Request body is required',
                retryable=False
            )), 400

        video_url = data.get('video_url')

        if not video_url:
            return jsonify(create_error_response(
                'MISSING_FIELDS',
                'video_url is required',
                retryable=False
            )), 400

        timestamp = data.get('timestamp', 5)

        # Get API key
        api_key = get_api_key('user_1', 'recraft')

        # Create Recraft service
        recraft_service = create_recraft_service(api_key)

        # Extract frame
        result = recraft_service.extract_frame(video_url, timestamp)

        if 'error' in result:
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Frame extraction endpoint error: {str(e)}")
        return jsonify(create_error_response(
            'ENDPOINT_ERROR',
            str(e),
            retryable=True
        )), 500


# ============================================================
# API KEY MANAGEMENT ENDPOINTS
# ============================================================

@storyboard_bp.route('/api-keys', methods=['POST'])
def api_keys_save():
    """
    Save (or update) an encrypted API key

    Request Body:
        user_id: User identifier (required)
        service: Service name (required)
        api_key: Plain text API key (required)

    Returns:
        Save result
    """
    try:
        from services.api_key_manager import save_api_key

        data = request.get_json()

        if not data:
            return jsonify(create_error_response(
                'INVALID_REQUEST',
                'Request body is required',
                retryable=False
            )), 400

        user_id = data.get('user_id')
        service = data.get('service')
        api_key = data.get('api_key')

        if not user_id or not service or not api_key:
            return jsonify(create_error_response(
                'MISSING_FIELDS',
                'user_id, service, and api_key are required',
                retryable=False
            )), 400

        # Save API key
        result = save_api_key(user_id, service, api_key)

        if 'error' in result:
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"API key save endpoint error: {str(e)}")
        return jsonify(create_error_response(
            'ENDPOINT_ERROR',
            str(e),
            retryable=True
        )), 500


@storyboard_bp.route('/api-keys/<user_id>', methods=['GET'])
def api_keys_list(user_id: str):
    """
    List all API keys for a user (without revealing actual keys)

    Path Params:
        user_id: User identifier

    Returns:
        List of services with API keys
    """
    try:
        from services.api_key_manager import get_api_key_manager

        manager = get_api_key_manager()
        result = manager.list_user_keys(user_id)

        if 'error' in result:
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"API key list endpoint error: {str(e)}")
        return jsonify(create_error_response(
            'ENDPOINT_ERROR',
            str(e),
            retryable=True
        )), 500


@storyboard_bp.route('/api-keys/<user_id>/<service>', methods=['DELETE'])
def api_keys_delete(user_id: str, service: str):
    """
    Delete an API key

    Path Params:
        user_id: User identifier
        service: Service name

    Returns:
        Deletion result
    """
    try:
        from services.api_key_manager import delete_api_key

        result = delete_api_key(user_id, service)

        if 'error' in result:
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"API key delete endpoint error: {str(e)}")
        return jsonify(create_error_response(
            'ENDPOINT_ERROR',
            str(e),
            retryable=True
        )), 500


@storyboard_bp.route('/api-keys/<user_id>/<service>/validate', methods=['GET'])
def api_keys_validate(user_id: str, service: str):
    """
    Validate that an API key exists

    Path Params:
        user_id: User identifier
        service: Service name

    Returns:
        Validation result
    """
    try:
        from services.api_key_manager import validate_api_key

        is_valid = validate_api_key(user_id, service)

        return jsonify({
            'user_id': user_id,
            'service': service,
            'has_key': is_valid,
            'valid': is_valid,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"API key validation endpoint error: {str(e)}")
        return jsonify(create_error_response(
            'ENDPOINT_ERROR',
            str(e),
            retryable=True
        )), 500


@storyboard_bp.route('/api-keys/services', methods=['GET'])
def api_keys_services():
    """
    Get list of supported services

    Returns:
        Supported services with metadata
    """
    try:
        from services.api_key_manager import get_supported_services

        services = get_supported_services()

        return jsonify({
            'services': services,
            'count': len(services),
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Services endpoint error: {str(e)}")
        return jsonify(create_error_response(
            'ENDPOINT_ERROR',
            str(e),
            retryable=True
        )), 500


# ============================================================
# HEALTH CHECK
# ============================================================

@storyboard_bp.route('/health', methods=['GET'])
def health_check():
    """
    Storyboard API health check

    Returns:
        Service health status
    """
    return jsonify({
        'status': 'operational',
        'service': 'Storyboard API',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'drive': 3,
            'video': 4,
            'metadata': 3,
            'thumbnails': 3,
            'api_keys': 5
        }
    }), 200
