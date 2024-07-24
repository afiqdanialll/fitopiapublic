/*pipeline {
    agent any
    stages {
        stage('Preparation') {
            steps {
                //stop main containers to run start and test development containers
                sh 'docker compose -f docker-compose.yml -p main_fitopia down || true'
                // remove main containers to ensure no running container
                sh 'docker compose -f docker-compose.yml -p main_fitopia rm -f || true'
                sh 'chmod +x backend/wsgi-entrypoint.sh backend/server/manage.py'
            }
        }
        stage('Automated Test') {
            when {
                branch 'development'
            }
            steps {
                sh 'docker compose -f docker-compose.yml -p development_fitopia build'
                sh 'docker compose -f docker-compose.yml -p development_fitopia up -d'
                sh 'sleep 30'
                sh 'docker exec development_fitopia-backend-1 python backend/server/manage.py test apps.authentication.tests'
                sh 'docker exec development_fitopia-backend-1 python backend/server/manage.py test apps.data.tests'
                sh 'docker exec development_fitopia-backend-1 python backend/server/manage.py test apps.data.tests_selenium_staff'
                sh 'docker exec development_fitopia-backend-1 python backend/server/manage.py test apps.data.tests_selenium_customer'
            }
            post {
                always {
                    sh 'docker compose -f docker-compose.yml -p development_fitopia down'
                }
            }
        }
        stage('OWASP Dependency-Check Vulnerabilities') {
            when {
                branch 'development'
            }
            steps {
                sh 'cd frontend && npm install'
                dependencyCheck additionalArguments: '--noupdate --format HTML --format XML --enableExperimental "pip"', odcInstallation: 'OWASP Dependency-Check Vulnerabilities'
                dependencyCheckPublisher pattern: 'dependency-check-report.xml'
            }
        }
        stage('Code Quality Check via SonarQube') {
            when {
                branch 'development'
            }
            steps {
                script {
                    def scannerHome = tool 'SonarQube'
                    withSonarQubeEnv('SonarQube') {
                        sh "${scannerHome}/bin/sonar-scanner -Dsonar.projectKey=sonarqube-fitopia -Dsonar.sources=."
                    }
                }
            }
        }
        stage('Deploy Production') {
            when {
                branch 'main'
            }
            steps {
                sh 'docker rmi -f main_fitopia-nginx || true'
                sh 'docker rmi -f main_fitopia-backend || true'
                sh 'docker compose -f docker-compose.yml -p main_fitopia up --build -d'
            }
        }
    }
    post {
        always {
            script {
                if (env.BRANCH_NAME == 'development') {
                    // Remove development containers and images and volumes
                    sh 'docker compose -f docker-compose.yml -p development_fitopia rm -f || true'
                    sh 'docker rmi development_fitopia-nginx || true'
                    sh 'docker rmi development_fitopia-backend || true'
                    sh 'docker volume rm -f development_fitopia_static_volume || true'
                    sh 'docker volume rm -f development_fitopia_logs || true'
                    // Remove unused data by docker to save space
                    sh 'docker builder prune -f'
                    sh 'docker image prune -f'
                    sh 'docker container prune -f'
                    // Remove node_modules folder from system to save space
                    sh 'rm -rf /var/jenkins_home/workspace/fitopia_development/frontend/node_modules'
                    // Spin up previous functional verison of production for availability purpose
                    sh 'docker compose -f docker-compose.yml -p main_fitopia up -d'
                }
            }
        }
    }
}*/

pipeline {
    agent any
    stages {
        stage ('Checkout') {
            steps {
                git branch:'master', url: 'https://github.com/afiqdanialll/fitopiapublic.git'
            }
        }

        stage('Code Quality Check via SonarQube') {
            steps {
                script {
                def scannerHome = tool 'SonarQube';
                    withSonarQubeEnv('SonarQube') {
                    sh "/var/jenkins_home/tools/hudson.plugins.sonar.SonarRunnerInstallation/SonarQube/bin/sonar-scanner -Dsonar.projectKey=Fitopia -Dsonar.sources=. -Dsonar.host.url=http://192.168.86.108:9000 -Dsonar.token=sqp_57cf6637d96e72604aca99aff160869e8ac81ffc"
                    }
                }
            }
        }
    }
    post {
        always {
            recordIssues enabledForFailure: true, tool: sonarQube()
        }
    }
}
