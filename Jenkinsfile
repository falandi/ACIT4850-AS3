def call() {
pipeline {
agent any
stages {
stage('Build') {
steps {
sh 'pip install -r requirements.txt'
         }
    }
stage('Python Lint'){
steps {
    sh 'pylint-fail-under --fail_under 5.0 *.py'
    }
}

stage('Unit Test') { 
steps { 
    
    script {
        def test_reports_exist = fileExists 'test-reports'
        if (test_reports_exist) {
            sh 'rm test-reports/*.xml || true'
        }
        def api_test_reports_exist = fileExists 'api-test-reports'
        if (api_test_reports_exist) {
            sh 'rm api-test-reports/*.xml || true'
        }

        def test_reports_car_exist = fileExists 'test-reports-car'
        if (test_reports_car_exist) {
            sh 'rm test-reports-car/*.xml || true'
        }

         def test_reports_instructor_exist = fileExists 'test-reports-instructor'
        if (test_reports_instructor_exist) {
            sh 'rm test-reports-instructor/*.xml || true'
        }

    }
    
    script {
        def files = findFiles(glob: 'test*.py')
        for (file in files){
            sh "coverage run --omit */site-packages/*,*/dist-packages/* ${file}"
            sh 'coverage report' 
        }

    }
    
    script {
        def test_reports_exist = fileExists 'test-reports'
            if (test_reports_exist) {
                junit 'test-reports/*.xml'
            }
        def api_test_reports_exist = fileExists 'api-test-reports'
            if (api_test_reports_exist) {
                junit 'api-test-reports/*.xml'
            }

        def test_reports_car_exist = fileExists 'test-reports-car'
            if (test_reports_car_exist) {
                junit 'test-reports-car/*.xml'
            }

        def test_reports_instructor_exist = fileExists 'test-reports-instructor'
            if (test_reports_instructor_exist) {
                junit 'test-reports-instructor/*.xml'
            }

    }
  
   
} 

}

stage('Zip Artifacts') {
steps{
    script {
        sh 'zip -r app.zip *.py'
    }
    
    script{
        archiveArtifacts artifacts: 'app.zip',
                   allowEmptyArchive: true,
                   fingerprint: true,
                   onlyIfSuccessful: true
    }

    
    
}
}

}
}

}
#beep boop
