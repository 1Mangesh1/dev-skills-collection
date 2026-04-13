---
name: ci-cd-pipelines
description: CI/CD pipeline design, setup, and optimization. Use when user asks to "set up CI/CD", "create a pipeline", "configure Jenkins", "set up GitLab CI", "create CircleCI config", "automate deployments", "create build pipeline", "set up continuous deployment", "configure pipeline stages", "add pipeline caching", "pipeline security", "secret management", "artifact management", "GitHub Actions workflow", "deployment strategies", "canary deployment", or mentions CI/CD pipelines, continuous integration, continuous deployment, build automation, deployment pipelines, or pipeline optimization.
license: MIT
metadata:
  author: 1mangesh1
  version: "1.0.0"
  tags:
    - cicd
    - pipelines
    - jenkins
    - gitlab-ci
    - circleci
    - automation
    - deployment
---

# CI/CD Pipelines

Comprehensive guide to building, configuring, and optimizing CI/CD pipelines across multiple platforms including GitLab CI, Jenkins, CircleCI, and more.

> **Cross-reference**: For GitHub Actions specifically, see the dedicated `github-actions` skill which covers workflows, matrix builds, caching, secrets, and reusable actions in depth.

## CI/CD Pipeline Fundamentals

### Core Concepts

- **Continuous Integration (CI)**: Automatically build and test code on every commit
- **Continuous Delivery (CD)**: Automatically prepare releases for deployment (manual trigger)
- **Continuous Deployment (CD)**: Automatically deploy every change that passes the pipeline

### Pipeline Anatomy

```
Commit -> Build -> Test -> Scan -> Stage -> Deploy -> Monitor
```

- **Stages**: Logical groupings of jobs (build, test, deploy)
- **Jobs**: Individual units of work within a stage
- **Steps**: Commands or actions within a job
- **Artifacts**: Files produced by jobs and passed between stages
- **Triggers**: Events that start a pipeline (push, merge, schedule, manual)

### Pipeline Design Principles

1. **Fail fast** - Run quick checks (lint, syntax) before slow tests
2. **Parallelize** - Run independent jobs concurrently
3. **Cache aggressively** - Avoid rebuilding unchanged dependencies
4. **Minimize artifacts** - Pass only what downstream jobs need
5. **Idempotent deployments** - Running deploy twice yields the same result

---

## GitLab CI/CD

### Basic `.gitlab-ci.yml`

```yaml
# .gitlab-ci.yml
stages:
  - build
  - test
  - scan
  - deploy

variables:
  NODE_VERSION: "20"
  DOCKER_DRIVER: overlay2

# Global defaults
default:
  image: node:${NODE_VERSION}
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - node_modules/
      - .npm/

# Build stage
build:
  stage: build
  script:
    - npm ci --cache .npm --prefer-offline
    - npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 1 hour

# Test stage with parallel jobs
unit-tests:
  stage: test
  needs: [build]
  script:
    - npm ci --cache .npm --prefer-offline
    - npm run test:unit -- --coverage
  coverage: '/Lines\s*:\s*(\d+\.?\d*)%/'
  artifacts:
    reports:
      junit: junit.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml

integration-tests:
  stage: test
  needs: [build]
  services:
    - postgres:16
    - redis:7
  variables:
    POSTGRES_DB: test_db
    POSTGRES_USER: runner
    POSTGRES_PASSWORD: secret
    DATABASE_URL: "postgresql://runner:secret@postgres:5432/test_db"
  script:
    - npm ci --cache .npm --prefer-offline
    - npm run test:integration

# Security scanning
sast:
  stage: scan
  needs: []
  image: semgrep/semgrep:latest
  script:
    - semgrep --config auto --json --output semgrep-results.json .
  artifacts:
    reports:
      sast: semgrep-results.json
  allow_failure: true

dependency-scan:
  stage: scan
  needs: []
  script:
    - npm audit --audit-level=high
  allow_failure: true

# Deploy to staging
deploy-staging:
  stage: deploy
  needs: [unit-tests, integration-tests]
  environment:
    name: staging
    url: https://staging.example.com
  script:
    - ./deploy.sh staging
  only:
    - main

# Deploy to production with manual approval
deploy-production:
  stage: deploy
  needs: [deploy-staging]
  environment:
    name: production
    url: https://example.com
  script:
    - ./deploy.sh production
  when: manual
  only:
    - main
```

### GitLab CI Rules and Conditions

