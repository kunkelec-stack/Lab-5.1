pipeline {
    agent any
    environment {
        DOCKER_CREDENTIALS_ID = 'roseaw-dockerhub'
        DOCKER_IMAGE = 'cithit/kunkelec'                        
        IMAGE_TAG = "build-${BUILD_NUMBER}"
        GITHUB_URL = 'https://github.com/kunkelec-stack/Lab-5.1.git' 
        KUBECONFIG = credentials('kunkelec-225-sp26')
    }
    stages {
        stage('Checkout') {
            steps {
                checkout([$class: 'GitSCM', branches: [[name: '*/main']],
                          userRemoteConfigs: [[url: "${GITHUB_URL}"]]])
            }
        }
        stage('Lint HTML') {
            steps {
                sh 'npm install htmlhint --save-dev'
                sh 'npx htmlhint *.html'
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    docker.withRegistry('https://registry-1.docker.io', 'roseaw-dockerhub') {
                        docker.build("${DOCKER_IMAGE}:${IMAGE_TAG}", "-f Dockerfile .")
                    }
                }
            }
        }
        stage('Push Docker Image') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', "${DOCKER_CREDENTIALS_ID}") {
                        docker.image("${DOCKER_IMAGE}:${IMAGE_TAG}").push()
                    }
                }
            }
        }
        stage('Deploy to Dev Environment') {
            steps {
                script {
                    def kubeConfig = readFile(KUBECONFIG)
                    sh "sed -i 's|${DOCKER_IMAGE}:latest|${DOCKER_IMAGE}:${IMAGE_TAG}|' deployment-dev.yaml"
                    sh "kubectl apply -f deployment-dev.yaml"
                }
            }
        }
        stage('Run Acceptance Tests') {
            steps {
                script {
                    sh 'docker stop qa-tests || true'
                    sh 'docker rm qa-tests || true'
                    sh 'docker build -t qa-tests -f Dockerfile.test .'
                    sh 'docker run qa-tests'
                    sh 'docker stop qa-tests || true'
                    sh 'docker rm qa-tests || true'
                }
            }
        }
        stage('Deploy to Prod Environment') {
            steps {
                script {
                    sh "sed -i 's|${DOCKER_IMAGE}:latest|${DOCKER_IMAGE}:${IMAGE_TAG}|' deployment-prod.yaml"
                    sh "kubectl apply -f deployment-prod.yaml"
                }
            }
        stage('Setup Test Data') {
            steps {
                echo 'Running Data Generation (from Lab 4.2)...'
                sh 'python3 data-gen.py'
            }
        }

        stage('Security Snapshot') {
            steps {
                echo 'Taking Security Snapshot (from Lab 3.7)...'
                sh 'python3 snapshot-before-security.py'
            }
        }

        stage('DAST Security Scan') {
            steps {
                echo 'Running OWASP ZAP Security Scan...'
                // IMPORTANT: Replace the URL below with your actual Dev Service URL
                sh 'docker run --rm -t ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t http://kunkelec-dev-service -r zap_report.html || true'
            }
        }

        stage('Security Cleanup') {
            steps {
                echo 'Cleaning up Security Data (from Lab 3.7)...'
                sh 'python3 delete-security-data.py'
            }
        }

        stage('Final Data Cleanup') {
            steps {
                echo 'Cleaning up Test Data (from Lab 4.2)...'
                sh 'python3 data-clear.py'
            }
        }     
        }
        stage('Check Kubernetes Cluster') {
            steps {
                script {
                    sh "kubectl get all"
                }
            }
        }
    }
    post {
        success {
            slackSend color: "good", message: "Build Completed: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
        unstable {
            slackSend color: "warning", message: "Build Unstable: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
        failure {
            slackSend color: "danger", message: "Build Failed: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
    }
}
