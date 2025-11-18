#!/usr/bin/env python3
"""Check for missing __init__.py files"""
from pathlib import Path

def check_init_files():
    """Check all Python package directories have __init__.py"""
    backend_dir = Path(__file__).parent
    app_dir = backend_dir / "app"

    missing = []

    # Check all directories under app/
    for dirpath in app_dir.rglob("*"):
        if dirpath.is_dir() and "__pycache__" not in str(dirpath):
            # Check if it contains .py files
            py_files = list(dirpath.glob("*.py"))
            if py_files:
                init_file = dirpath / "__init__.py"
                if not init_file.exists():
                    missing.append(str(dirpath.relative_to(backend_dir)))

    if missing:
        print("❌ Missing __init__.py files in:")
        for path in sorted(missing):
            print(f"   - {path}")
        return False
    else:
        print("✅ All Python package directories have __init__.py")
        return True

if __name__ == "__main__":
    import sys
    sys.exit(0 if check_init_files() else 1)