```yaml
# Advanced rules
deploy-preview:
  stage: deploy
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
      when: always
    - if: '$CI_COMMIT_BRANCH == "main"'
      when: never
    - when: never
  script:
    - ./deploy-preview.sh

# Trigger downstream pipeline
trigger-downstream:
  stage: deploy
  trigger:
    project: mygroup/downstream-project
    branch: main
    strategy: depend
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
```

### GitLab CI Matrix Builds

```yaml
test-matrix:
  stage: test
  parallel:
    matrix:
      - NODE_VERSION: ["18", "20", "22"]
        DB: ["postgres", "mysql"]
  image: node:${NODE_VERSION}
  services:
    - name: ${DB}:latest
  script:
    - npm ci
    - npm test
```

---

## Jenkins

### Declarative Jenkinsfile

```groovy
// Jenkinsfile (Declarative Pipeline)
pipeline {
    agent any

    environment {
        DOCKER_REGISTRY = 'registry.example.com'
        APP_NAME = 'my-app'
        NODE_HOME = tool('NodeJS-20')
        PATH = "${NODE_HOME}/bin:${env.PATH}"
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
    }

    parameters {
        choice(name: 'DEPLOY_ENV', choices: ['staging', 'production'], description: 'Target environment')
        booleanParam(name: 'SKIP_TESTS', defaultValue: false, description: 'Skip test stage')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                    env.VERSION = "${env.BUILD_NUMBER}-${env.GIT_COMMIT_SHORT}"
                }
            }
        }

        stage('Install') {
            steps {
                sh 'npm ci'
            }
        }

        stage('Lint & Format') {
            steps {
                sh 'npm run lint'
                sh 'npm run format:check'
            }
        }

        stage('Test') {
            when {
                not { params.SKIP_TESTS }
            }
            parallel {
                stage('Unit Tests') {
                    steps {
                        sh 'npm run test:unit -- --ci --reporters=jest-junit'
                    }
                    post {
                        always {
                            junit 'junit.xml'
                        }
                    }
                }
                stage('Integration Tests') {
                    steps {
                        sh 'docker compose -f docker-compose.test.yml up -d'
                        sh 'npm run test:integration'
                    }
                    post {
                        always {
                            sh 'docker compose -f docker-compose.test.yml down -v'
                        }
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${DOCKER_REGISTRY}/${APP_NAME}:${VERSION}")
                }
            }
        }

        stage('Push Image') {
            steps {
                script {
                    docker.withRegistry("https://${DOCKER_REGISTRY}", 'docker-registry-creds') {
                        docker.image("${DOCKER_REGISTRY}/${APP_NAME}:${VERSION}").push()
                        docker.image("${DOCKER_REGISTRY}/${APP_NAME}:${VERSION}").push('latest')
                    }
                }
            }
        }

        stage('Deploy') {
            input {
                message "Deploy to ${params.DEPLOY_ENV}?"
                ok 'Deploy'
                submitter 'admin,deployers'
            }
            steps {
                withCredentials([
                    string(credentialsId: 'deploy-token', variable: 'DEPLOY_TOKEN'),
                    file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')
                ]) {
                    sh """
                        kubectl set image deployment/${APP_NAME} \
                            ${APP_NAME}=${DOCKER_REGISTRY}/${APP_NAME}:${VERSION} \
                            -n ${params.DEPLOY_ENV}
                    """
                }
            }
        }
    }

    post {
        success {
            slackSend(
                channel: '#deployments',
                color: 'good',
                message: "SUCCESS: ${APP_NAME} ${VERSION} deployed to ${params.DEPLOY_ENV}"
            )
        }
        failure {
            slackSend(
                channel: '#deployments',
                color: 'danger',
                message: "FAILED: ${APP_NAME} pipeline - ${env.BUILD_URL}"
            )
        }
        always {
            cleanWs()
        }
    }
}
```

### Scripted Jenkinsfile

