#!/usr/bin/env groovy

def testSuiteParams = "";
def testNamesToRun = []
def testCounter = 0
def deleteFlag = false
def runs = [:]
def header = """
###################################################################
#                                                                 #
#      OCRE Cloud Benchmarking Validation Test Suite (CERN)       #
#                                                                 #
###################################################################
"""
def runSCM() {
  println "Cloning workspace from GitHub."
  cleanWs()
  git(
    url: 'git@github.com:cern-it-efp/OCRE-Testsuite.git',
    credentialsId: 'Jakub',
    branch: "jenkins"
  )
}

def runOCRETests(test) {
  println "Initiating test run with the name '${test}'"
  runSCM()

    dir ("$WORKSPACE/src") {
        sh "touch logging/${test}"
        sh "python3 -B run.py --${test} --configs ${YAML_ROOT}${YAML_CONFIG}.yaml --testsCatalog ${YAML_ROOT}testsCatalog.yaml"
    }
}

def runValidation(testSuiteParams) {
  dir ("$WORKSPACE/src") {
      sh "python3 -B validation.py ${testSuiteParams} --configs ${YAML_ROOT}${YAML_CONFIG}.yaml --testsCatalog ${YAML_ROOT}testsCatalog.yaml"
  }
}

def runClusterCreation(nodes) {
  dir ("$WORKSPACE/src") {
      sh "python3 -B cluster.py --create ${YAML_ROOT}${YAML_CONFIG}.yaml --nodes ${nodes}"
  }
}

def runClusterDeletion() {
  dir ("$WORKSPACE/src") {
      sh "python3 -B cluster.py -d"
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
            script{
              runSCM()
            }
          }
        }

        stage('Set-up') {
          steps {
            script{
                dir ("$WORKSPACE") {
                if (params.DELETE_CLUSTER) deleteFlag = true
                if (params.S3_TEST) {
                    testSuiteParams += "--s3Test " 
                    testNamesToRun.add("s3Test")
                    testCounter++
                }
                if (params.DL_TEST){
                  testSuiteParams += "--dlTest " 
                  testNamesToRun.add("dlTest")
                  testCounter++
                }
                if (params.PERF_SONAR_TEST){
                  testSuiteParams += "--perfSonarTest " 
                  testNamesToRun.add("perfSonarTest")
                  testCounter++
                }
                if (params.DODAS_TEST){
                  testSuiteParams += "--dodasTest " 
                  testNamesToRun.add("dodasTest")
                  testCounter++
                }
                if (params.DATA_REPARATION_TEST){
                  testSuiteParams += "--dataRepatriationTest " 
                  testNamesToRun.add("dataRepatriationTest")
                  testCounter++
                }
                if (params.CPU_BENCHMARKING_TEST){
                  testSuiteParams += "--cpuBenchmarkingTest" 
                  testNamesToRun.add("cpuBenchmarkingTest")
                  testCounter++
                }
                println "Run params var: $testSuiteParams"
                println "Amount of tests: $testCounter"
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
              script{
                if (testCounter > 0){
                  runValidation(testSuiteParams)
                } else {
                  println "No test selected. Nothing to validate."
                }
              }
            }
          }

          stage('Cluster creation') {
            steps {
              script{
                if (testCounter > 0){
                  runClusterCreation(testCounter)
                } else {
                  println "No test selected. Nothing to create."
                }
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

          stage('Cluster deletion') {
            steps {
              script{
                if (testCounter > 0){
                  if (deleteFlag){
                    runClusterDeletion()
                  } else {
                    println "Cluster deletion not selected. Leaving VM running."
                  }
                } else {
                  println "No test selected. Nothing to delete."
                }
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