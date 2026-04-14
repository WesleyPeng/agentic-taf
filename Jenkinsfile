// Agentic-TAF CI/CD Pipeline
// Stages: Install → Lint → Unit Tests → Build Wheel
// Future: API Tests → UI Tests → BDD → AI → Chaos → Load → Report

pipeline {
    agent {
        docker {
            image 'python:3.12-slim'
            args '-u root'
        }
    }

    environment {
        PYTHONPATH = 'src/main/python'
        PIP_NO_CACHE_DIR = '1'
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
        ansiColor('xterm')
    }

    stages {
        stage('Install') {
            steps {
                sh '''
                    python -m pip install --upgrade pip
                    pip install -r src/main/python/requirements-dev.txt
                '''
            }
        }

        stage('Lint') {
            parallel {
                stage('flake8') {
                    steps {
                        sh 'flake8 src/main/python/ src/test/python/ --max-line-length=120 --count --show-source --statistics'
                    }
                }
                stage('mypy') {
                    steps {
                        sh 'mypy src/main/python/taf/ --ignore-missing-imports'
                    }
                }
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    pytest src/test/python/ut/ -v --tb=short \
                        --junitxml=reports/unit-tests.xml \
                        --cov=taf --cov-report=xml:reports/coverage.xml
                '''
            }
            post {
                always {
                    junit 'reports/unit-tests.xml'
                    archiveArtifacts artifacts: 'reports/*.xml', allowEmptyArchive: true
                }
            }
        }

        stage('Build Wheel') {
            steps {
                sh '''
                    pip install build
                    python -m build --wheel --outdir dist/
                '''
            }
            post {
                success {
                    archiveArtifacts artifacts: 'dist/*.whl', allowEmptyArchive: true
                }
            }
        }

        // --- Future stages (stubs) ---

        stage('API Tests') {
            when { expression { return false } }
            steps {
                sh 'pytest src/test/python/suites/agentic/api/ -v --junitxml=reports/api-tests.xml -m e2e'
            }
        }

        stage('UI Tests') {
            when { expression { return false } }
            steps {
                sh 'pytest src/test/python/suites/agentic/ui/ -v --junitxml=reports/ui-tests.xml -m e2e --headless'
            }
        }

        stage('BDD') {
            when { expression { return false } }
            steps {
                sh 'behave src/test/python/suites/agentic/bdd/features/ --junit --junit-directory=reports/'
            }
        }

        stage('AI Tests') {
            when { expression { return false } }
            steps {
                sh 'pytest src/test/python/suites/agentic/ai/ -v --junitxml=reports/ai-tests.xml -m ai'
            }
        }

        stage('Chaos') {
            when { expression { return false } }
            steps {
                sh 'pytest src/test/python/suites/agentic/chaos/ -v --junitxml=reports/chaos-tests.xml -m chaos --timeout=600'
            }
        }

        stage('Load') {
            when { expression { return false } }
            steps {
                sh 'pytest src/test/python/suites/agentic/load/ -v --junitxml=reports/load-tests.xml -m load --timeout=900'
            }
        }

        stage('Report') {
            when { expression { return false } }
            steps {
                sh 'echo "TODO: Push results to OpenSearch + SonarQube + LangFuse"'
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