```groovy
// Jenkinsfile (Scripted Pipeline)
node('docker') {
    def app
    def version

    try {
        stage('Checkout') {
            checkout scm
            version = sh(script: 'git describe --tags --always', returnStdout: true).trim()
        }

        stage('Build') {
            sh 'npm ci'
            sh 'npm run build'
        }

        stage('Test') {
            parallel(
                'unit': { sh 'npm run test:unit' },
                'lint': { sh 'npm run lint' }
            )
        }

        stage('Docker') {
            app = docker.build("my-app:${version}")
            docker.withRegistry('https://registry.example.com', 'docker-creds') {
                app.push()
                app.push('latest')
            }
        }

        stage('Deploy') {
            if (env.BRANCH_NAME == 'main') {
                timeout(time: 15, unit: 'MINUTES') {
                    input message: 'Deploy to production?', ok: 'Deploy'
                }
                sh "./deploy.sh production ${version}"
            }
        }

        currentBuild.result = 'SUCCESS'
    } catch (e) {
        currentBuild.result = 'FAILURE'
        throw e
    } finally {
        cleanWs()
        emailext(
            subject: "${currentBuild.result}: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
            body: "Build URL: ${env.BUILD_URL}",
            recipientProviders: [culprits(), requestor()]
        )
    }
}
```

### Jenkins Shared Library

```groovy
// vars/standardPipeline.groovy (Shared Library)
def call(Map config = [:]) {
    pipeline {
        agent any
        stages {
            stage('Build') {
                steps {
                    sh config.buildCommand ?: 'npm ci && npm run build'
                }
            }
            stage('Test') {
                steps {
                    sh config.testCommand ?: 'npm test'
                }
            }
            stage('Deploy') {
                when { branch 'main' }
                steps {
                    sh config.deployCommand ?: './deploy.sh'
                }
            }
        }
    }
}

// Usage in Jenkinsfile:
// @Library('my-shared-lib') _
// standardPipeline(buildCommand: 'make build', testCommand: 'make test')
```

---

## CircleCI

### `.circleci/config.yml`

```yaml
# .circleci/config.yml
version: 2.1

orbs:
  node: circleci/node@5.2
  docker: circleci/docker@2.6
  slack: circleci/slack@4.13

executors:
  node-executor:
    docker:
      - image: cimg/node:20.11
    working_directory: ~/project
    resource_class: medium

  node-with-db:
    docker:
      - image: cimg/node:20.11
      - image: cimg/postgres:16.2
        environment:
          POSTGRES_USER: test
          POSTGRES_DB: test_db
          POSTGRES_PASSWORD: test
      - image: cimg/redis:7.2

commands:
  install-deps:
    steps:
      - checkout
      - node/install-packages:
          pkg-manager: npm
          cache-path: node_modules
          cache-version: v1

jobs:
  lint:
    executor: node-executor
    steps:
      - install-deps
      - run:
          name: Lint
          command: npm run lint
      - run:
          name: Type Check
          command: npm run typecheck

  unit-test:
    executor: node-executor
    parallelism: 4
    steps:
      - install-deps
      - run:
          name: Run Unit Tests
          command: |
            TESTFILES=$(circleci tests glob "src/**/*.test.ts" | circleci tests split --split-by=timings)
            npx jest $TESTFILES --ci --reporters=jest-junit
          environment:
            JEST_JUNIT_OUTPUT_DIR: ./reports
      - store_test_results:
          path: ./reports
      - store_artifacts:
          path: ./coverage

  integration-test:
    executor: node-with-db
    steps:
      - install-deps
      - run:
          name: Wait for DB
          command: dockerize -wait tcp://localhost:5432 -timeout 30s
      - run:
          name: Run Migrations
          command: npm run db:migrate
      - run:
          name: Integration Tests
          command: npm run test:integration

  build-and-push:
    executor: docker/docker
    steps:
      - setup_remote_docker:
          version: "20.10.24"
      - checkout
      - docker/build:
          image: myorg/myapp
          tag: "${CIRCLE_SHA1:0:7},latest"
      - docker/push:
          image: myorg/myapp
          tag: "${CIRCLE_SHA1:0:7},latest"

  deploy:
    executor: node-executor
    parameters:
      environment:
        type: enum
        enum: ["staging", "production"]
    steps:
      - checkout
      - run:
          name: Deploy to << parameters.environment >>
          command: ./deploy.sh << parameters.environment >>
      - slack/notify:
          event: pass
          template: basic_success_1

workflows:
  build-test-deploy:
    jobs:
      - lint
      - unit-test:
          requires:
            - lint
      - integration-test:
          requires:
            - lint
      - build-and-push:
          requires:
            - unit-test
            - integration-test
          filters:
            branches:
              only: main
      - deploy:
          name: deploy-staging
          environment: staging
          requires:
            - build-and-push
      - hold-production:
          type: approval
          requires:
            - deploy-staging
      - deploy:
          name: deploy-production
          environment: production
          requires:
            - hold-production
```

