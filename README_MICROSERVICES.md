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

### Prerequisites
- Python 3.8+
- MySQL Database
- pip package manager

### 1. Environment Setup
```bash
# Clone or navigate to the project directory
cd /path/to/python-app

# Copy environment configuration
cp .env.example .env

# Edit .env with your database credentials and settings
nano .env
```

### 2. Database Setup
Ensure MySQL is running and create the database:
```sql
CREATE DATABASE users_db;
CREATE USER 'flaskuser'@'localhost' IDENTIFIED BY 'flask_password';
GRANT ALL PRIVILEGES ON users_db.* TO 'flaskuser'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Install Dependencies
```bash
# Install all dependencies
pip install -r requirements.txt

# Or install service-specific dependencies
pip install -r services/user_service/requirements.txt
pip install -r services/web_frontend/requirements.txt
```

## Running the Application

### Option 1: Start All Services Together
```bash
./scripts/start_all_services.sh
```

### Option 2: Start Services Individually

**Terminal 1 - User Service:**
```bash
./scripts/start_user_service.sh
```

**Terminal 2 - Web Frontend:**
```bash
./scripts/start_web_frontend.sh
```

### Option 3: Manual Start (Development)
```bash
# Start User Service
cd services/user_service
python app.py

# Start Web Frontend (in another terminal)
cd services/web_frontend
python app.py
```

## Service Management

### Health Checks
```bash
./scripts/health_check.sh
```

### Stop All Services
```bash
./scripts/stop_all_services.sh
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

## Deployment on EC2

### System Requirements
- Ubuntu/Amazon Linux EC2 instance
- Python 3.8+
- MySQL/MariaDB
- Nginx (recommended for production)
- Systemd for service management

### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv mysql-client -y


### 2. Application Deployment
```bash
# Clone application
git clone <your-repo>
cd /home/ubuntu/python-app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with production settings
```

### 3. Database Setup
```bash
sudo mysql -u root -p
```
```sql
CREATE DATABASE users_db;
CREATE USER 'flaskuser'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON users_db.* TO 'flaskuser'@'localhost';
FLUSH PRIVILEGES;
```

### 4. Systemd Service Files

**User Service (/etc/systemd/system/user-service.service):**
```ini
[Unit]
Description=User Service
After=network.target mysql.service

[Service]
Type=simple
User=flaskapp
WorkingDirectory=/home/flaskapp/python-app
Environment=PATH=/home/flaskapp/python-app/venv/bin
ExecStart=/home/flaskapp/python-app/venv/bin/python services/user_service/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Web Frontend Service (/etc/systemd/system/web-frontend.service):**
```ini
[Unit]
Description=Web Frontend Service
After=network.target user-service.service

[Service]
Type=simple
User=flaskapp
WorkingDirectory=/home/flaskapp/python-app
Environment=PATH=/home/flaskapp/python-app/venv/bin
ExecStart=/home/flaskapp/python-app/venv/bin/python services/web_frontend/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 5. Service Management
```bash
# Enable and start services
sudo systemctl enable user-service web-frontend
sudo systemctl start user-service web-frontend

# Check status
sudo systemctl status user-service web-frontend

# View logs
sudo journalctl -u user-service -f
sudo journalctl -u web-frontend -f
```

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

## Troubleshooting

### Common Issues

1. **Service won't start**
   - Check database connectivity
   - Verify `.env` configuration
   - Check port availability: `lsof -i :5000` or `lsof -i :5001`

2. **Database connection errors**
   - Verify MySQL is running: `sudo systemctl status mysql`
   - Check credentials in `.env`
   - Test connection: `mysql -u flaskuser -p users_db`

3. **Service communication errors**
   - Check if User Service is running
   - Verify USER_SERVICE_URL in `.env`
   - Check firewall rules

4. **Permission errors**
   - Ensure correct file ownership: `chown -R flaskapp:flaskapp /home/flaskapp/python-app`
   - Check script permissions: `chmod +x scripts/*.sh`

### Debugging Commands
```bash
# Check running processes
ps aux | grep python

# Check port usage
netstat -tlnp | grep :5000
netstat -tlnp | grep :5001

# Test API endpoints
curl -X GET http://localhost:5001/api/users
curl -X POST http://localhost:5001/api/users -H "Content-Type: application/json" -d '{"first_name":"Test","last_name":"User","age":25}'
```