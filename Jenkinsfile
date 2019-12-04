#!/usr/bin/env groovy

def testSuiteParams = "";
def testNamesToRun = []

node{
    stage('SCM') {
        cleanWs()
        git(
           url: 'git@github.com:cern-it-efp/OCRE-Testsuite.git',
           credentialsId: 'Jakub',
           branch: "jenkins"
        )
    }

    stage('Set-up') {
        script{
            dir ("$WORKSPACE/src/logging") {
            sh "rm -f header killMe footer hpcTest dlTest shared logs"
            sh "touch logs run.txt"

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
      }
    }

    stage('Validation') {
        dir ("$WORKSPACE/src") {
        sh "python3 -B validation.py $testSuiteParams"
        }
    }
}

    def runs = [:]
    testNamesToRun.each { name -> 
        runs[name] = node {
            stage(name) {
                runOCRETests(name)
            }
        }
    }

    def runOCRETests(test) {
      println "Initiating test run with the name '${test}'"
      dir ("$WORKSPACE/src") {
        sh "python3 -B run.py --${test}"
      }
    }

    currentBuild.result = 'SUCCESS'
    try{
      runs.failFast = true
      parallel runs
    } catch (Exception err) {
      println "ERROR: ${err.message}"
      if (currentBuild.rawBuild.getActions(jenkins.model.InterruptedBuildAction.class).isEmpty()) {
          currentBuild.result = 'FAILURE'
      } else {
          currentBuild.result = 'ABORTED'
      }
    } finally {
        // smtp server needs to be configured in order to be able send notification mails
        emailext body: "${currentBuild.currentResult}: Job ${env.JOB_NAME} build ${env.BUILD_NUMBER} \n More info at: ${env.BUILD_URL}",
            recipientProviders: [[$class: 'DevelopersRecipientProvider'], [$class: 'RequesterRecipientProvider']],
            subject: "Jenkins Build ${currentBuild.currentResult}: Job ${env.JOB_NAME}"
        // destroy all VMs
        
    }   