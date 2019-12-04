#!/usr/bin/env python3

from tests.lib.aux import *
from tests.lib.checker import *
from tests.lib.terraform import *
from tests.lib.kubern8s import *

from tests.dataRepatriationTest import *
from tests.cpuBenchmarkingTest import *
from tests.perfSonarTest import *
from tests.dodasTest import *
from tests.hpcTest import *
from tests.dlTest import *
from tests.s3Test import *

import sys
try:
    import yaml
    import json
    import getopt
    import jsonschema
    import os
    import datetime
    import time
    import subprocess
    import string
    import re
    import shutil

except ModuleNotFoundError as ex:
    print(ex)
    sys.exit(1)

#tests to be run (will be updated from CMD in the run)
dataRepatriationTest = False
cpuBenchmarkingTest = False
perfSonarTest = False
dodasTest = False
hpcTest = False
dlTest = False
s3Test = False

logger(
    "OCRE Cloud Benchmarking Validation Test Suite (CERN)",
    "#",
    "logging/header")

onlyTest = False
configs = ""
instanceDefinition = ""
dependencies = ""
credentials = ""
totalCost = 0
testsRoot = "tests/"
viaBackend = False
testsSharingCluster = ["s3Test", "dataRepatriationTest",
                       "perfsonarTest", "cpuBenchmarking", "dodasTest"]
customClustersTests = ["dlTest", "hpcTest"]
baseCWD = os.getcwd()
resultsExist = False
provDict = loadFile("schemas/provDict.yaml",
                    required=True)["allProviders"]
extraSupportedClouds = loadFile("schemas/provDict.yaml",
                                required=True)["extraSupportedClouds"]
obtainCost = True
retry = None
publicRepo = "https://ocre-testsuite.rtfd.io"

def sharedClusterTests(test):
    """Runs the test that shared the general purpose cluster.

    Parameters:
        msgArray (Array<str>): Stuff to show on the banner. Contains the
                               tests to be deployed on the shared cluster.

    Returns:
        None: In case of errors the function stops (returns None)
    """

    start = time.time()
    testCost = 0
    logger(msgArr, "=", "logging/shared")
    if onlyTest is False:
        # minus 1 because the array contains the string message
        prov, msg = terraformProvisionment("shared",
                                           len(msgArr) - 1,
                                           None,
                                           None,
                                           "logging/shared",
                                           configs,
                                           testsRoot,
                                           retry,
                                           instanceDefinition,
                                           credentials,
                                           dependencies,
                                           baseCWD,
                                           provDict,
                                           extraSupportedClouds)
        if prov is False:
            writeFail(resDir, "sharedCluster_result.json",
                      msg, "logging/shared")
            return
    else:
        if not checkCluster("shared"):
            return  # Cluster not reachable, do not add cost for this test
    eval(test, args=(testsCatalog, configs, resDir, obtainCost)) # Run the selected test
    if obtainCost is True:  # duration * instancePrice * numberOfInstances
        testCost = ((time.time() - start) / 3600) * \
            configs["costCalculation"]["generalInstancePrice"] * \
            len(msgArr[1:])
    return (None, testCost)

# -----------------CMD OPTIONS--------------------------------------------
try:
    opts, args = getopt.getopt(
        sys.argv, "ul", ["--only-test", "--via-backend", "--retry"])
except getopt.GetoptError as err:
    writeToFile("logging/header", err, True)
    stop(1)
for arg in args[1:len(args)]:
    if arg == '--only-test':
        writeToFile("logging/header", "(ONLY TEST EXECUTION)", True)
        #runCMD("kubectl delete pods --all", hideLogs=True)
        onlyTest = True
    elif arg == '--dataRepatriationTest':
        dataRepatriationTest = True
    elif arg == '--cpuBenchmarkingTest':
        cpuBenchmarkingTest = True
    elif arg == '--perfSonarTest':
        perfSonarTest = True
    elif arg == '--dodasTest':
        dodasTest = True
    elif arg == '--hpcTest':
        hpcTest = True
    elif arg == '--dlTest':
        dlTest = True
    elif arg == '--s3Test':
        s3Test = True
    elif arg == '--retry':
        retry = True
    else:
        writeToFile("logging/header", "Bad option '%s'. Docs at %s " %
                    (arg, publicRepo), True)
        stop(1)


# -----------------CONFIGURE PATHS ---------------------------------------
print("About to set paths to the config files.")
configs = loadFile("/var/jenkins_home/configurations/configs.yaml", required=True)
testsCatalog = loadFile(
        "/var/jenkins_home/configurations/testsCatalog.yaml", required=True)

provDict = loadFile("schemas/provDict.yaml",
                    required=True)["allProviders"]
extraSupportedClouds = loadFile("schemas/provDict.yaml",
                                required=True)["extraSupportedClouds"] 

publicRepo = "https://ocre-testsuite.rtfd.io"                                       

# TODO: instanceDefinition is now only required when not running on main clouds
instanceDefinition = loadFile("/var/jenkins_home/configurations/instanceDefinition")
extraInstanceConfig = loadFile("/var/jenkins_home/configurations/extraInstanceConfig")
dependencies = loadFile("/var/jenkins_home/configurations/dependencies")
credentials = loadFile("/var/jenkins_home/configurations/credentials")

# ----------------CREATE RESULTS FOLDER AND GENERAL FILE------------------
print("About to create results folder and general file.")
s3ResDirBase = configs["providerName"] + "/" + str(
    datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S"))
resDir = "../results/%s/detailed" % s3ResDirBase
os.makedirs(resDir)
generalResults = {
    "testing": []
}

# ----------------RUN TESTS-----------------------------------------------
cluster = 1
entry = ""

msgArr = ["CLUSTER %s: (parallel running tests):" % (cluster)]
for test in testsSharingCluster:
    if test is True:
        entry, cost = sharedClusterTests(test)
        cluster += 1

for test in customClustersTests:
    if test is True:
        logger("CLUSTER %s: %s" % (cluster, test), "=", "logging/%s" % test)
        entry, cost = eval(test)
        cluster += 1

if entry:
    generalResults["testing"].append(entry)
totalCost += cost

if checkResultsExist(resDir) is True:
    # ----------------CALCULATE COSTS-----------------------------------------
    if totalCost > 0:
        generalResults["estimatedCost"] = totalCost
    else:
        writeToFile(
            "logging/footer",
            "(Costs aren't correctly set: calculation will not be made)",
            True)

    # ----------------MANAGE RESULTS------------------------------------------
    with open("../results/" + s3ResDirBase + "/general.json", 'w') as outfile:
        json.dump(generalResults, outfile, indent=4, sort_keys=True)

    msg1 = "TESTING COMPLETED. Results at:"
    # No results push if local run (only ts-backend has AWS creds for this)
    if viaBackend is True:
        s3Endpoint = "https://s3.cern.ch"
        bucket = "s3://ts-results"
        pushResults = runCMD(
            "aws s3 cp --endpoint-url=%s %s %s/%s --recursive > /dev/null" %
            (s3Endpoint, "../results/" + s3ResDirBase, bucket, s3ResDirBase))
        runCMD("cp ../results/%s/general.json .. " % s3ResDirBase)
        if pushResults != 0:
            logger("S3 upload failed! Is 'awscli' installed and configured?",
                   "!", "logging/footer")
        else:
            logger([msg1, "S3 bucket"], "#", "logging/footer")
    else:
        logger([msg1, "results/" + s3ResDirBase], "#", "logging/footer")
else:
    shutil.rmtree("../results/" + s3ResDirBase, True)

stop(0)