---

## Pipeline Design Patterns

### Fan-Out / Fan-In

Run multiple jobs in parallel, then converge on a single downstream job.

```yaml
# GitLab CI example
stages:
  - build
  - test
  - merge-results
  - deploy

build:
  stage: build
  script: npm run build
  artifacts:
    paths: [dist/]

test-unit:
  stage: test
  needs: [build]
  script: npm run test:unit
  artifacts:
    reports:
      junit: reports/unit.xml

test-e2e:
  stage: test
  needs: [build]
  script: npm run test:e2e
  artifacts:
    reports:
      junit: reports/e2e.xml

test-performance:
  stage: test
  needs: [build]
  script: npm run test:perf
  artifacts:
    paths: [perf-results/]

merge-and-report:
  stage: merge-results
  needs: [test-unit, test-e2e, test-performance]
  script: ./generate-report.sh

deploy:
  stage: deploy
  needs: [merge-and-report]
  script: ./deploy.sh
```

### Matrix Builds

Test across multiple versions, platforms, or configurations simultaneously.

```yaml
# CircleCI matrix
workflows:
  multi-platform:
    jobs:
      - test:
          matrix:
            parameters:
              node-version: ["18", "20", "22"]
              os: ["linux", "macos"]
```

### Conditional Pipelines (Monorepo Strategy)

```yaml
# GitLab CI - trigger jobs only when relevant files change
frontend:
  stage: build
  rules:
    - changes:
        - "frontend/**"
        - "shared/**"
  script:
    - cd frontend && npm ci && npm run build

backend:
  stage: build
  rules:
    - changes:
        - "backend/**"
        - "shared/**"
  script:
    - cd backend && pip install -r requirements.txt && pytest

infrastructure:
  stage: deploy
  rules:
    - changes:
        - "terraform/**"
  script:
    - cd terraform && terraform plan
```

---

## Caching Strategies

### Layer Caching for Speed

```yaml
# GitLab CI - granular caching
variables:
  NPM_CACHE: "${CI_PROJECT_DIR}/.npm"

default:
  cache:
    - key:
        files:
          - package-lock.json
      paths:
        - node_modules/
      policy: pull-push
    - key: "${CI_JOB_NAME}-build-cache"
      paths:
        - .next/cache/
        - dist/
      policy: pull-push

# Jobs that only read cache
test:
  cache:
    - key:
        files:
          - package-lock.json
      paths:
        - node_modules/
      policy: pull   # Read-only, don't waste time uploading
  script:
    - npm test
```

### Docker Layer Caching

```yaml
# CircleCI
jobs:
  build-docker:
    machine:
      image: ubuntu-2204:current
      docker_layer_caching: true
    steps:
      - checkout
      - run: docker build -t myapp:latest .

# Jenkins
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                script {
                    docker.build("myapp:${env.BUILD_NUMBER}",
                        "--cache-from myapp:latest .")
                }
            }
        }
    }
}
```

---

## Secret Management in Pipelines

### Best Practices

1. **Never hardcode secrets** in pipeline files
2. **Use platform-native secret stores** (GitLab CI Variables, Jenkins Credentials, CircleCI Contexts)
3. **Mask secrets** in logs
4. **Rotate secrets** regularly
5. **Limit scope** - use environment-specific secrets

### GitLab CI Variables

```yaml
# Protected and masked variables set in GitLab UI
# Settings > CI/CD > Variables

deploy:
  script:
    - echo "Deploying with token"
    - curl -H "Authorization: Bearer ${DEPLOY_TOKEN}" https://api.example.com/deploy
  variables:
    DEPLOY_TOKEN: ${PRODUCTION_DEPLOY_TOKEN}  # Pulled from CI/CD settings
```

### Jenkins Credentials

```groovy
pipeline {
    agent any
    stages {
        stage('Deploy') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'docker-hub',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    ),
                    string(credentialsId: 'api-key', variable: 'API_KEY'),
                    file(credentialsId: 'service-account', variable: 'SA_KEY_FILE')
                ]) {
                    sh 'docker login -u $DOCKER_USER -p $DOCKER_PASS'
                    sh 'gcloud auth activate-service-account --key-file=$SA_KEY_FILE'
                }
            }
        }
    }
}
```

### HashiCorp Vault Integration

