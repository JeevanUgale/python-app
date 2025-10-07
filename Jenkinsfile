pipeline {
    agent any
    environment {
        SECRET_KEY = credentials('flask_secret_text')
        DB_USER = credentials('db_user')
        DB_PASS = credentials('db_user_pass')
        DB_HOST = credentials('db_host')
        DB_PORT = '3306'
        DB_NAME = credentials('db_name')
    }
    stages {
        stage('Git Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/JeevanUgale/python-app.git'
                sh 'ls -la'
            }
        }
        stage('copy env file') {
            steps {
                echo 'copying .env.example to .env'
                sh 'cp .env.example .env'
            }
        }
        stage('change the env file values') {
            steps {
                echo 'changing the .env file values'
                sh '''
                sed -i "s/SECRET_KEY=.*/SECRET_KEY=${SECRET_KEY}/" .env
                sed -i "s/DB_USER=.*/DB_USER=${DB_USER}/" .env
                sed -i "s/DB_PASS=.*/DB_PASS=${DB_PASS}/" .env
                sed -i "s/DB_HOST=.*/DB_HOST=${DB_HOST}/" .env
                sed -i "s/DB_PORT=.*/DB_PORT=${DB_PORT}/" .env
                sed -i "s/DB_NAME=.*/DB_NAME=${DB_NAME}/" .env
                '''
                sh 'cat .env'
            }
        }
        stage('Create python venv') {
            steps {
                sh 'python3 -m venv .venv'
            }
        }
        stage('upgrade pip and install build tools') {
            steps {
                sh '. .venv/bin/activate && pip install --upgrade pip build wheel setuptools'
                sh '. .venv/bin/activate && pip install -r requirements.txt'
            }
        }
        stage('Build the app') {
            steps {
                sh '. .venv/bin/activate && python -m build'
            }
        }
        stage('Install the built app') {
            steps {
                sh '. .venv/bin/activate && pip install dist/*.whl'
            }
        }
        stage('Smoke Test') {
            steps {
                sh '. .venv/bin/activate && python scripts/smoke_test.py'
            }
        }
        stage('Archive Artifacts') {
            steps {
                archiveArtifacts artifacts: 'dist/**', fingerprint: true
            }
        }
        stage('Install Gunicorn') {
            steps {
                sh '. .venv/bin/activate && pip install gunicorn'
            }
        }
        stage('Run the app with Gunicorn') {
            steps {
                sh 'sudo systemctl daemon-reload && sudo systemctl start python_app && sudo systemctl status python_app'
            }
        }
    }
}