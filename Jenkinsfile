pipeline {
    agent any
    environment {
        APP_NAME = 'product-service'
        BUILD_TAG = "${env.GIT_BRANCH}-${env.BUILD_NUMBER}"
        // PYPI_TOKEN = credentials('pypi-token')   // Not needed yet, securely inject from Jenkins credentials
    }

    stages {
        // Checkout stage is implicit in Jenkins pipeline via SCM, 
        // so we don't need to define it explicitly.
        stage('Install Dependencies') {
            steps {
                sh '''
                  python3 -m venv venv
                  . venv/bin/activate
                  pip install --upgrade pip
                  pip install -r requirements.txt
                '''
            }
        }

        stage('Linting') {
            steps {
                sh '''
                  . venv/bin/activate
                  pip install flake8
                  flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics
                  flake8 src/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
                '''
            }
        }

        // Tests will be included later
        // stage('Run Tests') {
        //     steps {
        //         sh '''
        //           . venv/bin/activate
        //           pytest --maxfail=1 --disable-warnings -q
        //         '''
        //     }
        // }

        stage('Build/Package') {
            steps {
                sh '''
                  . venv/bin/activate
                  python -m build
                  mv dist/*.whl dist/${BUILD_TAG}.whl
                '''
            }
        }

        stage('Archive Artifacts') {
            steps {
                archiveArtifacts artifacts: "dist/${BUILD_TAG}.whl", fingerprint: true
            }
        }
    }

    post {
        success {
            slackSend(channel: '#all-godaampe',
                      color: 'good',
                      message: "✅ SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER} on ${env.GIT_BRANCH}")
        }
        failure {
            slackSend(channel: '#all-godaampe',
                      color: 'danger',
                      message: "❌ FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER} on ${env.GIT_BRANCH}")
        }
    }
}
