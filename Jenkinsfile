pipeline {
  agent any

  environment {
    PYTHON = 'python3'
    VENV = '.venv'
  }

  stages {
    stage('Prepare') {
      steps {
        // create and activate venv
        sh "${env.PYTHON} -m venv ${env.VENV}"
        sh ". ${env.VENV}/bin/activate && python -m pip install --upgrade pip"
      }
    }

    stage('Install build deps') {
      steps {
        // install runtime deps and build tooling
        sh ". ${env.VENV}/bin/activate && pip install -r requirements.txt build wheel setuptools"
      }
    }

    stage('Build') {
      steps {
        // build sdist and wheel
        sh ". ${env.VENV}/bin/activate && python -m build"
      }
    }

    stage('Install artifact') {
      steps {
        // install the newly-built wheel into the venv for smoke tests
        sh ". ${env.VENV}/bin/activate && python -m pip install dist/*.whl"
      }
    }

    stage('Smoke test') {
      steps {
        // run a simple import check
        sh ". ${env.VENV}/bin/activate && python scripts/smoke_test.py"
      }
    }

    stage('Archive') {
      steps {
        archiveArtifacts artifacts: 'dist/**', fingerprint: true
      }
    }
  }

  post {
    always {
      echo 'Cleaning up environment'
      sh 'rm -rf .venv'
    }
  }
}
