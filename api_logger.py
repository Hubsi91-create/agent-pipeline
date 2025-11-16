"""
API Logger - Production-Grade Request/Response Logging
=======================================================
Comprehensive logging system for all API calls with request tracking,
performance metrics, and structured logging.

Features:
- Automatic request/response logging middleware
- Request ID tracking for distributed tracing
- Performance metrics (response time, payload size)
- Structured JSON logging format
- Error tracking and exception logging
- Log rotation and file handling
- Environment-specific configurations

Author: Music Video Production System
Version: 1.0.0
"""

import logging
import json
import time
import uuid
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps
from flask import request, g, Response
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os


# ============================================================
# LOGGING CONFIGURATION
# ============================================================

class ProductionLogger:
    """
    Production-grade logging configuration with multiple handlers.

    Supports:
    - Console output (colorized for development)
    - File output with rotation
    - JSON structured logging
    - Multiple log levels per handler
    """

    def __init__(
        self,
        name: str = 'api',
        log_dir: str = './logs',
        log_level: str = 'INFO',
        enable_console: bool = True,
        enable_file: bool = True,
        enable_json: bool = True
    ):
        """
        Initialize production logger.

        Args:
            name: Logger name
            log_dir: Directory for log files
            log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            enable_console: Enable console output
            enable_file: Enable file output
            enable_json: Enable JSON structured logging
        """
        self.name = name
        self.log_dir = log_dir
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)

        # Create logs directory
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Initialize logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_level)

        # Remove existing handlers
        self.logger.handlers = []

        # Add handlers
        if enable_console:
            self._add_console_handler()

        if enable_file:
            self._add_file_handler()

        if enable_json:
            self._add_json_handler()

    def _add_console_handler(self):
        """Add colorized console handler"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)

        # Production-friendly format (no colors in prod)
        console_format = logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)

    def _add_file_handler(self):
        """Add rotating file handler"""
        log_file = os.path.join(self.log_dir, f'{self.name}.log')

        # Rotate after 10MB, keep 10 backups
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=10
        )

        file_handler.setLevel(self.log_level)

        file_format = logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)

    def _add_json_handler(self):
        """Add JSON structured logging handler"""
        json_file = os.path.join(self.log_dir, f'{self.name}_structured.jsonl')

        # Rotate daily, keep 30 days
        json_handler = TimedRotatingFileHandler(
            json_file,
            when='midnight',
            interval=1,
            backupCount=30
        )

        json_handler.setLevel(self.log_level)
        json_handler.setFormatter(JSONFormatter())
        self.logger.addHandler(json_handler)

    def get_logger(self) -> logging.Logger:
        """Get configured logger instance"""
        return self.logger


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        # Add extra fields from record
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id

        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id

        if hasattr(record, 'endpoint'):
            log_data['endpoint'] = record.endpoint

        if hasattr(record, 'method'):
            log_data['method'] = record.method

        if hasattr(record, 'status_code'):
            log_data['status_code'] = record.status_code

        if hasattr(record, 'response_time_ms'):
            log_data['response_time_ms'] = record.response_time_ms

        return json.dumps(log_data)


# ============================================================
# REQUEST/RESPONSE LOGGING MIDDLEWARE
# ============================================================

class APIRequestLogger:
    """
    Flask middleware for automatic API request/response logging.

    Logs:
    - Request: Method, path, query params, headers, body
    - Response: Status code, response time, payload size
    - Performance: Request duration, slow request warnings
    - Errors: Exception details, stack traces
    """

    def __init__(
        self,
        app=None,
        logger: Optional[logging.Logger] = None,
        slow_request_threshold_ms: int = 1000,
        log_request_body: bool = True,
        log_response_body: bool = False,
        exclude_paths: list = None
    ):
        """
        Initialize API request logger.

        Args:
            app: Flask application instance
            logger: Logger instance (creates new if None)
            slow_request_threshold_ms: Threshold for slow request warnings
            log_request_body: Whether to log request bodies
            log_response_body: Whether to log response bodies
            exclude_paths: Paths to exclude from logging (e.g., /health)
        """
        self.logger = logger or logging.getLogger('api.requests')
        self.slow_threshold = slow_request_threshold_ms
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.exclude_paths = exclude_paths or ['/health', '/favicon.ico']

        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize Flask app with logging middleware"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_request(self.teardown_request)

    def before_request(self):
        """Log request details before processing"""
        # Skip excluded paths
        if request.path in self.exclude_paths:
            return

        # Generate unique request ID
        request_id = str(uuid.uuid4())
        g.request_id = request_id
        g.start_time = time.time()

        # Build request log data
        log_data = {
            'request_id': request_id,
            'method': request.method,
            'path': request.path,
            'endpoint': request.endpoint or 'unknown',
            'remote_addr': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'unknown')
        }

        # Add query parameters
        if request.args:
            log_data['query_params'] = dict(request.args)

        # Add request body (sanitized)
        if self.log_request_body and request.is_json:
            try:
                body = request.get_json()
                # Sanitize sensitive fields
                body = self._sanitize_data(body)
                log_data['request_body'] = body
            except Exception:
                log_data['request_body'] = '[Invalid JSON]'

        # Log request
        self.logger.info(
            f"API Request: {request.method} {request.path}",
            extra=log_data
        )

    def after_request(self, response: Response) -> Response:
        """Log response details after processing"""
        # Skip excluded paths
        if request.path in self.exclude_paths:
            return response

        # Calculate response time
        response_time = None
        if hasattr(g, 'start_time'):
            response_time = (time.time() - g.start_time) * 1000  # Convert to ms

        # Build response log data
        log_data = {
            'request_id': getattr(g, 'request_id', 'unknown'),
            'method': request.method,
            'path': request.path,
            'endpoint': request.endpoint or 'unknown',
            'status_code': response.status_code,
            'response_time_ms': round(response_time, 2) if response_time else None,
            'content_length': response.content_length
        }

        # Add response body if enabled
        if self.log_response_body and response.is_json:
            try:
                body = response.get_json()
                log_data['response_body'] = body
            except Exception:
                pass

        # Determine log level based on status code and response time
        if response.status_code >= 500:
            log_level = logging.ERROR
            log_msg = f"API Error: {request.method} {request.path} - {response.status_code}"
        elif response.status_code >= 400:
            log_level = logging.WARNING
            log_msg = f"API Client Error: {request.method} {request.path} - {response.status_code}"
        elif response_time and response_time > self.slow_threshold:
            log_level = logging.WARNING
            log_msg = f"Slow API Request: {request.method} {request.path} - {response_time:.0f}ms"
        else:
            log_level = logging.INFO
            log_msg = f"API Response: {request.method} {request.path} - {response.status_code}"

        self.logger.log(log_level, log_msg, extra=log_data)

        # Add request ID to response headers
        response.headers['X-Request-ID'] = getattr(g, 'request_id', 'unknown')

        return response

    def teardown_request(self, exception=None):
        """Log exceptions and cleanup"""
        if exception:
            log_data = {
                'request_id': getattr(g, 'request_id', 'unknown'),
                'method': request.method,
                'path': request.path,
                'endpoint': request.endpoint or 'unknown',
                'exception_type': type(exception).__name__,
                'exception_message': str(exception)
            }

            self.logger.error(
                f"API Exception: {request.method} {request.path} - {type(exception).__name__}",
                extra=log_data,
                exc_info=True
            )

    def _sanitize_data(self, data: Any) -> Any:
        """Sanitize sensitive data from logs"""
        if not isinstance(data, dict):
            return data

        sanitized = data.copy()
        sensitive_keys = [
            'password', 'secret', 'token', 'api_key', 'access_token',
            'refresh_token', 'authorization', 'credit_card', 'ssn'
        ]

        for key in sanitized:
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = '[REDACTED]'
            elif isinstance(sanitized[key], dict):
                sanitized[key] = self._sanitize_data(sanitized[key])

        return sanitized


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def get_request_id() -> str:
    """Get current request ID from Flask g object"""
    return getattr(g, 'request_id', 'unknown')


def log_api_call(endpoint: str, **kwargs):
    """
    Decorator for logging API function calls.

    Usage:
        @log_api_call('create_video')
        def create_video(data):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **func_kwargs):
            logger = logging.getLogger('api.calls')
            request_id = get_request_id()

            log_data = {
                'request_id': request_id,
                'endpoint': endpoint,
                'function': func.__name__,
                **kwargs
            }

            start_time = time.time()

            try:
                logger.info(f"Calling {endpoint}", extra=log_data)
                result = func(*args, **func_kwargs)

                duration_ms = (time.time() - start_time) * 1000
                log_data['duration_ms'] = round(duration_ms, 2)

                logger.info(f"Completed {endpoint}", extra=log_data)
                return result

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                log_data['duration_ms'] = round(duration_ms, 2)
                log_data['error'] = str(e)

                logger.error(f"Failed {endpoint}: {str(e)}", extra=log_data, exc_info=True)
                raise

        return wrapper
    return decorator


