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

        stage('Run Tests with Coverage') {
            steps {
                sh '''
                  . venv/bin/activate
                  pytest tests/unit \
                    --cov=src \
                    --cov-report=term-missing \
                    --cov-report=html:htmlcov \
                    --cov-report=xml:coverage.xml \
                    --cov-fail-under=80 \
                    --maxfail=1 \
                    --disable-warnings -v
                '''
            }
        }

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
                
                // Archive coverage reports
                archiveArtifacts artifacts: "htmlcov/**,coverage.xml", allowEmptyArchive: true
                
                // Publish code coverage metrics
                publishHTML([
                    reportDir: 'htmlcov',
                    reportFiles: 'index.html',
                    reportName: 'Code Coverage Report',
                    keepAll: true,
                    allowMissing: false,
                    alwaysLinkToLastBuild: true
                ])
                
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
