pipeline {
    agent {
        label 'app-server'
    }
    stages {
        stage('Clone reporitory') {
            steps {
                git url: 'https://github.com/jeevanugale/python-app.git', branch: 'bugfix-01'
            }
        }
        stage('Copy .env.example') {
            steps {
                sh 'cp .env.example .env'
            }
        }
        stage('') {
    }
}