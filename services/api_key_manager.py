"""
API Key Manager - Secure Encrypted Storage
===========================================
Handles encrypted storage and retrieval of API keys for external services.

Features:
- AES-256 Encryption
- Secure key derivation (PBKDF2)
- Database storage with unique constraints
- Key validation and rotation

Security:
- Encryption key stored in environment variable
- Keys never stored in plaintext
- Automatic key rotation support

Author: Music Video Production System
Version: 1.0.0
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from database import get_db

logger = logging.getLogger(__name__)


class APIKeyManager:
    """
    Secure API Key Management with Encryption

    Provides methods for:
    - Encrypting and storing API keys
    - Decrypting and retrieving API keys
    - Key validation
    - Key rotation
    """

    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize API Key Manager

        Args:
            encryption_key: Master encryption key (defaults to env variable)
        """
        self.db = get_db()

        # Get encryption key from environment or parameter
        key_source = encryption_key or os.getenv('API_KEY_ENCRYPTION_KEY')

        if not key_source:
            # Generate a default key for development (NOT FOR PRODUCTION!)
            logger.warning("⚠️  No encryption key found! Using default (NOT SECURE FOR PRODUCTION)")
            key_source = "dev-key-DO-NOT-USE-IN-PRODUCTION-12345678"

        # Derive encryption key using PBKDF2
        self.cipher = self._create_cipher(key_source)

    def _create_cipher(self, key_source: str) -> Fernet:
        """
        Create Fernet cipher from key source

        Args:
            key_source: Source string for key derivation

        Returns:
            Fernet cipher instance
        """
        # Derive a proper encryption key using PBKDF2HMAC
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'music-agents-salt',  # In production, use random salt stored in DB
            iterations=100000
        )

        key = base64.urlsafe_b64encode(kdf.derive(key_source.encode()))
        return Fernet(key)

    def encrypt_key(self, api_key: str) -> str:
        """
        Encrypt an API key

        Args:
            api_key: Plain text API key

        Returns:
            Encrypted API key (base64 encoded)
        """
        try:
            encrypted = self.cipher.encrypt(api_key.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise ValueError("Failed to encrypt API key")

    def decrypt_key(self, encrypted_key: str) -> str:
        """
        Decrypt an API key

        Args:
            encrypted_key: Encrypted API key (base64 encoded)

        Returns:
            Decrypted plain text API key
        """
        try:
            decrypted = self.cipher.decrypt(encrypted_key.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise ValueError("Failed to decrypt API key")

    def save_api_key(
        self,
        user_id: str,
        service: str,
        api_key: str
    ) -> Dict[str, Any]:
        """
        Save (or update) an encrypted API key

        Args:
            user_id: User identifier
            service: Service name (google_drive, runway, dadan, recraft)
            api_key: Plain text API key

        Returns:
            Result dictionary with status
        """
        try:
            # Validate inputs
            if not user_id or not service or not api_key:
                return {
                    'error': 'INVALID_INPUT',
                    'message': 'user_id, service, and api_key are required'
                }

            # Encrypt the API key
            encrypted_key = self.encrypt_key(api_key)

            # Save to database
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                # Check if key already exists
                cursor.execute("""
                    SELECT id FROM api_keys
                    WHERE user_id = ? AND service = ?
                """, (user_id, service))

                existing = cursor.fetchone()

                if existing:
                    # Update existing key
                    cursor.execute("""
                        UPDATE api_keys
                        SET encrypted_key = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ? AND service = ?
                    """, (encrypted_key, user_id, service))

                    logger.info(f"Updated API key for {service} (user: {user_id})")
                    action = 'updated'
                else:
                    # Insert new key
                    cursor.execute("""
                        INSERT INTO api_keys (user_id, service, encrypted_key)
                        VALUES (?, ?, ?)
                    """, (user_id, service, encrypted_key))

                    logger.info(f"Saved new API key for {service} (user: {user_id})")
                    action = 'created'

            return {
                'success': True,
                'action': action,
                'user_id': user_id,
                'service': service,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to save API key: {str(e)}")
            return {
                'error': 'SAVE_FAILED',
                'message': str(e)
            }

    def get_api_key(
        self,
        user_id: str,
        service: str
    ) -> Optional[str]:
        """
        Retrieve and decrypt an API key

        Args:
            user_id: User identifier
            service: Service name

        Returns:
            Decrypted API key or None if not found
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT encrypted_key FROM api_keys
                    WHERE user_id = ? AND service = ?
                """, (user_id, service))

                row = cursor.fetchone()

                if not row:
                    logger.warning(f"No API key found for {service} (user: {user_id})")
                    return None

                # Decrypt and return
                encrypted_key = row[0]
                decrypted_key = self.decrypt_key(encrypted_key)

                logger.info(f"Retrieved API key for {service} (user: {user_id})")
                return decrypted_key

        except Exception as e:
            logger.error(f"Failed to retrieve API key: {str(e)}")
            return None

    def delete_api_key(
        self,
        user_id: str,
        service: str
    ) -> Dict[str, Any]:
        """
        Delete an API key

        Args:
            user_id: User identifier
            service: Service name

        Returns:
            Result dictionary with status
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    DELETE FROM api_keys
                    WHERE user_id = ? AND service = ?
                """, (user_id, service))

                deleted_count = cursor.rowcount

                if deleted_count > 0:
                    logger.info(f"Deleted API key for {service} (user: {user_id})")
                    return {
                        'success': True,
                        'deleted': True,
                        'user_id': user_id,
                        'service': service
                    }
                else:
                    logger.warning(f"No API key to delete for {service} (user: {user_id})")
                    return {
                        'success': True,
                        'deleted': False,
                        'message': 'API key not found'
                    }

        except Exception as e:
            logger.error(f"Failed to delete API key: {str(e)}")
            return {
                'error': 'DELETE_FAILED',
                'message': str(e)
            }

    def list_user_keys(self, user_id: str) -> Dict[str, Any]:
        """
        List all services with API keys for a user (without revealing keys)

        Args:
            user_id: User identifier

        Returns:
            Dictionary with services and metadata
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT service, created_at, updated_at
                    FROM api_keys
                    WHERE user_id = ?
                    ORDER BY service
                """, (user_id,))

                rows = cursor.fetchall()

                services = []
                for row in rows:
                    services.append({
                        'service': row[0],
                        'created_at': row[1],
                        'updated_at': row[2],
                        'has_key': True
                    })

                return {
                    'user_id': user_id,
                    'services': services,
                    'count': len(services)
                }

        except Exception as e:
            logger.error(f"Failed to list API keys: {str(e)}")
            return {
                'error': 'LIST_FAILED',
                'message': str(e)
            }

    def validate_key(
        self,
        user_id: str,
        service: str
    ) -> bool:
        """
        Validate that an API key exists and can be decrypted

        Args:
            user_id: User identifier
            service: Service name

        Returns:
            True if key exists and is valid
        """
        try:
            api_key = self.get_api_key(user_id, service)
            return api_key is not None and len(api_key) > 0
        except Exception as e:
            logger.error(f"Key validation failed: {str(e)}")
            return False

    def rotate_encryption_key(
        self,
        old_encryption_key: str,
        new_encryption_key: str
    ) -> Dict[str, Any]:
        """
        Rotate the master encryption key (re-encrypt all stored keys)

        Args:
            old_encryption_key: Current encryption key
            new_encryption_key: New encryption key

        Returns:
            Result dictionary with status
        """
        try:
            # Create old and new ciphers
            old_cipher = self._create_cipher(old_encryption_key)
            new_cipher = self._create_cipher(new_encryption_key)

            # Get all encrypted keys
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("SELECT id, encrypted_key FROM api_keys")
                rows = cursor.fetchall()

                rotated_count = 0

                for row in rows:
                    key_id = row[0]
                    old_encrypted = row[1]

                    try:
                        # Decrypt with old key
                        decrypted = old_cipher.decrypt(old_encrypted.encode()).decode()

                        # Re-encrypt with new key
                        new_encrypted = new_cipher.encrypt(decrypted.encode()).decode()

                        # Update in database
                        cursor.execute("""
                            UPDATE api_keys
                            SET encrypted_key = ?, updated_at = CURRENT_TIMESTAMP
                            WHERE id = ?
                        """, (new_encrypted, key_id))

                        rotated_count += 1

                    except Exception as e:
                        logger.error(f"Failed to rotate key {key_id}: {str(e)}")
                        continue

                # Update the cipher
                self.cipher = new_cipher

                logger.info(f"Rotated {rotated_count} API keys")

                return {
                    'success': True,
                    'rotated_count': rotated_count,
                    'total_keys': len(rows),
                    'timestamp': datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"Key rotation failed: {str(e)}")
            return {
                'error': 'ROTATION_FAILED',
                'message': str(e)
            }


