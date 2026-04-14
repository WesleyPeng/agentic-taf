// Agentic-TAF CI/CD Pipeline
// Full pipeline: Install → Lint → Unit Tests → Build →
//   API → Security → UI → BDD → AI → Chaos → Load → Report
//
// E2E stages require:
//   AGENT_BASE_URL      — agent endpoint (via kubectl port-forward)
//   DASHBOARD_BASE_URL  — dashboard endpoint (via kubectl port-forward)
//   KUBECONFIG          — path to kubeconfig for chaos tests
//   TAF_RUN_E2E=true    — master switch to enable E2E stages
//
// Reporting stage requires:
//   SONAR_HOST_URL + SONAR_TOKEN  — SonarQube scanner
//   OPENSEARCH_URL                — OpenSearch for JUnit results
//   LANGFUSE_PUBLIC_KEY + LANGFUSE_SECRET_KEY — LangFuse traces

pipeline {
    agent {
        docker {
            image 'python:3.12-slim'
            args '-u root'
        }
    }

    environment {
        PYTHONPATH      = 'src/main/python'
        PIP_NO_CACHE_DIR = '1'
        TAF_RUN_E2E     = "${params.RUN_E2E ?: env.TAF_RUN_E2E ?: 'false'}"
    }

    parameters {
        booleanParam(name: 'RUN_E2E', defaultValue: false, description: 'Run E2E test stages (requires live cluster)')
    }

    options {
        timeout(time: 60, unit: 'MINUTES')
        timestamps()
        ansiColor('xterm')
    }

    stages {
        stage('Install') {
            steps {
                sh '''
                    apt-get update -qq && apt-get install -y -qq curl > /dev/null 2>&1
                    python -m pip install --upgrade pip
                    pip install -r src/main/python/requirements-dev.txt
                    pip install ".[httpx,websocket,all]" 2>/dev/null || true
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
                    mkdir -p reports
                    pytest src/test/python/ut/ -v --tb=short \
                        --junitxml=reports/unit-tests.xml \
                        --cov=taf --cov-report=xml:reports/coverage.xml \
                        --cov-report=term-missing
                '''
            }
            post {
                always {
                    junit 'reports/unit-tests.xml'
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

        // --- E2E stages (gated by TAF_RUN_E2E) ---

        stage('API Tests') {
            when { expression { return env.TAF_RUN_E2E == 'true' } }
            steps {
                sh '''
                    pytest src/test/python/suites/agentic/api/ -v \
                        --junitxml=reports/api-tests.xml -m e2e
                '''
            }
            post {
                always { junit allowEmptyResults: true, testResults: 'reports/api-tests.xml' }
            }
        }

        stage('Security Tests') {
            when { expression { return env.TAF_RUN_E2E == 'true' } }
            steps {
                sh '''
                    pytest src/test/python/suites/agentic/security/ -v \
                        --junitxml=reports/security-tests.xml -m e2e
                '''
            }
            post {
                always { junit allowEmptyResults: true, testResults: 'reports/security-tests.xml' }
            }
        }

        stage('UI Tests') {
            when { expression { return env.TAF_RUN_E2E == 'true' } }
            steps {
                sh '''
                    pip install playwright && playwright install --with-deps chromium
                    pytest src/test/python/suites/agentic/ui/ -v \
                        --junitxml=reports/ui-tests.xml -m e2e
                '''
            }
            post {
                always { junit allowEmptyResults: true, testResults: 'reports/ui-tests.xml' }
            }
        }

        stage('BDD') {
            when { expression { return env.TAF_RUN_E2E == 'true' } }
            steps {
                sh '''
                    behave src/test/python/suites/agentic/bdd/features/ \
                        --junit --junit-directory=reports/
                '''
            }
            post {
                always { junit allowEmptyResults: true, testResults: 'reports/TESTS-*.xml' }
            }
        }

        stage('AI Tests') {
            when { expression { return env.TAF_RUN_E2E == 'true' } }
            steps {
                sh '''
                    pytest src/test/python/suites/agentic/ai/ -v \
                        --junitxml=reports/ai-tests.xml -m ai
                '''
            }
            post {
                always { junit allowEmptyResults: true, testResults: 'reports/ai-tests.xml' }
            }
        }

        stage('Chaos') {
            when { expression { return env.TAF_RUN_E2E == 'true' } }
            steps {
                sh '''
                    pytest src/test/python/suites/agentic/chaos/ -v \
                        --junitxml=reports/chaos-tests.xml -m chaos --timeout=600
                '''
            }
            post {
                always { junit allowEmptyResults: true, testResults: 'reports/chaos-tests.xml' }
            }
        }

        stage('Load') {
            when { expression { return env.TAF_RUN_E2E == 'true' } }
            steps {
                sh '''
                    pytest src/test/python/suites/agentic/load/ -v \
                        --junitxml=reports/load-tests.xml -m load --timeout=900
                '''
            }
            post {
                always { junit allowEmptyResults: true, testResults: 'reports/load-tests.xml' }
            }
        }

        stage('Report') {
            steps {
                sh '''
                    echo "=== Test Results ==="
                    ls -la reports/ || true

                    # Push JUnit results to OpenSearch (if configured)
                    if [ -n "${OPENSEARCH_URL}" ]; then
                        python src/test/python/suites/agentic/reporting/push_results.py \
                            --reports-dir reports/ \
                            --opensearch-url "${OPENSEARCH_URL}" \
                            --index test-results || echo "OpenSearch push failed (non-fatal)"
                    fi

                    # SonarQube scan (if configured)
                    if [ -n "${SONAR_HOST_URL}" ] && [ -n "${SONAR_TOKEN}" ]; then
                        pip install pysonar-scanner 2>/dev/null || true
                        sonar-scanner \
                            -Dsonar.host.url="${SONAR_HOST_URL}" \
                            -Dsonar.token="${SONAR_TOKEN}" || echo "SonarQube scan failed (non-fatal)"
                    fi
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
            cleanWs()
        }
    }
}