# ============================================================
# GLOBAL LOGGER INSTANCES
# ============================================================

# Initialize production loggers
_loggers = {}


def get_production_logger(
    name: str = 'api',
    log_level: str = None,
    **kwargs
) -> logging.Logger:
    """
    Get or create a production logger instance.

    Args:
        name: Logger name
        log_level: Override log level (uses env var or INFO)
        **kwargs: Additional ProductionLogger arguments

    Returns:
        Configured logger instance
    """
    if name not in _loggers:
        # Get log level from environment or use default
        log_level = log_level or os.getenv('LOG_LEVEL', 'INFO')

        prod_logger = ProductionLogger(
            name=name,
            log_level=log_level,
            **kwargs
        )

        _loggers[name] = prod_logger.get_logger()

    return _loggers[name]


def initialize_api_logging(
    app,
    log_level: str = None,
    slow_request_threshold_ms: int = 1000,
    **kwargs
):
    """
    Initialize comprehensive API logging for Flask app.

    Args:
        app: Flask application instance
        log_level: Log level (DEBUG, INFO, WARNING, ERROR)
        slow_request_threshold_ms: Threshold for slow request warnings
        **kwargs: Additional APIRequestLogger arguments

    Returns:
        Tuple of (logger, request_logger)
    """
    # Initialize production logger
    logger = get_production_logger('api', log_level=log_level)

    # Initialize request logging middleware
    request_logger = APIRequestLogger(
        app=app,
        logger=logger,
        slow_request_threshold_ms=slow_request_threshold_ms,
        **kwargs
    )

    logger.info("API logging initialized successfully")
    logger.info(f"Log level: {log_level or os.getenv('LOG_LEVEL', 'INFO')}")
    logger.info(f"Slow request threshold: {slow_request_threshold_ms}ms")

    return logger, request_logger