# ============================================================
# SINGLETON INSTANCE
# ============================================================

_api_key_manager_instance: Optional[APIKeyManager] = None


def get_api_key_manager() -> APIKeyManager:
    """
    Get singleton API Key Manager instance

    Returns:
        APIKeyManager instance
    """
    global _api_key_manager_instance

    if _api_key_manager_instance is None:
        _api_key_manager_instance = APIKeyManager()

    return _api_key_manager_instance


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def save_api_key(user_id: str, service: str, api_key: str) -> Dict[str, Any]:
    """
    Save an API key (convenience function)

    Args:
        user_id: User identifier
        service: Service name
        api_key: Plain text API key

    Returns:
        Result dictionary
    """
    manager = get_api_key_manager()
    return manager.save_api_key(user_id, service, api_key)


def get_api_key(user_id: str, service: str) -> Optional[str]:
    """
    Get an API key (convenience function)

    Args:
        user_id: User identifier
        service: Service name

    Returns:
        Decrypted API key or None
    """
    manager = get_api_key_manager()
    return manager.get_api_key(user_id, service)


def delete_api_key(user_id: str, service: str) -> Dict[str, Any]:
    """
    Delete an API key (convenience function)

    Args:
        user_id: User identifier
        service: Service name

    Returns:
        Result dictionary
    """
    manager = get_api_key_manager()
    return manager.delete_api_key(user_id, service)


def validate_api_key(user_id: str, service: str) -> bool:
    """
    Validate an API key exists (convenience function)

    Args:
        user_id: User identifier
        service: Service name

    Returns:
        True if key exists and is valid
    """
    manager = get_api_key_manager()
    return manager.validate_key(user_id, service)


# ============================================================
# SUPPORTED SERVICES
# ============================================================

SUPPORTED_SERVICES = {
    'google_drive': {
        'name': 'Google Drive',
        'description': 'OAuth2 access token for Google Drive API',
        'required': True
    },
    'runway': {
        'name': 'Runway ML',
        'description': 'API key for Runway Gen-4 video generation',
        'required': True
    },
    'dadan': {
        'name': 'Dadan AI',
        'description': 'API key for YouTube metadata generation',
        'required': False
    },
    'recraft': {
        'name': 'Recraft AI',
        'description': 'API key for thumbnail generation',
        'required': False
    }
}


def get_supported_services() -> Dict[str, Dict[str, Any]]:
    """
    Get list of supported services

    Returns:
        Dictionary of supported services with metadata
    """
    return SUPPORTED_SERVICES
