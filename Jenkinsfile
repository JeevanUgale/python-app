pipeline {
    agent {
        label 'app-server'
    }
    stages {
        stage('Clone reporitory') {
            steps {
                git url: 'https://github.com/jeevanugale/python-app.git', branch: 'testing'
            }
        }
        stage('Copy .env.example') {
            steps {
                sh 'cp .env.example .env'
            }
        }
        stage('inject secrets securly') {
            steps {
                withCredentials([
                    string(credentialsId: 'db-name', variable: 'DB_NAME'),
                    string(credentialsId: 'db-host', variable: 'DB_HOST'),
                    string(credentialsId: 'db-pass', variable: 'DB_PASS'),
                    string(credentialsId: 'mysql-root-password', variable: 'MYSQL_ROOT_PASSWORD'),
                    string(credentialsId: 'secret-key', variable: 'SECRET_KEY'),
                    string(credentialsId: 'jwt-secret', variable: 'JWT_SECRET'),
                    string(credentialsId: 'admin-username', variable: 'ADMIN_USERNAME'),
                    string(credentialsId: 'admin-password-hash', variable: 'ADMIN_PASSWORD_HASH')
                ]) {
                    sh '''
                      sed -i "s|^DB_NAME=.*|DB_NAME=${DB_NAME}|" .env
                      sed -i "s|^DB_HOST=.*|DB_HOST=${DB_HOST}|" .env
                      sed -i "s|^DB_PASS=.*|DB_PASS=${DB_PASS}|" .env
                      sed -i "s|^MYSQL_ROOT_PASSWORD=.*|MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}|" .env
                      sed -i "s|^SECRET_KEY=.*|SECRET_KEY=${SECRET_KEY}|" .env
                      sed -i "s|^JWT_SECRET=.*|JWT_SECRET=${JWT_SECRET}|" .env
                      sed -i "s|^ADMIN_USERNAME=.*|ADMIN_USERNAME=${ADMIN_USERNAME}|" .env
                      sed -i "s|^ADMIN_PASSWORD_HASH=.*|ADMIN_PASSWORD_HASH=${ADMIN_PASSWORD_HASH}|" .env
                    '''
                }
            }
        }
        stage('run docker compose') {
            steps {
                sh '''
                  docker rm $(docker ps -aq) -f || true
                  docker compose pull
                  docker compose up -d
                '''
            }
        }
    }
}