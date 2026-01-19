import os
from flask import Flask, render_template, redirect, url_for, flash, request as flask_request, session
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SubmitField, HiddenField, PasswordField
from wtforms.validators import DataRequired, NumberRange, Length, Optional
from pathlib import Path
from dotenv import load_dotenv
from functools import wraps
from clients.service_clients import AuthServiceClient, UserServiceClient, AdminServiceClient

# Load .env from project root
basedir = Path(__file__).resolve().parents[2]
load_dotenv(basedir / '.env')

# Configuration for Services
AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL', 'http://localhost:5001')
USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL', 'http://localhost:5002')
ADMIN_SERVICE_URL = os.environ.get('ADMIN_SERVICE_URL', 'http://localhost:5003')
REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', 10))

# Initialize service clients
auth_service = AuthServiceClient(AUTH_SERVICE_URL, timeout=REQUEST_TIMEOUT)
user_service = UserServiceClient(USER_SERVICE_URL, timeout=REQUEST_TIMEOUT)
admin_service = AdminServiceClient(ADMIN_SERVICE_URL, timeout=REQUEST_TIMEOUT)

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


def login_required(f):
    """Decorator to require login for certain routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin login for certain routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'token' not in session or not session.get('is_admin'):
            flash('Admin privileges required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key'

    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return {
            'status': 'healthy',
            'service': 'web-frontend',
            'services': {
                'auth_service': AUTH_SERVICE_URL,
                'user_service': USER_SERVICE_URL,
                'admin_service': ADMIN_SERVICE_URL
            }
        }, 200

    @app.route('/', methods=['GET', 'POST'])
    def index():
        """Home page - show signup form"""
        form = UserForm()
        if form.validate_on_submit():
            user_data = {
                'first_name': form.first_name.data.strip(),
                'last_name': form.last_name.data.strip(),
                'age': form.age.data,
                'qualification': (form.qualification.data or '').strip(),
                'address': (form.address.data or '').strip(),
            }
            
            # Only include password if provided
            if form.password.data and form.password.data.strip():
                user_data['password'] = form.password.data.strip()
            
            if user_service.create_user(user_data):
                flash('User registered successfully! Please log in.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Error registering user. Please try again.', 'danger')
        
        return render_template('index.html', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Login page"""
        form = LoginForm()
        if form.validate_on_submit():
            username = form.username.data.strip()
            password = form.password.data.strip()
            
            try:
                result = auth_service.login(username, password)
                
                if result and result.get('success'):
                    # Store token and user info in session
                    session['token'] = result['token']
                    session['user_id'] = result.get('user_id') or result.get('admin_id')
                    session['username'] = result.get('username')
                    session['is_admin'] = result.get('is_admin', False)
                    
                    flash(f'Welcome {username}!', 'success')
                    
                    if session.get('is_admin'):
                        return redirect(url_for('admin_dashboard'))
                    else:
                        return redirect(url_for('dashboard'))
                else:
                    flash('Invalid username or password', 'danger')
            except Exception as e:
                flash(f'Login failed: {str(e)}', 'danger')
        
        return render_template('login.html', form=form)

    @app.route('/logout', methods=['GET'])
    def logout():
        """Logout user"""
        session.clear()
        flash('You have been logged out.', 'success')
        return redirect(url_for('login'))

    @app.route('/dashboard', methods=['GET'])
    @login_required
    def dashboard():
        """User dashboard"""
        if session.get('is_admin'):
            return redirect(url_for('admin_dashboard'))
        
        token = session.get('token')
        user_id = session.get('user_id')
        
        user = user_service.get_user(user_id, token)
        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('logout'))
        
        return render_template('dashboard.html', user=user)

    @app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_user(user_id):
        """Edit user profile"""
        token = session.get('token')
        user = user_service.get_user(user_id, token)
        
        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('dashboard'))
        
        form = EditUserForm()
        if form.validate_on_submit():
            user_data = {
                'first_name': form.first_name.data.strip(),
                'last_name': form.last_name.data.strip(),
                'age': form.age.data,
                'qualification': (form.qualification.data or '').strip(),
                'address': (form.address.data or '').strip(),
            }
            
            if form.password.data and form.password.data.strip():
                user_data['password'] = form.password.data.strip()
            
            if user_service.update_user(user_id, user_data, token):
                flash('User updated successfully', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Error updating user', 'danger')
        elif flask_request.method == 'GET':
            form.first_name.data = user['first_name']
            form.last_name.data = user['last_name']
            form.age.data = user['age']
            form.qualification.data = user.get('qualification', '')
            form.address.data = user.get('address', '')
        
        return render_template('edit.html', form=form, user=user, user_id=user_id)

    @app.route('/admin/dashboard', methods=['GET'])
    @admin_required
    def admin_dashboard():
        """Admin dashboard"""
        token = session.get('token')
        
        dashboard_data = admin_service.get_dashboard(token)
        users = admin_service.get_all_users(token)
        
        return render_template('admin_dashboard.html', 
                             dashboard=dashboard_data or {}, 
                             users=users or [])

    @app.route('/admin/users', methods=['GET'])
    @admin_required
    def admin_users():
        """Admin user management"""
        token = session.get('token')
        users = admin_service.get_all_users(token)
        
        return render_template('admin_dashboard.html', users=users or [])

    @app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
    @admin_required
    def admin_delete_user(user_id):
        """Delete user (admin only)"""
        token = session.get('token')
        
        if admin_service.delete_user(user_id, token):
            flash('User deleted successfully', 'success')
        else:
            flash('Error deleting user', 'danger')
        
        return redirect(url_for('admin_dashboard'))

    return app


def run():
    app = create_app()
    port = int(os.environ.get('WEB_FRONTEND_PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    print(f"🌐 Starting Web Frontend on {host}:{port}")
    print(f"Auth Service URL: {AUTH_SERVICE_URL}")
    print(f"User Service URL: {USER_SERVICE_URL}")
    print(f"Admin Service URL: {ADMIN_SERVICE_URL}")
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run()