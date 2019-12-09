#!/usr/bin/env python3

import os
import sys

#jenkins library configuration
sys.path.append(os.path.abspath(os.environ['WORKSPACE'] + "/src/tests"))
sys.path.append(os.path.abspath(os.environ['WORKSPACE'] + "/src/tests/lib"))

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
    from multiprocessing import Process, Queue
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

test = ""
onlyTest = True
configs = ""
instanceDefinition = ""
dependencies = ""
credentials = ""
totalCost = 0
testsRoot = "tests/"
viaBackend = False
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

    logger(
    "OCRE Cloud Benchmarking Validation Test Suite (CERN)" + "\n" +
    "Running %s test..." % (test),
    "#",
    False)
    
    start = time.time()
    testCost = 0
    if not checkCluster("shared"):
        print("Cluster not reachable, do not add cost for this test")
        return
    print(eval('dir()'))
    print(eval(test, args=(testsCatalog, configs, resDir, obtainCost))) # Run the selected test
    if obtainCost is True:  # duration * instancePrice * numberOfInstances
        testCost = ((time.time() - start) / 3600) * \
            configs["costCalculation"]["generalInstancePrice"]
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
        test = "dataRepatriationTest"
    elif arg == '--cpuBenchmarkingTest':
        test = "cpuBenchmarkingTest"
    elif arg == '--perfSonarTest':
        test = "perfSonarTest"
    elif arg == '--dodasTest':
        test = "dodasTest"
    elif arg == '--s3Test':
        test = "s3Test"
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
totalCost = 0
cost = 0
cluster = 1
entry = ""

logger(
    "Running %s test..." % (test),
    "#",
    False)

logger("CLUSTER %s: %s" % (cluster, test), "=", False)
print(eval('dir()'))
# Run the selected test 
entry, cost = eval(test + '(testsCatalog, configs, resDir, obtainCost)')
# p = Process(target=eval(test))
# p.start()

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
