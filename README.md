# Python Microservices Application

This application has been refactored from a monolithic Flask application into a microservices architecture. The application manages user data with CRUD operations, split across multiple independent services.

## Architecture Overview

```
┌─────────────────┐    HTTP API    ┌─────────────────┐
│  Web Frontend   │ ──────────────▶ │  User Service   │
│    (Port 5000)  │                 │   (Port 5001)   │
│                 │                 │                 │
│ - Templates     │                 │ - REST API      │
│ - Forms         │                 │ - Database      │
│ - User Interface│                 │ - User CRUD     │
└─────────────────┘                 └─────────────────┘
```

## Services

### 1. User Service (Port 5001)
- **Purpose**: Handles all user data operations
- **Technology**: Flask REST API + SQLAlchemy
- **Database**: MySQL
- **Endpoints**:
  - `GET /health` - Health check
  - `GET /api/users` - List all users
  - `GET /api/users/{id}` - Get specific user
  - `POST /api/users` - Create new user
  - `PUT /api/users/{id}` - Update user
  - `DELETE /api/users/{id}` - Delete user

### 2. Web Frontend Service (Port 5000)
- **Purpose**: Provides web interface and user interaction
- **Technology**: Flask + WTForms + Bootstrap
- **Communication**: HTTP requests to User Service
- **Features**:
  - User forms (create/edit)
  - User listing with actions
  - Flash messages and validation
  - Responsive UI

### 3. Shared Components
- **Configuration management**: Centralized config classes
- **Utilities**: Health checks, retry mechanisms, API response formats
- **Common patterns**: Error handling, service communication

## Setup and Installation

### Database Setup

```sql
CREATE DATABASE users_db;
CREATE USER 'flaskuser'@'%' IDENTIFIED BY 'flask_password';
GRANT ALL PRIVILEGES ON users_db.* TO 'flaskuser'@'%';
FLUSH PRIVILEGES;
```

### Prerequisites (Install required packages)
- Python 3.8+
- MySQL Database/mysql-client
- pip package manager
- Systemd for service management

````bash
sudo apt udpdate
sudo apt install python3-venv python3-pip mysql-client -y
````

### 1. Environment Setup
```bash
# Clone or navigate to the project directory
cd /path/to/python-app

# Copy environment configuration
cp .env.example .env

# Edit .env with your database credentials and settings
vim .env
```

### 2. Install Dependencies
```bash
# Install all dependencies
pip install -r requirements.txt

# Or install service-specific dependencies
pip install -r services/user_service/requirements.txt
pip install -r services/web_frontend/requirements.txt
```

## Running the Application

### Start Services Individually

**Terminal 1 - User Service:**
```bash
sudo cp deployment/user-service.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable user-service
sudo systemctl start user-service
```

**Terminal 2 - Web Frontend:**
```bash
sudo cp deployment/web-frontend.service /etc/systemd/system/
sudo systemctl enbale web-frontend
sudo systemctl start web-frontend
```

## Service Management

### Health Checks
```bash
./scripts/health_check.sh
```

### Individual Service URLs
- **Web Frontend**: http://localhost:5000
- **User Service API**: http://localhost:5001
- **Health Checks**: 
  - http://localhost:5000/health
  - http://localhost:5001/health

## Configuration

### Environment Variables (.env)
```bash
# Database Configuration
DB_USER=flaskuser
DB_PASS=flask_password
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=users_db

# Application Configuration
SECRET_KEY=your-secret-key-here
DEBUG=False

# Service Ports
USER_SERVICE_PORT=5001
WEB_FRONTEND_PORT=5000

# Service URLs
USER_SERVICE_URL=http://localhost:5001

# General Configuration
HOST=0.0.0.0
```

# View logs
````bash
sudo journalctl -u user-service -f
sudo journalctl -u web-frontend -f
````

### 6. Nginx Configuration (Optional)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Monitoring and Maintenance

### Log Files
- Application logs: Check service outputs via `journalctl`
- Nginx logs: `/var/log/nginx/access.log` and `/var/log/nginx/error.log`
- System logs: `/var/log/syslog`

### Health Monitoring
```bash
# Check service health
curl http://localhost:5000/health
curl http://localhost:5001/health

# Monitor system resources
htop
df -h
free -h
```

### Backup Strategy
- Database: Regular MySQL dumps
- Application: Code in version control
- Configuration: Backup `.env` and service files

## Migration from Monolithic App

The original monolithic application (`python_app/`) has been decomposed into:

1. **Database logic** → User Service
2. **Web interface** → Web Frontend Service  
3. **Shared configuration** → Shared components

### Key Changes:
- Database operations now happen via REST API calls
- Form handling moved to frontend service
- Database models isolated in User Service
- Configuration centralized in shared components
- Inter-service communication via HTTP

### Benefits:
- **Scalability**: Services can be scaled independently
- **Maintainability**: Clear separation of concerns
- **Deployment**: Services can be deployed separately
- **Technology diversity**: Different services can use different tech stacks
- **Fault isolation**: Failure in one service doesn't affect others

## API Documentation

### User Service REST API

#### GET /api/users
Returns list of all users.
```json
{
  "success": true,
  "users": [
    {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "age": 30,
      "qualification": "Engineer",
      "address": "123 Main St"
    }
  ]
}
```

#### POST /api/users
Create a new user.
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "age": 30,
  "qualification": "Engineer",
  "address": "123 Main St"
}
```

#### PUT /api/users/{id}
Update existing user (partial updates supported).

#### DELETE /api/users/{id}
Delete a user by ID.