pipeline {
    agent any

    stages {
        stage('Install Dependencies') {
            steps {
                sh '''
                  python3 -m venv venv
                  . venv/bin/activate
                  pip install --upgrade pip
                  pip install -e .
                '''
            }
        }
        // stage('Run Tests') {
        //     steps {
        //         sh '''
        //           . venv/bin/activate
        //           pytest --maxfail=1 --disable-warnings -q
        //         '''
        //     }
        // }
        stage('Build') {
            steps {
                sh '''
                  . venv/bin/activate
                  python -m build
                '''
            }
        }
    }
    post {
        success {
            archiveArtifacts artifacts: 'dist/*', fingerprint: true
        }
    }
}
