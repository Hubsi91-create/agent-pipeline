"""
WSGI Entrypoint for Local Backend Deployment

This file serves as the entry point for running the Flask backend locally.
It imports the Flask app instance from app.py and makes it available for
WSGI servers or direct execution.

Usage:
    python wsgi.py              # Run development server
    gunicorn wsgi:app           # Run with gunicorn
    waitress-serve --call wsgi:app  # Run with waitress (Windows)
"""

from app import app

if __name__ == "__main__":
    # Run Flask development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
