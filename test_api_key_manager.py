"""
API Key Manager Test Script
============================
Test script for encrypted API key storage and retrieval.

Usage:
    python test_api_key_manager.py

Author: Music Video Production System
Version: 1.0.0
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from services.api_key_manager import (
    save_api_key,
    get_api_key,
    delete_api_key,
    validate_api_key,
    get_api_key_manager,
    get_supported_services
)


def test_save_and_retrieve():
    """Test saving and retrieving API keys"""
    print("\n" + "=" * 60)
    print("TEST 1: Save and Retrieve API Keys")
    print("=" * 60)

    # Test data
    user_id = "test_user_123"
    test_keys = {
        "runway": "sk-runway-test-abc123xyz789",
        "google_drive": "ya29.a0AfB_test_token_xyz",
        "dadan": "dadan-api-key-test-123",
        "recraft": "recraft-key-test-456"
    }

    # Save keys
    print("\n📝 Saving API keys...")
    for service, api_key in test_keys.items():
        result = save_api_key(user_id, service, api_key)

        if result.get('success'):
            print(f"  ✅ {service}: {result['action']}")
        else:
            print(f"  ❌ {service}: {result.get('error')}")

    # Retrieve keys
    print("\n🔍 Retrieving API keys...")
    for service, original_key in test_keys.items():
        retrieved_key = get_api_key(user_id, service)

        if retrieved_key:
            match = "✅ MATCH" if retrieved_key == original_key else "❌ MISMATCH"
            print(f"  {service}: {retrieved_key[:20]}... {match}")
        else:
            print(f"  ❌ {service}: NOT FOUND")

    return user_id, test_keys


def test_list_keys(user_id):
    """Test listing user's API keys"""
    print("\n" + "=" * 60)
    print("TEST 2: List User API Keys")
    print("=" * 60)

    manager = get_api_key_manager()
    result = manager.list_user_keys(user_id)

    if 'error' in result:
        print(f"❌ Error: {result['message']}")
        return

    print(f"\n📋 User: {result['user_id']}")
    print(f"📊 Total Keys: {result['count']}")
    print("\nServices:")

    for service_info in result['services']:
        print(f"  • {service_info['service']}")
        print(f"    Created: {service_info['created_at']}")
        print(f"    Updated: {service_info['updated_at']}")
        print(f"    Has Key: {service_info['has_key']}")


def test_validation(user_id, test_keys):
    """Test API key validation"""
    print("\n" + "=" * 60)
    print("TEST 3: Validate API Keys")
    print("=" * 60)

    print("\n✓ Validating existing keys...")
    for service in test_keys.keys():
        is_valid = validate_api_key(user_id, service)
        status = "✅ VALID" if is_valid else "❌ INVALID"
        print(f"  {service}: {status}")

    print("\n✓ Validating non-existent key...")
    is_valid = validate_api_key(user_id, "nonexistent_service")
    status = "✅ VALID" if is_valid else "❌ INVALID (Expected)"
    print(f"  nonexistent_service: {status}")


def test_update_key(user_id):
    """Test updating an existing API key"""
    print("\n" + "=" * 60)
    print("TEST 4: Update Existing API Key")
    print("=" * 60)

    service = "runway"
    old_key = get_api_key(user_id, service)
    new_key = "sk-runway-updated-xyz999"

    print(f"\n📝 Updating {service} key...")
    print(f"  Old: {old_key[:30]}...")

    result = save_api_key(user_id, service, new_key)

    if result.get('success'):
        print(f"  ✅ Action: {result['action']}")

        retrieved_key = get_api_key(user_id, service)
        print(f"  New: {retrieved_key[:30]}...")

        match = "✅ MATCH" if retrieved_key == new_key else "❌ MISMATCH"
        print(f"  Verification: {match}")
    else:
        print(f"  ❌ Error: {result.get('error')}")


def test_delete_key(user_id):
    """Test deleting an API key"""
    print("\n" + "=" * 60)
    print("TEST 5: Delete API Key")
    print("=" * 60)

    service = "dadan"

    print(f"\n🗑️  Deleting {service} key...")

    # Verify it exists first
    exists_before = validate_api_key(user_id, service)
    print(f"  Before deletion: {'EXISTS' if exists_before else 'NOT FOUND'}")

    # Delete
    result = delete_api_key(user_id, service)

    if result.get('success'):
        print(f"  ✅ Deleted: {result.get('deleted')}")

        # Verify it's gone
        exists_after = validate_api_key(user_id, service)
        print(f"  After deletion: {'EXISTS' if exists_after else 'NOT FOUND (Expected)'}")
    else:
        print(f"  ❌ Error: {result.get('error')}")


def test_supported_services():
    """Test getting supported services"""
    print("\n" + "=" * 60)
    print("TEST 6: Supported Services")
    print("=" * 60)

    services = get_supported_services()

    print(f"\n📚 Total Services: {len(services)}\n")

    for service_id, service_info in services.items():
        required = "✅ REQUIRED" if service_info['required'] else "⚪ OPTIONAL"
        print(f"  {service_id}")
        print(f"    Name: {service_info['name']}")
        print(f"    Description: {service_info['description']}")
        print(f"    Status: {required}")


def test_encryption_decryption():
    """Test encryption/decryption directly"""
    print("\n" + "=" * 60)
    print("TEST 7: Encryption/Decryption")
    print("=" * 60)

    manager = get_api_key_manager()

    test_key = "sk-test-12345-abcdefghijklmnop"

    print(f"\n🔐 Original Key: {test_key}")

    # Encrypt
    encrypted = manager.encrypt_key(test_key)
    print(f"🔒 Encrypted: {encrypted[:60]}...")

    # Decrypt
    decrypted = manager.decrypt_key(encrypted)
    print(f"🔓 Decrypted: {decrypted}")

    # Verify
    match = "✅ MATCH" if decrypted == test_key else "❌ MISMATCH"
    print(f"✓ Verification: {match}")


def cleanup(user_id, test_keys):
    """Clean up test data"""
    print("\n" + "=" * 60)
    print("CLEANUP: Removing Test Data")
    print("=" * 60)

    print("\n🧹 Deleting test API keys...")

    for service in test_keys.keys():
        result = delete_api_key(user_id, service)
        if result.get('deleted'):
            print(f"  ✅ Deleted: {service}")
        else:
            print(f"  ⚪ Not found: {service}")


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("API KEY MANAGER - TEST SUITE")
    print("=" * 80)

    # Check encryption key
    encryption_key = os.getenv('API_KEY_ENCRYPTION_KEY')
    if encryption_key:
        print(f"✅ Encryption Key: Set ({len(encryption_key)} chars)")
    else:
        print("⚠️  Encryption Key: Using default (NOT SECURE FOR PRODUCTION)")

    try:
        # Run tests
        user_id, test_keys = test_save_and_retrieve()
        test_list_keys(user_id)
        test_validation(user_id, test_keys)
        test_update_key(user_id)
        test_delete_key(user_id)
        test_supported_services()
        test_encryption_decryption()

        # Cleanup
        cleanup(user_id, test_keys)

        # Summary
        print("\n" + "=" * 80)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 80)

    except Exception as e:
        print("\n" + "=" * 80)
        print(f"❌ TEST FAILED: {str(e)}")
        print("=" * 80)
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
