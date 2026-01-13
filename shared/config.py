import os
from dotenv import load_dotenv
from pathlib import Path

class BaseConfig:
    """Base configuration class with common settings"""
    
    def __init__(self):
        # Load .env from project root
        self.basedir = Path(__file__).resolve().parents[1]
        load_dotenv(self.basedir / '.env')
    
    @property
    def SECRET_KEY(self):
        return os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    @property
    def DB_USER(self):
        return os.environ.get('DB_USER') or 'root'
    
    @property
    def DB_PASS(self):
        return os.environ.get('DB_PASS') or ''
    
    @property
    def DB_HOST(self):
        return os.environ.get('DB_HOST') or '127.0.0.1'
    
    @property
    def DB_PORT(self):
        return os.environ.get('DB_PORT') or '3306'
    
    @property
    def DB_NAME(self):
        return os.environ.get('DB_NAME') or 'users_db'
    
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def SQLALCHEMY_TRACK_MODIFICATIONS(self):
        return False
    
    @property
    def DEBUG(self):
        return os.environ.get('DEBUG', 'False').lower() == 'true'
    
    @property
    def ENVIRONMENT(self):
        return os.environ.get('ENVIRONMENT', 'development')
    
    @property
    def LOG_LEVEL(self):
        return os.environ.get('LOG_LEVEL', 'INFO')


class AuthServiceConfig(BaseConfig):
    """Configuration specific to Auth Service"""
    
    @property
    def PORT(self):
        return int(os.environ.get('AUTH_SERVICE_PORT', 5001))
    
    @property
    def HOST(self):
        return os.environ.get('HOST', '0.0.0.0')
    
    @property
    def JWT_SECRET(self):
        return os.environ.get('JWT_SECRET') or 'dev-jwt-secret-change-in-production'
    
    @property
    def JWT_ALGORITHM(self):
        return 'HS256'
    
    @property
    def TOKEN_EXPIRY(self):
        return int(os.environ.get('TOKEN_EXPIRY', 3600))
    
    @property
    def ADMIN_USERNAME(self):
        return os.environ.get('ADMIN_USERNAME', 'admin')
    
    @property
    def ADMIN_PASSWORD_HASH(self):
        return os.environ.get('ADMIN_PASSWORD_HASH') or 'dev-admin-password-hash'


class UserServiceConfig(BaseConfig):
    """Configuration specific to User Service"""
    
    @property
    def PORT(self):
        return int(os.environ.get('USER_SERVICE_PORT', 5002))
    
    @property
    def HOST(self):
        return os.environ.get('HOST', '0.0.0.0')
    
    @property
    def AUTH_SERVICE_URL(self):
        return os.environ.get('AUTH_SERVICE_URL', 'http://localhost:5001')
    
    @property
    def REQUEST_TIMEOUT(self):
        return int(os.environ.get('REQUEST_TIMEOUT', 10))


class AdminServiceConfig(BaseConfig):
    """Configuration specific to Admin Service"""
    
    @property
    def PORT(self):
        return int(os.environ.get('ADMIN_SERVICE_PORT', 5003))
    
    @property
    def HOST(self):
        return os.environ.get('HOST', '0.0.0.0')
    
    @property
    def AUTH_SERVICE_URL(self):
        return os.environ.get('AUTH_SERVICE_URL', 'http://localhost:5001')
    
    @property
    def REQUEST_TIMEOUT(self):
        return int(os.environ.get('REQUEST_TIMEOUT', 10))


class WebFrontendConfig(BaseConfig):
    """Configuration specific to Web Frontend Service"""
    
    @property
    def PORT(self):
        return int(os.environ.get('WEB_FRONTEND_PORT', 5000))
    
    @property
    def HOST(self):
        return os.environ.get('HOST', '0.0.0.0')
    
    @property
    def AUTH_SERVICE_URL(self):
        return os.environ.get('AUTH_SERVICE_URL', 'http://localhost:5001')
    
    @property
    def USER_SERVICE_URL(self):
        return os.environ.get('USER_SERVICE_URL', 'http://localhost:5002')
    
    @property
    def ADMIN_SERVICE_URL(self):
        return os.environ.get('ADMIN_SERVICE_URL', 'http://localhost:5003')
    
    @property
    def REQUEST_TIMEOUT(self):
        return int(os.environ.get('REQUEST_TIMEOUT', 10))