```yaml
# GitLab CI with Vault
deploy:
  variables:
    VAULT_AUTH_ROLE: "gitlab-ci"
  id_tokens:
    VAULT_ID_TOKEN:
      aud: https://vault.example.com
  secrets:
    DATABASE_PASSWORD:
      vault: production/db/password@secrets
      file: false
  script:
    - ./deploy.sh
```

---

## Docker-Based Pipelines

### Multi-Stage Docker Build in CI

```yaml
# GitLab CI with Docker-in-Docker
build-image:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
    IMAGE_TAG: "${CI_REGISTRY_IMAGE}:${CI_COMMIT_SHORT_SHA}"
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build
        --build-arg BUILDKIT_INLINE_CACHE=1
        --cache-from ${CI_REGISTRY_IMAGE}:latest
        --tag ${IMAGE_TAG}
        --tag ${CI_REGISTRY_IMAGE}:latest
        .
    - docker push ${IMAGE_TAG}
    - docker push ${CI_REGISTRY_IMAGE}:latest
```

### Kaniko (Rootless Docker Builds)

```yaml
# GitLab CI with Kaniko (no Docker daemon needed)
build-image:
  stage: build
  image:
    name: gcr.io/kaniko-project/executor:v1.21.0-debug
    entrypoint: [""]
  script:
    - /kaniko/executor
        --context "${CI_PROJECT_DIR}"
        --dockerfile "${CI_PROJECT_DIR}/Dockerfile"
        --destination "${CI_REGISTRY_IMAGE}:${CI_COMMIT_SHORT_SHA}"
        --cache=true
        --cache-repo="${CI_REGISTRY_IMAGE}/cache"
```

---

## Deploy Strategies

### Blue-Green Deployment

```yaml
# GitLab CI blue-green deploy
deploy-blue-green:
  stage: deploy
  script:
    - |
      # Determine current active (blue or green)
      CURRENT=$(kubectl get svc myapp -o jsonpath='{.spec.selector.slot}')
      if [ "$CURRENT" = "blue" ]; then TARGET="green"; else TARGET="blue"; fi

      # Deploy to inactive slot
      kubectl set image deployment/myapp-${TARGET} app=${IMAGE_TAG}
      kubectl rollout status deployment/myapp-${TARGET} --timeout=300s

      # Run smoke tests against inactive slot
      ./smoke-test.sh https://${TARGET}.internal.example.com

      # Switch traffic
      kubectl patch svc myapp -p "{\"spec\":{\"selector\":{\"slot\":\"${TARGET}\"}}}"

      echo "Switched traffic from ${CURRENT} to ${TARGET}"
```

### Canary Deployment

```yaml
# GitLab CI canary deploy
deploy-canary:
  stage: deploy
  script:
    - |
      # Deploy canary (10% traffic)
      kubectl apply -f k8s/canary-deployment.yaml
      kubectl set image deployment/myapp-canary app=${IMAGE_TAG}

      # Wait and monitor error rates
      sleep 300
      ERROR_RATE=$(curl -s "http://prometheus:9090/api/v1/query?query=rate(http_errors_total[5m])" | jq '.data.result[0].value[1]')

      if (( $(echo "$ERROR_RATE > 0.05" | bc -l) )); then
        echo "Error rate too high (${ERROR_RATE}), rolling back canary"
        kubectl delete deployment myapp-canary
        exit 1
      fi

      # Promote canary to full deployment
      kubectl set image deployment/myapp app=${IMAGE_TAG}
      kubectl rollout status deployment/myapp --timeout=300s
      kubectl delete deployment myapp-canary

deploy-rolling:
  stage: deploy
  script:
    - |
      kubectl set image deployment/myapp app=${IMAGE_TAG}
      kubectl rollout status deployment/myapp --timeout=600s

      # If rollout fails, auto-rollback
      if [ $? -ne 0 ]; then
        kubectl rollout undo deployment/myapp
        exit 1
      fi
```

---

## Environment Promotion (Dev -> Staging -> Production)

