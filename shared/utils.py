"""Common utilities and helper functions for microservices"""
import json
import logging
import requests
import time
from datetime import datetime
from functools import wraps

from flask import g, request
from prometheus_client import Counter, CONTENT_TYPE_LATEST, Histogram, generate_latest


def retry_on_failure(max_retries=3, delay=1):
    """Decorator to retry function calls on failure"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(delay * (2 ** attempt))  # Exponential backoff
            return None
        return wrapper
    return decorator


class ServiceHealthChecker:
    """Utility class to check health of services"""
    
    @staticmethod
    @retry_on_failure(max_retries=2, delay=0.5)
    def check_service_health(service_url, timeout=10):
        """Check if a service is healthy"""
        try:
            response = requests.get(f"{service_url}/health", timeout=timeout)
            return response.status_code == 200
        except:
            return False
    
    @staticmethod
    def get_service_status(services):
        """Get status of multiple services"""
        status = {}
        for service_name, service_url in services.items():
            status[service_name] = 'healthy' if ServiceHealthChecker.check_service_health(service_url) else 'unhealthy'
        return status


class APIResponse:
    """Standard API response format"""
    
    @staticmethod
    def success(data=None, message=None, status_code=200):
        response = {'success': True}
        if data is not None:
            response['data'] = data
        if message:
            response['message'] = message
        return response, status_code
    
    @staticmethod
    def error(message, status_code=400, error_code=None):
        response = {
            'success': False,
            'error': message
        }
        if error_code:
            response['error_code'] = error_code
        return response, status_code


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logs."""

    def __init__(self, service_name=None):
        super().__init__()
        self.service_name = service_name

    def format(self, record):
        log_record = {
            'ts': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'service': self.service_name,
            'message': record.getMessage(),
        }

        if record.exc_info:
            log_record['exc_info'] = self.formatException(record.exc_info)

        return json.dumps(log_record)


def setup_json_logging(service_name: str, level=logging.INFO):
    """Configure structured JSON logging to stdout."""
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter(service_name))

    logger = logging.getLogger()
    logger.setLevel(level)
    # Replace handlers to avoid duplicated log lines (e.g., when reloading).
    logger.handlers = [handler]


REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['service', 'endpoint', 'method', 'http_status'],
)

REQUEST_LATENCY = Histogram(
    'http_request_latency_seconds',
    'HTTP request latency in seconds',
    ['service', 'endpoint', 'method'],
)


def setup_prometheus(app, service_name: str):
    """Attach Prometheus metrics endpoint and request instrumentation."""
    setup_json_logging(service_name)

    @app.before_request
    def _start_timer():
        g._request_start_time = time.time()

    @app.after_request
    def _record_metrics(response):
        try:
            endpoint = request.endpoint or 'unknown'
            method = request.method
            status = response.status_code
            latency = time.time() - getattr(g, '_request_start_time', time.time())

            REQUEST_COUNT.labels(
                service=service_name,
                endpoint=endpoint,
                method=method,
                http_status=status,
            ).inc()
            REQUEST_LATENCY.labels(
                service=service_name,
                endpoint=endpoint,
                method=method,
            ).observe(latency)
        except Exception:
            pass
        return response

    @app.route('/metrics')
    def metrics():
        return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}