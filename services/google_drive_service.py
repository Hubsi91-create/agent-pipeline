"""
Google Drive Service - OAuth2 Integration
==========================================
Handles Google Drive file browsing, metadata extraction, and downloads.

Features:
- OAuth2 Authentication (Manual Token Input)
- Folder/File Listing
- File Metadata Retrieval
- File Download Streams
- Error Handling with Exponential Backoff

Author: Music Video Production System
Version: 1.0.0
"""

import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import requests

logger = logging.getLogger(__name__)


class GoogleDriveService:
    """
    Google Drive API Integration Service

    Provides methods for:
    - OAuth2 authentication
    - Listing folders and files
    - File metadata extraction
    - File downloads
    """

    DRIVE_API_BASE = "https://www.googleapis.com/drive/v3"

    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize Google Drive Service

        Args:
            access_token: OAuth2 access token (optional, can be set later)
        """
        self.access_token = access_token
        self.headers = {}

        if access_token:
            self._set_access_token(access_token)

    def _set_access_token(self, token: str):
        """Set OAuth2 access token"""
        self.access_token = token
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Make API request with exponential backoff

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            max_retries: Maximum retry attempts

        Returns:
            Response data as dictionary

        Raises:
            Exception: On API errors
        """
        if not self.access_token:
            return {
                'error': 'TOKEN_REQUIRED',
                'message': 'OAuth2 access token is required. Please provide a valid token.',
                'retryable': False
            }

        url = f"{self.DRIVE_API_BASE}/{endpoint}"
        retry_count = 0
        backoff_time = 1  # Start with 1 second

        while retry_count < max_retries:
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    params=params,
                    timeout=30
                )

                # Handle rate limiting (429)
                if response.status_code == 429:
                    retry_count += 1
                    logger.warning(f"Rate limit hit. Retrying in {backoff_time}s... (Attempt {retry_count}/{max_retries})")
                    time.sleep(backoff_time)
                    backoff_time *= 2  # Exponential backoff
                    continue

                # Handle token expiration (401)
                if response.status_code == 401:
                    return {
                        'error': 'TOKEN_EXPIRED',
                        'message': 'OAuth2 token has expired. Please refresh your token.',
                        'retryable': False
                    }

                # Handle not found (404)
                if response.status_code == 404:
                    return {
                        'error': 'NOT_FOUND',
                        'message': 'Resource not found',
                        'retryable': False
                    }

                # Parse response
                response.raise_for_status()
                return response.json()

            except requests.exceptions.Timeout:
                retry_count += 1
                logger.warning(f"Request timeout. Retrying in {backoff_time}s... (Attempt {retry_count}/{max_retries})")
                time.sleep(backoff_time)
                backoff_time *= 2

            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {str(e)}")
                return {
                    'error': 'REQUEST_FAILED',
                    'message': str(e),
                    'retryable': True
                }

        # Max retries exceeded
        return {
            'error': 'MAX_RETRIES_EXCEEDED',
            'message': f'Failed after {max_retries} attempts',
            'retryable': False
        }

    def list_folders(self, parent_id: str = 'root') -> Dict[str, Any]:
        """
        List folders in Google Drive

        Args:
            parent_id: Parent folder ID (default: 'root')

        Returns:
            Dictionary with folders list
        """
        try:
            params = {
                'q': f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false",
                'fields': 'files(id, name, createdTime, modifiedTime)',
                'orderBy': 'name'
            }

            response = self._make_request('GET', 'files', params)

            if 'error' in response:
                return response

            folders = []
            for file in response.get('files', []):
                folders.append({
                    'id': file['id'],
                    'name': file['name'],
                    'created': file.get('createdTime'),
                    'modified': file.get('modifiedTime')
                })

            return {
                'folders': folders,
                'count': len(folders),
                'parent_id': parent_id
            }

        except Exception as e:
            logger.error(f"Failed to list folders: {str(e)}")
            return {
                'error': 'FOLDER_LIST_FAILED',
                'message': str(e),
                'retryable': True
            }

    def list_files(
        self,
        folder_id: str,
        file_type: str = 'audio'
    ) -> Dict[str, Any]:
        """
        List files in a folder

        Args:
            folder_id: Folder ID
            file_type: Filter by type ('audio', 'video', 'image', or 'all')

        Returns:
            Dictionary with files list
        """
        try:
            # Build MIME type filter
            mime_filters = {
                'audio': "mimeType contains 'audio/'",
                'video': "mimeType contains 'video/'",
                'image': "mimeType contains 'image/'",
                'all': ''
            }

            mime_query = mime_filters.get(file_type, mime_filters['audio'])

            # Build query
            query_parts = [
                f"'{folder_id}' in parents",
                "trashed=false",
                "mimeType!='application/vnd.google-apps.folder'"
            ]

            if mime_query:
                query_parts.append(mime_query)

            params = {
                'q': ' and '.join(query_parts),
                'fields': 'files(id, name, mimeType, size, createdTime, modifiedTime, fileExtension)',
                'orderBy': 'name'
            }

            response = self._make_request('GET', 'files', params)

            if 'error' in response:
                return response

            files = []
            for file in response.get('files', []):
                file_data = {
                    'id': file['id'],
                    'name': file['name'],
                    'mimeType': file.get('mimeType'),
                    'size': int(file.get('size', 0)),
                    'extension': file.get('fileExtension'),
                    'created': file.get('createdTime'),
                    'modified': file.get('modifiedTime')
                }

                # Estimate duration for audio/video files (placeholder)
                # In production, you'd use actual metadata
                if 'audio' in file_data['mimeType'] or 'video' in file_data['mimeType']:
                    file_data['duration'] = None  # Would need ffprobe or similar

                files.append(file_data)

            return {
                'files': files,
                'count': len(files),
                'folder_id': folder_id,
                'file_type': file_type
            }

        except Exception as e:
            logger.error(f"Failed to list files: {str(e)}")
            return {
                'error': 'FILE_LIST_FAILED',
                'message': str(e),
                'retryable': True
            }

    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """
        Get detailed file metadata

        Args:
            file_id: File ID

        Returns:
            Dictionary with file metadata
        """
        try:
            params = {
                'fields': 'id, name, mimeType, size, createdTime, modifiedTime, fileExtension, webContentLink, webViewLink, owners, properties'
            }

            response = self._make_request('GET', f'files/{file_id}', params)

            if 'error' in response:
                return response

            metadata = {
                'id': response['id'],
                'name': response['name'],
                'mimeType': response.get('mimeType'),
                'size': int(response.get('size', 0)),
                'extension': response.get('fileExtension'),
                'created': response.get('createdTime'),
                'modified': response.get('modifiedTime'),
                'webContentLink': response.get('webContentLink'),
                'webViewLink': response.get('webViewLink'),
                'owners': response.get('owners', []),
                'properties': response.get('properties', {})
            }

            return metadata

        except Exception as e:
            logger.error(f"Failed to get file metadata: {str(e)}")
            return {
                'error': 'METADATA_FETCH_FAILED',
                'message': str(e),
                'retryable': True
            }

    def download_file(self, file_id: str) -> Dict[str, Any]:
        """
        Get download URL for a file

        Args:
            file_id: File ID

        Returns:
            Dictionary with download information
        """
        try:
            # Get file metadata first
            metadata = self.get_file_metadata(file_id)

            if 'error' in metadata:
                return metadata

            # Return download information
            return {
                'file_id': file_id,
                'name': metadata['name'],
                'size': metadata['size'],
                'download_url': f"{self.DRIVE_API_BASE}/files/{file_id}?alt=media",
                'headers': self.headers,
                'mimeType': metadata['mimeType']
            }

        except Exception as e:
            logger.error(f"Failed to prepare download: {str(e)}")
            return {
                'error': 'DOWNLOAD_PREP_FAILED',
                'message': str(e),
                'retryable': True
            }

    def validate_token(self) -> Dict[str, Any]:
        """
        Validate current OAuth2 token

        Returns:
            Validation result
        """
        try:
            response = self._make_request('GET', 'about', {'fields': 'user'})

            if 'error' in response:
                return {
                    'valid': False,
                    'error': response['error'],
                    'message': response['message']
                }

            return {
                'valid': True,
                'user': response.get('user', {})
            }

        except Exception as e:
            logger.error(f"Token validation failed: {str(e)}")
            return {
                'valid': False,
                'error': 'VALIDATION_FAILED',
                'message': str(e)
            }


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def create_drive_service(access_token: str) -> GoogleDriveService:
    """
    Factory function to create Google Drive service

    Args:
        access_token: OAuth2 access token

    Returns:
        Configured GoogleDriveService instance
    """
    return GoogleDriveService(access_token=access_token)


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format

    Args:
        size_bytes: File size in bytes

    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"
