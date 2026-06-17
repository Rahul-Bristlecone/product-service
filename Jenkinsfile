pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/Rahul-Bristlecone/product-service.git'
            }
        }
        stage('Install Dependencies') {
            steps {
                sh 'pip install --upgrade pip'
                sh 'pip install -r requirements.txt'
            }
        }
        // stage('Run Tests') {
        //     steps {
        //         sh 'pytest --maxfail=1 --disable-warnings -q'
        //     }
        // }
        stage('Build') {
            steps {
                sh 'python -m build'
            }
        }
    }
}
