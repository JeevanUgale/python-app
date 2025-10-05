# Python User Form App

This is a small Flask application that provides a user form (first_name, last_name, age, qualification, address), stores data in MariaDB, and shows a list of saved users.

What you'll get
- Flask backend with routes to create and list users
- WTForms-based form with validation
- SQLAlchemy models and configuration for MariaDB
- Docker Compose file to spin up a MariaDB instance quickly

Quick start (with Docker Compose)

1. Create a virtualenv and install dependencies:

   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

2. Run the app:

   python app.py

3. Open http://127.0.0.1:5000 in your browser.

Alternative (use local MariaDB): point the values in `.env` to your DB server and ensure the DB exists.

Notes
- The app will run create_all() on startup to create the `users` table if it doesn't exist.
- For production use, replace SECRET_KEY and secure the database credentials.
