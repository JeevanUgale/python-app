# Python Flask Application

This repository contains a **Python Flask web application** that demonstrates a typical Flask project structure with a relational database backend (MariaDB/MySQL).  
The application exposes basic web routes and uses SQLAlchemy for ORM-based database interactions.

---

## 🛠️ Technologies Used
- **Python 3.12+**
- **Flask** – web framework
- **Flask-SQLAlchemy** – ORM for database operations
- **Gunicorn** – WSGI HTTP server for production
- **MariaDB / MySQL** – relational database
- **pip / build / wheel / setuptools** – Python packaging tools
- **dotenv** – for environment configuration

---

## ⚙️ How the Application Works
1. The application is built as a Python package (`python_app`) with a factory function `create_app()` that initializes the Flask app and configures the database.
2. Environment variables (from the `.env` file) provide database credentials and runtime settings.
3. Gunicorn loads the app from `python_app/wsgi.py` and serves it on the configured host and port.
4. SQLAlchemy connects to the MariaDB database to perform CRUD operations.

---

## 📦 Prerequisites
- A Linux server (e.g., Ubuntu on EC2)
- `sudo` privileges
- Network access to your MariaDB server

---

## 🗄️ Database Setup (MariaDB)

### 1. Install MariaDB
```bash
sudo apt update && sudo apt install mariadb-server -y     # Update package index and install MariaDB server

### 2. Configure Bind Address
```bash
sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf          # Open MariaDB config file

# Change the following line:
bind-address = 0.0.0.0                                     # Allow MariaDB to accept connections from all hosts

sudo systemctl restart mariadb                             # Restart MariaDB to apply config changes

### 3. Create Database, User, and Grant Privileges
CREATE DATABASE users_db;                                  -- Create a new database
CREATE USER 'flaskuser'@'%' IDENTIFIED BY 'pass';          -- Create a new user with password
GRANT ALL PRIVILEGES ON users_db.* TO 'flaskuser'@'%';     -- Grant full access on the database to the user
FLUSH PRIVILEGES;                                          -- Apply changes
EXIT;                                                      -- Exit MariaDB prompt

### Application Setup

### 1. Install Required Packages
sudo apt update && sudo apt install python3-venv mysql-client python3-pip -y   # Install Python venv, MySQL client, and pip

### 2. Configure Environment
cp .env.example .env                                       # Copy example environment file to .env
vim .env                                                  # Edit .env to set DB credentials and other configs

### 3. Set Up Python Virtual Environment
python3 -m venv .venv                                      # Create a Python virtual environment
source .venv/bin/activate                                  # Activate the virtual environment
pip install --upgrade pip build wheel setuptools          # Upgrade pip and install build tools

### 4. Build and Install the Application
python -m build                                            # Build the project into a distributable package
pip install dist/*.whl                                     # Install the built package

### 5. Install Gunicorn
pip install gunicorn                                       # Install Gunicorn WSGI server

### 6. Run the Application with Gunicorn
gunicorn -w 2 -b 0.0.0.0:5000 python_app.wsgi:app &         # Run the app with 2 workers, bound to port 5000 in background

Notes:

-w 2 → Use 2 worker processes (adjust based on CPU cores)

-b 0.0.0.0:5000 → Binds the app to all network interfaces on port 5000

& → Runs the process in the background

### 7. Verify Deployment
http://<server-public-ip>:5000