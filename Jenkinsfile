#!/usr/bin/env groovy

def testSuiteParams = "";
def testNamesToRun = []
def runs = [:]
def header = """
###################################################################
#                                                                 #
#      OCRE Cloud Benchmarking Validation Test Suite (CERN)       #
#                                                                 #
###################################################################
"""
def runOCRETests(test) {
  println "Initiating test run with the name '${test}'"
  cleanWs()
  git(
    url: 'git@github.com:cern-it-efp/OCRE-Testsuite.git',
    credentialsId: 'Jakub',
    branch: "jenkins"
  )

    dir ("$WORKSPACE/src") {
        sh "touch logging/${test}"
        sh "python3 -B run.py --${test}"
    }
}

pipeline {
    agent any
    options {
        parallelsAlwaysFailFast()
    }
    stages {
        stage('SCM') {
          steps {
            cleanWs()
            git(
              url: 'git@github.com:cern-it-efp/OCRE-Testsuite.git',
              credentialsId: 'Jakub',
              branch: "jenkins"
            )
          }
        }

        stage('Set-up') {
          steps {
            script{
                dir ("$WORKSPACE") {
                if (params.ONLY_TEST) testSuiteParams = "--only-test "
                if (params.VIA_BACKEND) testSuiteParams += "--via-backend "
                if (params.RETRY) testSuiteParams += "--retry " 
                if (params.S3_TEST) {
                    testSuiteParams += "--s3Test " 
                    testNamesToRun.add("s3Test")
                }
                if (params.DL_TEST){
                  testSuiteParams += "--dlTest " 
                  testNamesToRun.add("dlTest")
                }
                if (params.PERF_SONAR_TEST){
                  testSuiteParams += "--perfSonarTest " 
                  testNamesToRun.add("perfSonarTest")
                }
                if (params.DODAS_TEST){
                  testSuiteParams += "--dodasTest " 
                  testNamesToRun.add("dodasTest")
                }
                if (params.DATA_REPARATION_TEST){
                  testSuiteParams += "--dataRepatriationTest " 
                  testNamesToRun.add("dataRepatriationTest")
                }
                if (params.CPU_BENCHMARKING_TEST){
                  testSuiteParams += "--cpuBenchmarkingTest" 
                  testNamesToRun.add("cpuBenchmarkingTest")
                }
                println "this is run params var: $testSuiteParams"
              }

            testNamesToRun.each { name -> 
                runs[name] = {
                  node {
                     stage(name) {
                        runOCRETests(name)
                     }
                  }
                }
            }

            }
          }
        }

        stage('Validation') {
          steps {
            dir ("$WORKSPACE/src") {
            sh "python3 -B validation.py $testSuiteParams"
            }
          }
        }

        stage('Tests Execution') {
          steps {
            script {
              println header
              parallel runs
            }
          }
        }

        stage('Tear Down') {
          steps {
            cleanWs()
          }
        }
    }
}  