from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
import os
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
basedir = Path(__file__).resolve().parents[2]
load_dotenv(basedir / '.env')

db = SQLAlchemy()

class AdminUser(db.Model):
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        """Hash and store password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<AdminUser {self.username}>"


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    qualification = db.Column(db.String(200))
    address = db.Column(db.Text)
    password = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'age': self.age,
            'qualification': self.qualification,
            'address': self.address
        }

    def __repr__(self):
        return f"<User {self.id} {self.first_name}>"


def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DB_USER = os.environ.get('DB_USER') or 'root'
    DB_PASS = os.environ.get('DB_PASS') or ''
    DB_HOST = os.environ.get('DB_HOST') or '127.0.0.1'
    DB_PORT = os.environ.get('DB_PORT') or '3306'
    DB_NAME = os.environ.get('DB_NAME') or 'users_db'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # JWT Configuration
    JWT_SECRET = os.environ.get('JWT_SECRET') or 'dev-jwt-secret-change-in-production'
    JWT_ALGORITHM = 'HS256'
    TOKEN_EXPIRY = int(os.environ.get('TOKEN_EXPIRY', 3600))
    
    db.init_app(app)
    
    with app.app_context():
        try:
            db.create_all()
            print("✅ Auth Service: Database connected and tables created")
            
            # Create default admin user if it doesn't exist
            admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
            admin_password_hash = os.environ.get('ADMIN_PASSWORD_HASH')
            
            if admin_password_hash and not AdminUser.query.filter_by(username=admin_username).first():
                admin_user = AdminUser(username=admin_username, password_hash=admin_password_hash)
                db.session.add(admin_user)
                db.session.commit()
                print(f"✅ Created default admin user: {admin_username}")
            
        except Exception as e:
            print(f"⚠️  Auth Service: Database connection failed: {e}")

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'healthy', 'service': 'auth-service'}), 200

    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """Authenticate user (regular user or admin)"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided',
                    'error_code': 'AUTH_001'
                }), 400
            
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
            
            if not username or not password:
                return jsonify({
                    'success': False,
                    'error': 'Username and password are required',
                    'error_code': 'AUTH_002'
                }), 400
            
            # Try regular user authentication first
            user = User.query.filter_by(first_name=username).first()
            
            if user and user.password and user.password == password:
                # Generate JWT token for regular user
                token_payload = {
                    'user_id': user.id,
                    'username': user.first_name,
                    'is_admin': False,
                    'exp': datetime.utcnow() + timedelta(seconds=TOKEN_EXPIRY),
                    'iat': datetime.utcnow()
                }
                token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
                
                return jsonify({
                    'success': True,
                    'token': token,
                    'user_id': user.id,
                    'username': user.first_name,
                    'is_admin': False,
                    'expires_in': TOKEN_EXPIRY,
                    'message': 'Login successful'
                }), 200
            
            # Try admin authentication
            admin_user = AdminUser.query.filter_by(username=username).first()
            
            if admin_user and admin_user.is_active and admin_user.check_password(password):
                # Update last login
                admin_user.last_login = datetime.utcnow()
                db.session.commit()
                
                # Generate JWT token for admin user
                token_payload = {
                    'admin_id': admin_user.id,
                    'username': admin_user.username,
                    'is_admin': True,
                    'exp': datetime.utcnow() + timedelta(seconds=TOKEN_EXPIRY),
                    'iat': datetime.utcnow()
                }
                token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
                
                return jsonify({
                    'success': True,
                    'token': token,
                    'admin_id': admin_user.id,
                    'username': admin_user.username,
                    'is_admin': True,
                    'expires_in': TOKEN_EXPIRY,
                    'message': 'Admin login successful'
                }), 200
            
            # Authentication failed
            return jsonify({
                'success': False,
                'error': 'Invalid username or password',
                'error_code': 'AUTH_003'
            }), 401
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_code': 'AUTH_500'
            }), 500

    @app.route('/api/auth/verify', methods=['POST'])
    def verify_token():
        """Verify JWT token validity"""
        try:
            data = request.get_json()
            token = data.get('token') if data else None
            
            if not token:
                return jsonify({
                    'success': False,
                    'error': 'Token not provided',
                    'error_code': 'AUTH_401'
                }), 401
            
            try:
                payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
                return jsonify({
                    'success': True,
                    'payload': payload,
                    'message': 'Token is valid'
                }), 200
            except jwt.ExpiredSignatureError:
                return jsonify({
                    'success': False,
                    'error': 'Token has expired',
                    'error_code': 'AUTH_401'
                }), 401
            except jwt.InvalidTokenError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid token',
                    'error_code': 'AUTH_401'
                }), 401
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_code': 'AUTH_500'
            }), 500

    @app.route('/api/auth/logout', methods=['POST'])
    def logout():
        """Logout user (token invalidation would happen on client side)"""
        try:
            return jsonify({
                'success': True,
                'message': 'Logout successful'
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_code': 'AUTH_500'
            }), 500

    return app


def run():
    app = create_app()
    port = int(os.environ.get('AUTH_SERVICE_PORT', 5001))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    print(f"🔐 Starting Auth Service on {host}:{port}")
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run()
