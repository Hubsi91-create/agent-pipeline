"""
API Logging Test Script
========================
Tests the production logging system with sample API calls.

Run this script to verify logging functionality:
- Request/response logging
- Performance metrics
- Error logging
- JSON structured logs

Usage:
    python test_api_logging.py
"""

import requests
import time
import json
from datetime import datetime


BASE_URL = 'http://localhost:5000'


def print_section(title: str):
    """Print section header"""
    print("\n" + "=" * 60)
    print(f"{title}")
    print("=" * 60)


def test_basic_request():
    """Test 1: Basic API request logging"""
    print_section("TEST 1: Basic API Request")

    url = f"{BASE_URL}/api/dashboard/overview"

    print(f"\nGET {url}")
    response = requests.get(url)

    print(f"Status: {response.status_code}")
    print(f"Request ID: {response.headers.get('X-Request-ID')}")
    print("[OK] Check logs/api.log for request/response details")


def test_with_query_params():
    """Test 2: Request with query parameters"""
    print_section("TEST 2: Request with Query Parameters")

    url = f"{BASE_URL}/api/agents/status"
    params = {
        'include_metrics': 'true',
        'limit': '10'
    }

    print(f"\nGET {url}")
    print(f"Params: {params}")

    response = requests.get(url, params=params)

    print(f"Status: {response.status_code}")
    print(f"Request ID: {response.headers.get('X-Request-ID')}")
    print("[OK] Check logs for query parameter logging")


def test_post_request():
    """Test 3: POST request with body logging"""
    print_section("TEST 3: POST Request with Body")

    url = f"{BASE_URL}/api/storyboard/video/calculate-cost"

    data = {
        'duration': 180,
        'engine': 'runway_gen3'
    }

    print(f"\nPOST {url}")
    print(f"Body: {json.dumps(data, indent=2)}")

    response = requests.post(url, json=data)

    print(f"Status: {response.status_code}")
    print(f"Request ID: {response.headers.get('X-Request-ID')}")
    print("[OK] Check logs for request body logging")


def test_slow_request():
    """Test 4: Slow request detection"""
    print_section("TEST 4: Slow Request Detection")

    url = f"{BASE_URL}/api/metrics/trends"
    params = {
        'period': '30d',
        'granularity': 'daily'
    }

    print(f"\nGET {url}")
    print("(This endpoint may take longer to process)")

    start_time = time.time()
    response = requests.get(url, params=params)
    duration = (time.time() - start_time) * 1000

    print(f"Status: {response.status_code}")
    print(f"Duration: {duration:.0f}ms")
    print(f"Request ID: {response.headers.get('X-Request-ID')}")

    if duration > 1000:
        print("[OK] Should trigger slow request warning in logs")
    else:
        print("[INFO] Request was fast, no slow warning expected")


def test_error_logging():
    """Test 5: Error logging (404)"""
    print_section("TEST 5: Error Logging (404)")

    url = f"{BASE_URL}/api/nonexistent/endpoint"

    print(f"\nGET {url}")
    response = requests.get(url)

    print(f"Status: {response.status_code}")
    print(f"Request ID: {response.headers.get('X-Request-ID')}")
    print("[OK] Check logs for 404 error logging")


def test_client_error():
    """Test 6: Client error logging (400)"""
    print_section("TEST 6: Client Error Logging (400)")

    url = f"{BASE_URL}/api/storyboard/video/calculate-cost"

    # Missing required fields
    data = {
        'duration': 180
        # Missing 'engine' field
    }

    print(f"\nPOST {url}")
    print(f"Body: {json.dumps(data, indent=2)}")
    print("(Missing required 'engine' field)")

    response = requests.post(url, json=data)

    print(f"Status: {response.status_code}")
    print(f"Request ID: {response.headers.get('X-Request-ID')}")
    print("[OK] Check logs for 400 client error logging")


