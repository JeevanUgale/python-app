from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import jwt
import os
import json
from datetime import datetime
from functools import wraps
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
basedir = Path(__file__).resolve().parents[2]
load_dotenv(basedir / '.env')

db = SQLAlchemy()

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


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50))
    resource_id = db.Column(db.Integer)
    old_values = db.Column(db.JSON)
    new_values = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f"<AuditLog {self.action} {self.resource_type}:{self.resource_id}>"


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
    
    db.init_app(app)
    
    with app.app_context():
        try:
            db.create_all()
            print("✅ Admin Service: Database connected and tables created")
        except Exception as e:
            print(f"⚠️  Admin Service: Database connection failed: {e}")

    def verify_admin_token(f):
        """Decorator to verify admin JWT token"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not token:
                return jsonify({
                    'success': False,
                    'error': 'Missing authorization token',
                    'error_code': 'ADMIN_401'
                }), 401
            
            try:
                payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
                
                if not payload.get('is_admin'):
                    return jsonify({
                        'success': False,
                        'error': 'Admin privileges required',
                        'error_code': 'ADMIN_403'
                    }), 403
                
                request.admin_id = payload.get('admin_id')
                request.admin_username = payload.get('username')
                return f(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                return jsonify({
                    'success': False,
                    'error': 'Token has expired',
                    'error_code': 'ADMIN_401'
                }), 401
            except jwt.InvalidTokenError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid token',
                    'error_code': 'ADMIN_401'
                }), 401
        
        return decorated_function

    def log_audit(action, resource_type, resource_id, old_values=None, new_values=None):
        """Log admin action to audit trail"""
        try:
            audit = AuditLog(
                admin_id=request.admin_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                old_values=old_values,
                new_values=new_values,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )
            db.session.add(audit)
            db.session.commit()
        except Exception as e:
            print(f"⚠️  Failed to log audit: {e}")

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'healthy', 'service': 'admin-service'}), 200

    @app.route('/api/admin/dashboard', methods=['GET'])
    @verify_admin_token
    def get_dashboard():
        """Get admin dashboard data"""
        try:
            total_users = User.query.count()
            recent_audits = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(10).all()
            
            return jsonify({
                'success': True,
                'dashboard': {
                    'total_users': total_users,
                    'recent_audits': [audit.to_dict() for audit in recent_audits]
                }
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_code': 'ADMIN_500'
            }), 500

    @app.route('/api/admin/users', methods=['GET'])
    @verify_admin_token
    def get_all_users():
        """Get all users (admin view)"""
        try:
            users = User.query.order_by(User.id.desc()).all()
            return jsonify({
                'success': True,
                'users': [user.to_dict() for user in users],
                'total': len(users)
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_code': 'ADMIN_500'
            }), 500

    @app.route('/api/admin/users/<int:user_id>', methods=['GET'])
    @verify_admin_token
    def get_user_details(user_id):
        """Get user details (admin view)"""
        try:
            user = User.query.get(user_id)
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'User not found',
                    'error_code': 'ADMIN_404'
                }), 404
            
            return jsonify({
                'success': True,
                'user': user.to_dict()
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_code': 'ADMIN_500'
            }), 500

    @app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
    @verify_admin_token
    def update_user(user_id):
        """Update user (admin only)"""
        try:
            user = User.query.get(user_id)
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'User not found',
                    'error_code': 'ADMIN_404'
                }), 404
            
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided',
                    'error_code': 'ADMIN_400'
                }), 400
            
            # Store old values for audit log
            old_values = user.to_dict()
            
            # Update fields if provided
            if 'first_name' in data:
                user.first_name = data['first_name'].strip()
            if 'last_name' in data:
                user.last_name = data['last_name'].strip()
            if 'age' in data:
                user.age = int(data['age'])
            if 'qualification' in data:
                user.qualification = (data.get('qualification') or '').strip()
            if 'address' in data:
                user.address = (data.get('address') or '').strip()
            
            db.session.commit()
            
            # Log to audit trail
            log_audit('UPDATE', 'user', user_id, old_values=old_values, new_values=user.to_dict())
            
            return jsonify({
                'success': True,
                'user': user.to_dict(),
                'message': 'User updated successfully'
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e),
                'error_code': 'ADMIN_500'
            }), 500

    @app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
    @verify_admin_token
    def delete_user(user_id):
        """Delete user (admin only)"""
        try:
            user = User.query.get(user_id)
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'User not found',
                    'error_code': 'ADMIN_404'
                }), 404
            
            # Log deletion before removing
            log_audit('DELETE', 'user', user_id, old_values=user.to_dict())
            
            db.session.delete(user)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'User deleted successfully'
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e),
                'error_code': 'ADMIN_500'
            }), 500

    @app.route('/api/admin/audit-logs', methods=['GET'])
    @verify_admin_token
    def get_audit_logs():
        """Get audit logs"""
        try:
            limit = request.args.get('limit', 100, type=int)
            offset = request.args.get('offset', 0, type=int)
            
            logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset).all()
            total = AuditLog.query.count()
            
            return jsonify({
                'success': True,
                'audit_logs': [log.to_dict() for log in logs],
                'total': total,
                'limit': limit,
                'offset': offset
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_code': 'ADMIN_500'
            }), 500

    return app


def run():
    app = create_app()
    port = int(os.environ.get('ADMIN_SERVICE_PORT', 5003))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    print(f"⚙️  Starting Admin Service on {host}:{port}")
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run()
