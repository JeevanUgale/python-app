"""Common utilities and helper functions for microservices"""
import requests
from functools import wraps
import time


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