def test_sensitive_data_sanitization():
    """Test 7: Sensitive data sanitization"""
    print_section("TEST 7: Sensitive Data Sanitization")

    url = f"{BASE_URL}/api/storyboard/api-keys"

    data = {
        'user_id': 'user_1',
        'service': 'runway',
        'api_key': 'sk-super-secret-api-key-12345'  # Should be sanitized in logs
    }

    print(f"\nPOST {url}")
    print("Body contains sensitive 'api_key' field")

    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        print(f"Request ID: {response.headers.get('X-Request-ID')}")
    except Exception as e:
        print(f"Error: {str(e)}")

    print("[OK] Check logs to verify api_key is [REDACTED]")


def test_concurrent_requests():
    """Test 8: Concurrent requests with unique IDs"""
    print_section("TEST 8: Concurrent Requests (Request ID Tracking)")

    import concurrent.futures

    def make_request(i):
        url = f"{BASE_URL}/api/dashboard/quick-stats"
        response = requests.get(url)
        return {
            'request_num': i,
            'status': response.status_code,
            'request_id': response.headers.get('X-Request-ID')
        }

    print("\nMaking 5 concurrent requests...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_request, i) for i in range(1, 6)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    print("\nResults:")
    for result in sorted(results, key=lambda x: x['request_num']):
        print(f"  Request #{result['request_num']}: {result['status']} - ID: {result['request_id'][:8]}...")

    print("[OK] Each request should have a unique Request ID in logs")


def check_log_files():
    """Check if log files were created"""
    print_section("Log Files Check")

    import os

    log_files = [
        'logs/api.log',
        'logs/api_structured.jsonl'
    ]

    print("\nChecking log files:")
    for log_file in log_files:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            print(f"  [OK] {log_file} ({size} bytes)")

            # Show last few lines
            if log_file.endswith('.log'):
                print(f"\n  Last 3 lines from {log_file}:")
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    for line in lines[-3:]:
                        print(f"    {line.rstrip()}")

            elif log_file.endswith('.jsonl'):
                print(f"\n  Last JSON log entry from {log_file}:")
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        last_log = json.loads(lines[-1])
                        print(f"    {json.dumps(last_log, indent=6)}")
        else:
            print(f"  [MISSING] {log_file}")


def run_all_tests():
    """Run all logging tests"""
    print("\n" + "=" * 60)
    print("API LOGGING TEST SUITE")
    print("=" * 60)
    print("\nMake sure the Flask server is running:")
    print("  python app.py")
    print("\nPress Enter to start tests...")
    input()

    try:
        # Test basic connectivity
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        print(f"\n[OK] Server is running at {BASE_URL}")
    except Exception as e:
        print(f"\n[ERROR] Cannot connect to server at {BASE_URL}")
        print(f"Error: {str(e)}")
        print("\nPlease start the server first: python app.py")
        return

    # Run tests
    tests = [
        test_basic_request,
        test_with_query_params,
        test_post_request,
        test_slow_request,
        test_error_logging,
        test_client_error,
        test_sensitive_data_sanitization,
        test_concurrent_requests
    ]

    for test_func in tests:
        try:
            test_func()
            time.sleep(0.5)  # Brief pause between tests
        except Exception as e:
            print(f"\n[ERROR] Test failed: {str(e)}")

    # Check log files
    check_log_files()

    # Summary
    print_section("Test Summary")
    print("\nAll tests completed!")
    print("\nLog files to review:")
    print("  1. logs/api.log - Human-readable logs")
    print("  2. logs/api_structured.jsonl - Structured JSON logs")
    print("\nWhat to look for:")
    print("  - Request/response details")
    print("  - Unique request IDs (X-Request-ID headers)")
    print("  - Response times in milliseconds")
    print("  - Slow request warnings (>1000ms)")
    print("  - Error logging (404, 400 status codes)")
    print("  - Sanitized sensitive data ([REDACTED])")
    print("  - Structured JSON format in .jsonl file")


if __name__ == '__main__':
    run_all_tests()
