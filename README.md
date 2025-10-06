# Python Flask Application
## **Overview**
This project is a web application built with the Flask framework and Python 3. It leverages MariaDB as the backend database and uses Gunicorn as the WSGI server for production-ready deployment. The application is designed for simplicity, scalability, and easy setup, making it ideal for small to medium web projects or as a template for more complex backends.

# Technologies Used
## **Python 3**

Flask (Web framework)

MariaDB (Database)

Gunicorn (WSGI HTTP server)

python-dotenv (Environment variable management)

# How the Application Works
Handles web and API requests via Flask routes and controllers.

Connects securely to a MariaDB database for persistent storage.

Uses environment variables for all configuration, improving security and portability.

Runs with Gunicorn for multi-worker production serving.

# Database Setup
## 1. Install MariaDB:

shell
`sudo apt update && sudo apt install mariadb-server -y`

## 2. Configuration Change:

**To allow external connections (not just localhost), modify the bind address in /etc/mysql/mariadb.conf.d/50-server.cnf:**

**text**
bind-address = 0.0.0.0
Restart MariaDB if this was changed:

shell
`sudo systemctl restart mariadb`

## 3. Create Database and User:

sql
`CREATE DATABASE users_db;
CREATE USER 'flaskuser'@'%' IDENTIFIED BY 'pass';
GRANT ALL PRIVILEGES ON users_db.* TO 'flaskuser'@'%';
FLUSH PRIVILEGES;`

# Application Setup
## 1. Install System Packages:

shell
`sudo apt update && sudo apt install python3-venv mysql-client python3-pip -y`

## 2. Clone the Repository:

shell
`git clone https://github.com/JeevanUgale/python-app.git
cd python-app`

## 3. Environment Variables:

**Copy the example file and update your environment values:**

shell
`cp .env.example .env
Edit .env to set:`

text
DB_HOST=<db_host>
DB_NAME=users_db
DB_USER=flaskuser
DB_PASS=pass
FLASK_SECRET_KEY=<your_secret>

## 4. Python Environment and App Installation:

shell
`python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip build wheel setuptools
python -m build
pip install dist/*.whl
pip install gunicorn`

## 5. Running the Application
Run the Flask app using Gunicorn with two workers, listening on all interfaces at port 5000:

shell
`gunicorn -w 2 -b 0.0.0.0:5000 python_app.wsgi:app &`