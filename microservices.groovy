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



}

}
}

}
