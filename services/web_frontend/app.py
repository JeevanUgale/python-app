import requests
import os
from flask import Flask, render_template, redirect, url_for, flash, request as flask_request
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SubmitField, HiddenField
from wtforms.validators import DataRequired, NumberRange
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
basedir = Path(__file__).resolve().parents[2]
load_dotenv(basedir / '.env')

# Configuration for User Service
USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL', 'http://localhost:5001')

class UserForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=1, max=150)])
    qualification = StringField('Qualification')
    address = TextAreaField('Address')
    submit = SubmitField('Save')

class DeleteForm(FlaskForm):
    user_id = HiddenField()
    submit = SubmitField('Delete')

class UserServiceClient:
    """Client to communicate with User Service"""
    
    def __init__(self, base_url):
        self.base_url = base_url
    
    def get_users(self):
        """Get all users from User Service"""
        try:
            response = requests.get(f"{self.base_url}/api/users", timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data.get('users', [])
            return []
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    def get_user(self, user_id):
        """Get a specific user from User Service"""
        try:
            response = requests.get(f"{self.base_url}/api/users/{user_id}", timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data.get('user')
            return None
        except Exception as e:
            print(f"Error getting user {user_id}: {e}")
            return None
    
    def create_user(self, user_data):
        """Create a new user via User Service"""
        try:
            response = requests.post(
                f"{self.base_url}/api/users",
                json=user_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            return response.status_code == 201
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def update_user(self, user_id, user_data):
        """Update a user via User Service"""
        try:
            response = requests.put(
                f"{self.base_url}/api/users/{user_id}",
                json=user_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error updating user {user_id}: {e}")
            return False
    
    def delete_user(self, user_id):
        """Delete a user via User Service"""
        try:
            response = requests.delete(f"{self.base_url}/api/users/{user_id}", timeout=30)
            return response.status_code == 200
        except Exception as e:
            print(f"Error deleting user {user_id}: {e}")
            return False


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # Initialize User Service client
    user_service = UserServiceClient(USER_SERVICE_URL)

    @app.route('/health', methods=['GET'])
    def health_check():
        # Check if user service is healthy
        try:
            response = requests.get(f"{USER_SERVICE_URL}/health", timeout=10)
            user_service_healthy = response.status_code == 200
        except:
            user_service_healthy = False
        
        return {
            'status': 'healthy' if user_service_healthy else 'degraded',
            'service': 'web-frontend',
            'dependencies': {
                'user_service': 'healthy' if user_service_healthy else 'unhealthy'
            }
        }, 200 if user_service_healthy else 503

    @app.route('/', methods=['GET', 'POST'])
    def index():
        form = UserForm()
        if form.validate_on_submit():
            user_data = {
                'first_name': form.first_name.data.strip(),
                'last_name': form.last_name.data.strip(),
                'age': form.age.data,
                'qualification': (form.qualification.data or '').strip(),
                'address': (form.address.data or '').strip(),
            }
            
            if user_service.create_user(user_data):
                flash('User saved successfully', 'success')
                return redirect(url_for('list_users'))
            else:
                flash('Error saving user. Please try again.', 'danger')
        
        return render_template('index.html', form=form)

    @app.route('/users')
    def list_users():
        users = user_service.get_users()
        delete_form = DeleteForm()
        return render_template('list.html', users=users, delete_form=delete_form)

    @app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
    def edit_user(user_id):
        user = user_service.get_user(user_id)
        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('list_users'))
        
        form = UserForm()
        
        if flask_request.method == 'GET':
            # Pre-populate form with user data
            form.first_name.data = user['first_name']
            form.last_name.data = user['last_name']
            form.age.data = user['age']
            form.qualification.data = user.get('qualification', '')
            form.address.data = user.get('address', '')
        
        if form.validate_on_submit():
            user_data = {
                'first_name': form.first_name.data.strip(),
                'last_name': form.last_name.data.strip(),
                'age': form.age.data,
                'qualification': (form.qualification.data or '').strip(),
                'address': (form.address.data or '').strip(),
            }
            
            if user_service.update_user(user_id, user_data):
                flash('User updated successfully', 'success')
                return redirect(url_for('list_users'))
            else:
                flash('Error updating user. Please try again.', 'danger')
        
        return render_template('edit.html', form=form, user=user)

    @app.route('/users/<int:user_id>/delete', methods=['POST'])
    def delete_user(user_id):
        form = DeleteForm()
        
        # Validate CSRF
        if not form.validate_on_submit():
            flash('Invalid delete request', 'danger')
            return redirect(url_for('list_users'))
        
        if user_service.delete_user(user_id):
            flash('User deleted successfully', 'success')
        else:
            flash('Error deleting user. Please try again.', 'danger')
        
        return redirect(url_for('list_users'))

    return app


def run():
    app = create_app()
    port = int(os.environ.get('WEB_FRONTEND_PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    print(f"Starting Web Frontend on {host}:{port}")
    print(f"User Service URL: {USER_SERVICE_URL}")
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run()