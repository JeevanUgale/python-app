from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root
basedir = Path(__file__).resolve().parents[2]
load_dotenv(basedir / '.env')

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    qualification = db.Column(db.String(200))
    address = db.Column(db.Text)

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
        return f"<User {self.id} {self.first_name} {self.last_name}>"


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
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'healthy', 'service': 'user-service'}), 200

    @app.route('/api/users', methods=['GET'])
    def get_users():
        """Get all users"""
        try:
            users = User.query.order_by(User.id.desc()).all()
            return jsonify({
                'success': True,
                'users': [user.to_dict() for user in users]
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/users/<int:user_id>', methods=['GET'])
    def get_user(user_id):
        """Get a specific user by ID"""
        try:
            user = User.query.get(user_id)
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
            return jsonify({
                'success': True,
                'user': user.to_dict()
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/users', methods=['POST'])
    def create_user():
        """Create a new user"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            # Validate required fields
            required_fields = ['first_name', 'last_name', 'age']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }), 400
            
            user = User(
                first_name=data['first_name'].strip(),
                last_name=data['last_name'].strip(),
                age=int(data['age']),
                qualification=(data.get('qualification') or '').strip(),
                address=(data.get('address') or '').strip()
            )
            
            db.session.add(user)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'user': user.to_dict(),
                'message': 'User created successfully'
            }), 201
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': 'Invalid data type for age'
            }), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/users/<int:user_id>', methods=['PUT'])
    def update_user(user_id):
        """Update an existing user"""
        try:
            user = User.query.get(user_id)
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
            
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            # Update fields if provided
            if 'first_name' in data:
                user.first_name = data['first_name'].strip()
            if 'last_name' in data:
                user.last_name = data['last_name'].strip()
            if 'age' in data:
                user.age = int(data['age'])
            if 'qualification' in data:
                user.qualification = (data['qualification'] or '').strip()
            if 'address' in data:
                user.address = (data['address'] or '').strip()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'user': user.to_dict(),
                'message': 'User updated successfully'
            }), 200
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': 'Invalid data type for age'
            }), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/users/<int:user_id>', methods=['DELETE'])
    def delete_user(user_id):
        """Delete a user"""
        try:
            user = User.query.get(user_id)
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
            
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
                'error': str(e)
            }), 500

    return app


def run():
    app = create_app()
    port = int(os.environ.get('USER_SERVICE_PORT', 5001))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    print(f"Starting User Service on {host}:{port}")
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run()