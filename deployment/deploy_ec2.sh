#!/bin/bash

# EC2 Deployment Script for Python Microservices Application
# Run this script as root on your EC2 instance

set -e

echo "==========================================="
echo "Python Microservices Deployment Script"
echo "==========================================="

# Variables
APP_USER="flaskapp"
APP_DIR="/home/$APP_USER/python-app"
SERVICE_DIR="/etc/systemd/system"
NGINX_DIR="/etc/nginx/sites-available"
DB_NAME="users_db"
DB_USER="flaskuser"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script as root (use sudo)"
    exit 1
fi

# Update system
print_status "Updating system packages..."
apt update && apt upgrade -y

# Install required packages
print_status "Installing required packages..."
apt install -y python3 python3-pip python3-venv mysql-server nginx curl git

# Create application user
print_status "Creating application user..."
if ! id "$APP_USER" &>/dev/null; then
    useradd -m -s /bin/bash $APP_USER
    print_status "User $APP_USER created"
else
    print_warning "User $APP_USER already exists"
fi

# Setup MySQL
print_status "Configuring MySQL..."
systemctl start mysql
systemctl enable mysql

# Generate random password for database user
DB_PASS=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

# Create database and user
mysql -u root <<EOF
CREATE DATABASE IF NOT EXISTS $DB_NAME;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
EOF

print_status "Database setup completed"

# Setup application directory
print_status "Setting up application directory..."
if [ ! -d "$APP_DIR" ]; then
    print_warning "Application directory not found. Please deploy your code to $APP_DIR"
    print_warning "Example: git clone <your-repo> $APP_DIR"
    mkdir -p $APP_DIR
    chown $APP_USER:$APP_USER $APP_DIR
else
    print_status "Application directory exists"
fi

# Create virtual environment and install dependencies
print_status "Setting up Python environment..."
sudo -u $APP_USER bash <<EOF
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
    echo "Dependencies installed"
else
    echo "requirements.txt not found, skipping dependency installation"
fi
EOF

# Create .env file
print_status "Creating environment configuration..."
sudo -u $APP_USER bash <<EOF
cd $APP_DIR
if [ ! -f .env ]; then
    cat > .env <<EOL
# Database Configuration
DB_USER=$DB_USER
DB_PASS=$DB_PASS
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=$DB_NAME

# Application Configuration
SECRET_KEY=\$(openssl rand -base64 32)
DEBUG=False

# Service Ports
USER_SERVICE_PORT=5001
WEB_FRONTEND_PORT=5000

# Service URLs
USER_SERVICE_URL=http://localhost:5001

# General Configuration
HOST=0.0.0.0
EOL
    echo "Environment file created with database credentials"
else
    echo ".env file already exists, skipping creation"
fi
EOF

# Install systemd service files
print_status "Installing systemd service files..."
if [ -f "$APP_DIR/deployment/user-service.service" ]; then
    cp "$APP_DIR/deployment/user-service.service" "$SERVICE_DIR/"
    cp "$APP_DIR/deployment/web-frontend.service" "$SERVICE_DIR/"
    
    systemctl daemon-reload
    systemctl enable user-service web-frontend
    print_status "Systemd services installed and enabled"
else
    print_warning "Service files not found in deployment directory"
fi

# Configure Nginx
print_status "Configuring Nginx..."
if [ -f "$APP_DIR/deployment/nginx.conf" ]; then
    cp "$APP_DIR/deployment/nginx.conf" "$NGINX_DIR/python-app"
    
    # Enable the site
    ln -sf "$NGINX_DIR/python-app" /etc/nginx/sites-enabled/
    
    # Remove default site
    rm -f /etc/nginx/sites-enabled/default
    
    # Test nginx configuration
    nginx -t
    
    systemctl enable nginx
    systemctl restart nginx
    print_status "Nginx configured and restarted"
else
    print_warning "Nginx configuration file not found"
fi

# Set correct permissions
print_status "Setting file permissions..."
chown -R $APP_USER:$APP_USER $APP_DIR
chmod +x $APP_DIR/scripts/*.sh 2>/dev/null || true

# Start services
print_status "Starting services..."
systemctl start user-service
systemctl start web-frontend

# Check service status
print_status "Checking service status..."
sleep 5

if systemctl is-active --quiet user-service; then
    print_status "User Service is running"
else
    print_error "User Service failed to start"
    systemctl status user-service --no-pager
fi

if systemctl is-active --quiet web-frontend; then
    print_status "Web Frontend Service is running"
else
    print_error "Web Frontend Service failed to start"
    systemctl status web-frontend --no-pager
fi

if systemctl is-active --quiet nginx; then
    print_status "Nginx is running"
else
    print_error "Nginx failed to start"
    systemctl status nginx --no-pager
fi

# Display deployment information
echo ""
echo "==========================================="
echo "Deployment Summary"
echo "==========================================="
echo "Application User: $APP_USER"
echo "Application Directory: $APP_DIR"
echo "Database Name: $DB_NAME"
echo "Database User: $DB_USER"
echo "Database Password: $DB_PASS"
echo ""
echo "Services:"
echo "- User Service: http://localhost:5001"
echo "- Web Frontend: http://localhost:5000"
echo "- Nginx: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo 'your-server-ip')"
echo ""
echo "Service Management:"
echo "- Start: sudo systemctl start user-service web-frontend"
echo "- Stop: sudo systemctl stop user-service web-frontend"
echo "- Status: sudo systemctl status user-service web-frontend"
echo "- Logs: sudo journalctl -u user-service -f"
echo ""
echo "Important: Please save the database password and update your domain in nginx configuration!"
echo "==========================================="