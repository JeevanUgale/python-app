import requests
import time


class CircuitBreaker:
    """Simple circuit breaker to prevent cascading failures"""
    
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.is_open = False
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.is_open:
            if time.time() - self.last_failure_time > self.timeout:
                self.is_open = False
                self.failures = 0
            else:
                raise Exception("Service unavailable - circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()
            if self.failures >= self.failure_threshold:
                self.is_open = True
            raise e


def retry_with_backoff(max_retries=3, base_delay=1):
    """Retry decorator with exponential backoff"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            delay = base_delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay)
                        delay *= 2
            
            raise last_exception
        return wrapper
    return decorator


class AuthServiceClient:
    """Client for Auth Service"""
    
    def __init__(self, base_url, timeout=10):
        self.base_url = base_url
        self.timeout = timeout
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)
    
    @retry_with_backoff(max_retries=3)
    def login(self, username, password):
        """Authenticate user with Auth Service"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={'username': username, 'password': password},
                headers={'Content-Type': 'application/json'},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except requests.exceptions.Timeout:
            raise Exception("Auth service timeout")
        except Exception as e:
            raise e
    
    @retry_with_backoff(max_retries=3)
    def verify_token(self, token):
        """Verify JWT token with Auth Service"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/verify",
                json={'token': token},
                headers={'Content-Type': 'application/json'},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            return None
    
    @retry_with_backoff(max_retries=3)
    def logout(self):
        """Logout user"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/logout",
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception as e:
            return False


class UserServiceClient:
    """Client for User Service"""
    
    def __init__(self, base_url, timeout=10):
        self.base_url = base_url
        self.timeout = timeout
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)
    
    @retry_with_backoff(max_retries=3)
    def get_users(self, token):
        """Get all users"""
        try:
            response = requests.get(
                f"{self.base_url}/api/users",
                headers={'Authorization': f'Bearer {token}'},
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json().get('users', [])
            return []
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    @retry_with_backoff(max_retries=3)
    def get_user(self, user_id, token):
        """Get a specific user"""
        try:
            response = requests.get(
                f"{self.base_url}/api/users/{user_id}",
                headers={'Authorization': f'Bearer {token}'},
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json().get('user')
            return None
        except Exception as e:
            print(f"Error getting user {user_id}: {e}")
            return None
    
    @retry_with_backoff(max_retries=3)
    def create_user(self, user_data):
        """Create a new user"""
        try:
            response = requests.post(
                f"{self.base_url}/api/users",
                json=user_data,
                headers={'Content-Type': 'application/json'},
                timeout=self.timeout
            )
            return response.status_code == 201
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    @retry_with_backoff(max_retries=3)
    def update_user(self, user_id, user_data, token):
        """Update a user"""
        try:
            response = requests.put(
                f"{self.base_url}/api/users/{user_id}",
                json=user_data,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                },
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error updating user {user_id}: {e}")
            return False
    
    @retry_with_backoff(max_retries=3)
    def delete_user(self, user_id, token):
        """Delete a user"""
        try:
            response = requests.delete(
                f"{self.base_url}/api/users/{user_id}",
                headers={'Authorization': f'Bearer {token}'},
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error deleting user {user_id}: {e}")
            return False


class AdminServiceClient:
    """Client for Admin Service"""
    
    def __init__(self, base_url, timeout=10):
        self.base_url = base_url
        self.timeout = timeout
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)
    
    @retry_with_backoff(max_retries=3)
    def get_dashboard(self, token):
        """Get admin dashboard"""
        try:
            response = requests.get(
                f"{self.base_url}/api/admin/dashboard",
                headers={'Authorization': f'Bearer {token}'},
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json().get('dashboard')
            return None
        except Exception as e:
            print(f"Error getting dashboard: {e}")
            return None
    
    @retry_with_backoff(max_retries=3)
    def get_all_users(self, token):
        """Get all users (admin view)"""
        try:
            response = requests.get(
                f"{self.base_url}/api/admin/users",
                headers={'Authorization': f'Bearer {token}'},
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json().get('users', [])
            return []
        except Exception as e:
            print(f"Error getting admin users: {e}")
            return []
    
    @retry_with_backoff(max_retries=3)
    def delete_user(self, user_id, token):
        """Delete user (admin only)"""
        try:
            response = requests.delete(
                f"{self.base_url}/api/admin/users/{user_id}",
                headers={'Authorization': f'Bearer {token}'},
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error deleting user {user_id}: {e}")
            return False
