import requests
import os
from flask import Flask, render_template, redirect, url_for, flash, request as flask_request, session
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SubmitField, HiddenField, PasswordField
from wtforms.validators import DataRequired, NumberRange, Length, Optional
from pathlib import Path
from dotenv import load_dotenv
from functools import wraps

# Load .env from project root
basedir = Path(__file__).resolve().parents[2]
load_dotenv(basedir / '.env')

# Configuration for User Service
USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL', 'http://localhost:5001')

class LoginForm(FlaskForm):
    username = StringField('Username (First Name)', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class UserForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=1, max=150)])
    qualification = StringField('Qualification')
    address = TextAreaField('Address')
    password = PasswordField('Password (Optional)', validators=[Optional(), Length(min=6, message='Password must be at least 6 characters long')])
    submit = SubmitField('Save')

class EditUserForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=1, max=150)])
    qualification = StringField('Qualification')
    address = TextAreaField('Address')
    password = PasswordField('Password (leave blank to keep current)', validators=[Optional(), Length(min=6, message='Password must be at least 6 characters long')])
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
    
    def authenticate_user(self, username, password):
        """Authenticate user with User Service"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={'username': username, 'password': password},
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None


def login_required(f):
    """Decorator to require login for certain routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


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
            
            # Only include password if it's provided
            if form.password.data and form.password.data.strip():
                user_data['password'] = form.password.data.strip()
            
            if user_service.create_user(user_data):
                flash('User saved successfully', 'success')
                # Clear the form by creating a new instance
                form = UserForm()
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
        
        form = EditUserForm()
        
        if flask_request.method == 'GET':
            # Pre-populate form with user data (except password for security)
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
            
            # Only include password if it's provided (for updates)
            if form.password.data.strip():
                user_data['password'] = form.password.data.strip()
            
            if user_service.update_user(user_id, user_data):
                flash('User updated successfully', 'success')
                # If user is editing their own profile, redirect to dashboard
                if session.get('user_id') == user_id:
                    return redirect(url_for('user_dashboard'))
                else:
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

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Login page with authentication"""
        form = LoginForm()
        
        if form.validate_on_submit():
            username = form.username.data.strip()
            password = form.password.data.strip()
            
            # Authenticate user via User Service
            auth_result = user_service.authenticate_user(username, password)
            
            if auth_result and auth_result.get('success'):
                user_data = auth_result.get('user')
                session['user_id'] = user_data['id']
                session['user_name'] = user_data['first_name']
                session['user_full_name'] = f"{user_data['first_name']} {user_data['last_name']}"
                session['is_admin'] = user_data['first_name'].lower() == 'flaskuser'
                
                if session['is_admin']:
                    flash(f'Welcome back, Administrator!', 'success')
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash(f'Welcome back, {user_data["first_name"]}!', 'success')
                    return redirect(url_for('user_dashboard'))
            else:
                flash('Invalid username or password. Please try again.', 'danger')
        
        return render_template('login.html', form=form)

    @app.route('/logout')
    def logout():
        """Logout user and clear session"""
        user_name = session.get('user_name', 'User')
        is_admin = session.get('is_admin', False)
        session.clear()
        
        if is_admin:
            flash(f'Goodbye, Administrator! You have been logged out.', 'info')
        else:
            flash(f'Goodbye, {user_name}! You have been logged out.', 'info')
        return redirect(url_for('index'))

    @app.route('/dashboard')
    @login_required
    def user_dashboard():
        """User dashboard showing personal data"""
        user_id = session.get('user_id')
        user_data = user_service.get_user(user_id)
        
        if not user_data:
            flash('Could not load your profile. Please try logging in again.', 'danger')
            return redirect(url_for('logout'))
        
        return render_template('dashboard.html', user=user_data)

    @app.route('/admin')
    @login_required
    def admin_dashboard():
        """Admin dashboard showing all users"""
        if not session.get('is_admin'):
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('user_dashboard'))
        
        users = user_service.get_users()
        delete_form = DeleteForm()
        return render_template('admin_dashboard.html', users=users, delete_form=delete_form)

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