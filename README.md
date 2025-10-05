# Python User Form App

This is a small Flask application that provides a user form (first_name, last_name, age, qualification, address), stores data in MariaDB, and shows a list of saved users.

What you'll get
- Flask backend with routes to create and list users
- WTForms-based form with validation
- SQLAlchemy models and configuration for MariaDB

**Quick start**

**DB-Setup:**

**1. Install MariaDB:**

   sudo apt update
   
   sudo apt install mariadb-server -y
   
   sudo systemctl enable mariadb
   
   sudo systemctl start mariadb

**2. create DB and user:**

   CREATE DATABASE users_db;
   
   CREATE USER 'flaskuser'@'APP_SERVER_PRIVATE_IP' IDENTIFIED BY 'password';
   
   GRANT ALL PRIVILEGES ON users_db.* TO 'flaskuser'@'APP_SERVER_PRIVATE_IP';
   
   FLUSH PRIVILEGES;

**App setup:**

**1. Install packages:**

   sudo apt udpate
   
   sudo apt install mysql-client python3.12-venv -y
   
   #clone the source code and cd into the directory.
   
**2. dump the sqldump file into databse server DB:**

   mysql -u flaskuser -p users_db -h db-server-ip/endpoint users_db < newdump.sql

**3. configurations for .env**

   cd python-app
   
   touch .env   #create a .env file to inject the DB creds. and change the values of varialbles as per your configuration.

   file env variables
   
   SECRET_KEY=any-alphabetic-words
   DB_USER=flaskuser
   DB_PASS=flask123
   DB_HOST=DB-server-ip
   DB_PORT=3306
   DB_NAME=users_db
   
**4. Create a virtualenv and install dependencies:**

   python3 -m venv .venv
   
   source .venv/bin/activate
   
   pip install -r requirements.txt

**5. Run the app:**

   python app.py

**6. Open http://app-server-ip:5000 in your browser.**

Alternative (use local MariaDB): point the values in `.env` to your DB server and ensure the DB exists.

**Notes**
- For production use, replace SECRET_KEY and secure the database credentials.