```yaml
# GitLab CI promotion pipeline
stages:
  - build
  - test
  - deploy-dev
  - deploy-staging
  - deploy-production

build:
  stage: build
  script:
    - docker build -t ${CI_REGISTRY_IMAGE}:${CI_COMMIT_SHORT_SHA} .
    - docker push ${CI_REGISTRY_IMAGE}:${CI_COMMIT_SHORT_SHA}

test:
  stage: test
  script:
    - npm ci && npm test

deploy-dev:
  stage: deploy-dev
  environment:
    name: development
    url: https://dev.example.com
    on_stop: stop-dev
  script:
    - helm upgrade --install myapp ./chart
        --namespace dev
        --set image.tag=${CI_COMMIT_SHORT_SHA}
        --set ingress.host=dev.example.com
  rules:
    - if: '$CI_COMMIT_BRANCH != "main"'

stop-dev:
  stage: deploy-dev
  environment:
    name: development
    action: stop
  script:
    - helm uninstall myapp --namespace dev
  when: manual

deploy-staging:
  stage: deploy-staging
  environment:
    name: staging
    url: https://staging.example.com
  script:
    - helm upgrade --install myapp ./chart
        --namespace staging
        --set image.tag=${CI_COMMIT_SHORT_SHA}
        --set ingress.host=staging.example.com
    - ./run-smoke-tests.sh https://staging.example.com
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'

deploy-production:
  stage: deploy-production
  environment:
    name: production
    url: https://example.com
  script:
    - helm upgrade --install myapp ./chart
        --namespace production
        --set image.tag=${CI_COMMIT_SHORT_SHA}
        --set ingress.host=example.com
        --set replicas=3
  when: manual
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
```

---

## Pipeline Security (SAST, DAST, Dependency Scanning)

```yaml
# GitLab CI security scanning stages
stages:
  - build
  - test
  - security
  - deploy

# Static Application Security Testing
sast-semgrep:
  stage: security
  image: semgrep/semgrep:latest
  script:
    - semgrep --config=auto --json --output=semgrep.json .
  artifacts:
    reports:
      sast: semgrep.json
  allow_failure: true

# Dependency vulnerability scanning
dependency-check:
  stage: security
  script:
    - npm audit --json > npm-audit.json || true
    - npx audit-ci --config audit-ci.json
  artifacts:
    paths:
      - npm-audit.json

# Container image scanning
container-scan:
  stage: security
  image:
    name: aquasec/trivy:latest
    entrypoint: [""]
  script:
    - trivy image
        --exit-code 1
        --severity HIGH,CRITICAL
        --format json
        --output trivy-results.json
        ${CI_REGISTRY_IMAGE}:${CI_COMMIT_SHORT_SHA}
  artifacts:
    paths:
      - trivy-results.json
  allow_failure: true

# Dynamic Application Security Testing
dast:
  stage: security
  needs: [deploy-staging]
  image: owasp/zap2docker-stable
  script:
    - zap-baseline.py
        -t https://staging.example.com
        -r zap-report.html
        -l WARN
  artifacts:
    paths:
      - zap-report.html
  allow_failure: true

# Secret detection
secret-detection:
  stage: security
  image: trufflesecurity/trufflehog:latest
  script:
    - trufflehog git --json --fail file://. > secrets-report.json
  artifacts:
    paths:
      - secrets-report.json
```

---

## Notification Integration

### Slack Notifications

```yaml
# GitLab CI with Slack
.notify_slack: &notify_slack
  after_script:
    - |
      if [ "$CI_JOB_STATUS" = "success" ]; then
        COLOR="#36a64f"
        STATUS="succeeded"
      else
        COLOR="#dc3545"
        STATUS="failed"
      fi
      curl -X POST "$SLACK_WEBHOOK_URL" \
        -H 'Content-type: application/json' \
        -d "{
          \"attachments\": [{
            \"color\": \"${COLOR}\",
            \"title\": \"Pipeline ${STATUS}: ${CI_PROJECT_NAME}\",
            \"text\": \"Branch: ${CI_COMMIT_REF_NAME}\nCommit: ${CI_COMMIT_SHORT_SHA}\nJob: ${CI_JOB_NAME}\",
            \"footer\": \"<${CI_PIPELINE_URL}|View Pipeline>\"
          }]
        }"

deploy-production:
  stage: deploy
  <<: *notify_slack
  script:
    - ./deploy.sh production
```

### Email Notifications (Jenkins)

```groovy
// Jenkinsfile post section
post {
    failure {
        emailext(
            subject: "FAILED: ${env.JOB_NAME} [${env.BUILD_NUMBER}]",
            body: """
                <h2>Build Failed</h2>
                <p>Job: ${env.JOB_NAME}</p>
                <p>Build: <a href="${env.BUILD_URL}">#${env.BUILD_NUMBER}</a></p>
                <p>Changes: ${currentBuild.changeSets.collect { it.items.collect { it.msg } }.flatten().join(', ')}</p>
            """,
            mimeType: 'text/html',
            recipientProviders: [culprits(), developers(), requestor()]
        )
    }
}
```

