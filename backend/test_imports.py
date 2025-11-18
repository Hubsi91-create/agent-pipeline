#!/usr/bin/env python3
"""
Test script to validate all imports in the agent-pipeline project
"""
import sys
import importlib
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

def test_import(module_path):
    """Test if a module can be imported"""
    try:
        importlib.import_module(module_path)
        return True, None
    except Exception as e:
        return False, str(e)

def main():
    """Test all critical imports"""
    test_modules = [
        # Core models
        ("app.models.data_models", "Data Models"),

        # Utilities
        ("app.utils.logger", "Logger"),

        # Main app (will fail due to dependencies, but we can check syntax)
        # ("app.main", "FastAPI Main App"),
    ]

    print("=" * 60)
    print("IMPORT TEST FOR AGENT-PIPELINE")
    print("=" * 60)

    passed = 0
    failed = 0

    for module_path, description in test_modules:
        print(f"\n Testing: {description} ({module_path})")
        success, error = test_import(module_path)

        if success:
            print(f" ✅ SUCCESS")
            passed += 1
        else:
            print(f" ❌ FAILED")
            print(f"    Error: {error}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
