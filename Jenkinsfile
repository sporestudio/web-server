pipeline {
    agent any

    environment {
        PYTHON = '/usr/bin/python3'
        VENV_DIR = 'venv'
    }

    stages {
        stage('checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/sporestudio/web-server.git'
                script {
                    dir('url-shortener') {
                        echo "Working inside the url-shortener directory"
                    }
                }
            }
        }
        stage('set ip Python enviroment') {
            steps {
                script {
                    // Create virtual enviroment
                    sh 'python3 -m venv venv'
                    sh 'source venv/bin/activate'
                }
            }
        }
        stage('Install dependencies') {
            steps {
                script {
                    sh 'pip install -r requirements.txt'
                }
            }
        }
        stage('run test') {
            steps { 
                script {
                    // exec test with pytest
                    sh 'pytest --maxfail=1 --disable-warnings -q'
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline completed.'
        }
    }
}