---

## Artifact Management

```yaml
# GitLab CI artifact strategies
build:
  stage: build
  script:
    - npm run build
  artifacts:
    paths:
      - dist/
      - build/
    exclude:
      - dist/**/*.map
    expire_in: 1 week
    when: on_success

test:
  stage: test
  script:
    - npm test
  artifacts:
    # Upload test results for GitLab UI integration
    reports:
      junit: reports/junit.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml
    # Also keep raw coverage for downstream
    paths:
      - coverage/
    when: always    # Keep artifacts even on failure
    expire_in: 30 days
```

---

## Pipeline as Code Best Practices

1. **Version control your pipeline** - Pipeline config lives with the code it builds
2. **Use templates and includes** to reduce duplication

```yaml
# GitLab CI includes
include:
  - project: 'devops/pipeline-templates'
    ref: main
    file:
      - '/templates/node-ci.yml'
      - '/templates/docker-build.yml'
      - '/templates/deploy.yml'

  - local: '.gitlab/ci/security.yml'

  - template: Security/SAST.gitlab-ci.yml
```

3. **Pin versions** of tools and images
4. **Use linting** to validate pipeline configs before commit

```bash
# Validate GitLab CI locally
gitlab-ci-lint .gitlab-ci.yml

# Validate CircleCI config
circleci config validate

# Validate Jenkins pipeline
# Use Jenkins CLI or replay feature
```

5. **Keep pipelines fast** - target under 10 minutes for CI, under 30 for full CD
6. **Use YAML anchors** to reduce repetition

```yaml
.deploy_template: &deploy_defaults
  image: alpine/k8s:1.28.4
  before_script:
    - kubectl config use-context ${KUBE_CONTEXT}
  script:
    - helm upgrade --install ${APP_NAME} ./chart --namespace ${NAMESPACE}

deploy-staging:
  <<: *deploy_defaults
  variables:
    KUBE_CONTEXT: staging-cluster
    NAMESPACE: staging
  environment:
    name: staging

deploy-production:
  <<: *deploy_defaults
  variables:
    KUBE_CONTEXT: production-cluster
    NAMESPACE: production
  environment:
    name: production
  when: manual
```

---

## Common Pipeline Failures and Fixes

| Problem | Cause | Fix |
|---------|-------|-----|
| `npm ci` fails | Lock file mismatch | Run `npm install` locally and commit `package-lock.json` |
| Docker build OOM | Insufficient memory | Increase runner resources or optimize Dockerfile |
| Tests pass locally, fail in CI | Environment differences | Use same Docker image locally; check env vars |
| Cache not restoring | Key mismatch | Verify cache key references correct files |
| Pipeline hangs | Waiting for approval or stuck service | Add timeouts; check `when: manual` stages |
| Permission denied | File not executable | Run `chmod +x script.sh` and commit |
| Secret not available | Variable scope mismatch | Check protected/masked settings; branch protection |
| Flaky tests | Race conditions or external deps | Retry mechanism; mock external services |
| Slow pipelines | No parallelism or caching | Add `parallel`, `needs` (DAG), and caching |
| Deploy rollback fails | No rollback strategy | Implement `kubectl rollout undo` or Helm rollback |

### Retry Flaky Jobs

```yaml
# GitLab CI
flaky-integration-test:
  stage: test
  retry:
    max: 2
    when:
      - runner_system_failure
      - stuck_or_timeout_failure
      - script_failure
  script:
    - npm run test:integration
```

### Timeout Configuration

```yaml
# GitLab CI
job-with-timeout:
  timeout: 15 minutes
  script:
    - npm run long-test

# CircleCI
jobs:
  slow-test:
    steps:
      - run:
          name: Long running test
          command: npm run test:e2e
          no_output_timeout: 20m
```

---

## References

- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [Jenkins Pipeline Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/)
- [CircleCI Configuration Reference](https://circleci.com/docs/configuration-reference/)
- [12 Factor App - Build/Release/Run](https://12factor.net/build-release-run)
- [DORA Metrics for CI/CD Performance](https://dora.dev/guides/dora-metrics-four-keys/)
- See also: `github-actions` skill for GitHub-specific workflows
