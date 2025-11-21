"""
System Audit Script - Forensics for Gemini Integration
This script performs a comprehensive audit to diagnose why mock data might be appearing.
"""

import sys
import shutil
import subprocess
import os
from pathlib import Path

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    try:
        # Try to set UTF-8 encoding for Windows console
        if sys.stdout.encoding != 'utf-8':
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass  # If this fails, emojis will be replaced with ?

def print_header(text):
    """Print a styled header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def check_gcloud_installation():
    """Check if gcloud is installed and in PATH"""
    print_header("1. GCLOUD INSTALLATION CHECK")

    gcloud_path = shutil.which('gcloud')
    if gcloud_path:
        print(f"✅ gcloud found in PATH: {gcloud_path}")

        # Check version
        try:
            result = subprocess.run(
                ['gcloud', '--version'],
                capture_output=True,
                text=True,
                timeout=5,
                shell=(os.name == 'nt')  # Windows needs shell=True for .CMD
            )
            print(f"\n📦 Version Info:")
            print(result.stdout)
        except Exception as e:
            print(f"❌ Could not get gcloud version: {e}")
    else:
        print("❌ gcloud NOT found in PATH")
        print("   Install: https://cloud.google.com/sdk/docs/install")
        print(f"   Current PATH: {os.environ.get('PATH', 'N/A')}")

def check_gcloud_auth():
    """Check if gcloud authentication is configured"""
    print_header("2. GCLOUD AUTHENTICATION CHECK")

    if not shutil.which('gcloud'):
        print("⚠️ Skipping auth check - gcloud not found")
        return

    # Check active account
    try:
        result = subprocess.run(
            ['gcloud', 'auth', 'list', '--filter=status:ACTIVE', '--format=value(account)'],
            capture_output=True,
            text=True,
            timeout=10,
            shell=(os.name == 'nt')
        )

        if result.returncode == 0 and result.stdout.strip():
            print(f"✅ Active account: {result.stdout.strip()}")
        else:
            print("❌ No active account found")
            print("   Run: gcloud auth login")
    except Exception as e:
        print(f"❌ Could not check auth: {e}")

    # Test access token
    print("\n🔑 Testing access token...")
    try:
        result = subprocess.run(
            ['gcloud', 'auth', 'print-access-token'],
            capture_output=True,
            text=True,
            timeout=10,
            shell=(os.name == 'nt')
        )

        if result.returncode == 0 and result.stdout.strip():
            token = result.stdout.strip()
            print(f"✅ Access token obtained ({len(token)} chars)")
            print(f"   Token preview: {token[:20]}...")
        else:
            print(f"❌ Could not get access token")
            print(f"   STDERR: {result.stderr}")
    except Exception as e:
        print(f"❌ Access token test failed: {e}")

def check_project_config():
    """Check if project is configured"""
    print_header("3. GOOGLE CLOUD PROJECT CHECK")

    if not shutil.which('gcloud'):
        print("⚠️ Skipping project check - gcloud not found")
        return

    # Check active project
    try:
        result = subprocess.run(
            ['gcloud', 'config', 'get-value', 'project'],
            capture_output=True,
            text=True,
            timeout=5,
            shell=(os.name == 'nt')
        )

        if result.returncode == 0 and result.stdout.strip():
            project = result.stdout.strip()
            print(f"✅ Active project: {project}")

            # Check if Gemini API is enabled (this might fail without permissions)
            print(f"\n🔍 Checking API access for project '{project}'...")
            test_result = subprocess.run(
                ['gcloud', 'ai', 'models', 'list', '--project', project, '--location=us-central1'],
                capture_output=True,
                text=True,
                timeout=15,
                shell=(os.name == 'nt')
            )

            if test_result.returncode == 0:
                print("✅ AI Platform API appears to be accessible")
            else:
                print("❌ AI Platform API might not be enabled")
                print(f"   Error: {test_result.stderr[:200]}")
        else:
            print("❌ No active project configured")
            print("   Run: gcloud config set project YOUR_PROJECT_ID")
    except Exception as e:
        print(f"❌ Could not check project: {e}")

def find_mock_strings():
    """Search for mock data strings in the codebase"""
    print_header("4. MOCK DATA STRING SEARCH")

    # Search patterns
    patterns = [
        ("Style 1", "Generic fallback variation pattern"),
        ("Variation 1", "Generic fallback description pattern"),
        ("mock_response", "Mock response function"),
        ("_mock_response", "Private mock response method"),
        ("fallback_variations", "Fallback variations variable")
    ]

    # Root directory to search
    backend_dir = Path(__file__).parent

    print(f"🔍 Searching in: {backend_dir}\n")

    for pattern, description in patterns:
        print(f"\n🔎 Searching for: '{pattern}' ({description})")
        found_files = []

        # Search all .py files
        for py_file in backend_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line_num, line in enumerate(lines, 1):
                        if pattern in line:
                            found_files.append((py_file, line_num, line.strip()))
            except Exception as e:
                continue

        if found_files:
            print(f"   ⚠️ Found {len(found_files)} occurrence(s):")
            for file_path, line_num, line_content in found_files:
                rel_path = file_path.relative_to(backend_dir)
                print(f"      📄 {rel_path}:{line_num}")
                print(f"         {line_content[:100]}")
        else:
            print(f"   ✅ Not found")

def check_log_file():
    """Check if debug log file exists and show recent entries"""
    print_header("5. DEBUG LOG FILE CHECK")

    log_file = Path(__file__).parent / "debug_log.txt"
    print(f"🔍 Log file location: {log_file}")

    if log_file.exists():
        print(f"✅ Log file exists ({log_file.stat().st_size} bytes)")

        # Show last 30 lines
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                recent_lines = lines[-30:] if len(lines) > 30 else lines

            print(f"\n📋 Last {len(recent_lines)} lines:")
            print("-" * 80)
            for line in recent_lines:
                print(line.rstrip())
        except Exception as e:
            print(f"❌ Could not read log file: {e}")
    else:
        print("⚠️ Log file does not exist yet")
        print("   It will be created when the application runs")

def main():
    """Run all audit checks"""
    print("\n")
    print("+" + "=" * 78 + "+")
    print("|" + " " * 20 + "SYSTEM AUDIT - GEMINI INTEGRATION" + " " * 25 + "|")
    print("+" + "=" * 78 + "+")

    check_gcloud_installation()
    check_gcloud_auth()
    check_project_config()
    find_mock_strings()
    check_log_file()

    print_header("AUDIT COMPLETE")
    print("\n💡 NEXT STEPS:")
    print("   1. If gcloud is missing: Install Google Cloud SDK")
    print("   2. If not authenticated: Run 'gcloud auth login'")
    print("   3. If no project: Run 'gcloud config set project YOUR_PROJECT_ID'")
    print("   4. If mock strings found: Review those files")
    print("   5. Run the app and check backend/debug_log.txt for detailed errors")
    print("\n")

if __name__ == "__main__":
    main()
