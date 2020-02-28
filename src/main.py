#!/usr/bin/env python3

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

from checker import *
from tests import *
import init


onlyTest = False
killResources = False
noTerraform = False
testsCatalog = ""
cfgPath = None
tcPath = None
instanceDefinition = ""
extraInstanceConfig = ""
dependencies = ""
credentials = ""
totalCost = 0
procs = []
viaBackend = False
testsSharingCluster = ["s3Test",
                       "dataRepatriationTest",
                       "perfsonarTest",
                       "cpuBenchmarking",
                       "dodasTest"]
customClustersTests = ["dlTest", "hpcTest"]
resultsExist = False

retry = None
destroy = None
destroyOnCompletion = None
clustersToDestroy = None
publicRepo = "https://eosc-testsuite.rtfd.io"
clusters = ["shared", "dlTest", "hpcTest"]


def header(noLogo=False, provider=None, results=None):
    """Prints the header according to parameters.

    Parameters:
        noLogo (bool): Specifies whether "EOSC" has to be shown or not.
        provider (str): Provider on which the suite is being run.
        results (str): Path to the results folder for the current run.
    """

    if noLogo is True:
        if provider is not None:
            if results is None:
                showThis = ["EOSC Cloud Validation Test Suite",
                    "Developed by CERN IT-EFP (ignacio.peluaga.lozada@cern.ch)",
                    ".........................................................",
                            "Provider: %s" % provider]
            else:
                showThis = ["EOSC Cloud Validation Test Suite",
                    "Developed by CERN IT-EFP (ignacio.peluaga.lozada@cern.ch)",
                    ".........................................................",
                    "Provider: %s" % provider,
                    "Results: results/%s" % results]
        else:
            showThis = ["EOSC Cloud Validation Test Suite",
                "Developed by CERN IT-EFP (ignacio.peluaga.lozada@cern.ch)",
                "........................................................."]

        logger(showThis, "#", "src/logging/header", override=True)
        if onlyTest is True:
            writeToFile("src/logging/header", "(ONLY TEST EXECUTION)", True)

    else:
        if provider is not None:
            if results is None:
                showThis = ["                 | Cloud Validation Test Suite",
                "█▀▀ █▀▀█ █▀▀ █▀▀ | Developed by CERN IT-EFP",
                "█▀▀ █  █  ▀▄ █   | Contact: ignacio.peluaga.lozada@cern.ch",
                "▀▀▀ ▀▀▀▀ ▀▀▀ ▀▀▀ | ..........................................",
                "  eosc-portal.eu | Provider: %s" % provider]
            else:
                showThis = ["                 | Cloud Validation Test Suite",
                "█▀▀ █▀▀█ █▀▀ █▀▀ | Developed by CERN IT-EFP",
                "█▀▀ █  █  ▀▄ █   | Contact: ignacio.peluaga.lozada@cern.ch",
                "▀▀▀ ▀▀▀▀ ▀▀▀ ▀▀▀ | ..........................................",
                "  eosc-portal.eu | Provider: %s" % provider,
                "                 | Results: results/%s" % results]
        else:
            showThis = ["                 | Cloud Validation Test Suite",
                "█▀▀ █▀▀█ █▀▀ █▀▀ | Developed by CERN IT-EFP",
                "█▀▀ █  █  ▀▄ █   | Contact: ignacio.peluaga.lozada@cern.ch",
                "▀▀▀ ▀▀▀▀ ▀▀▀ ▀▀▀ | ..........................................",
                "  eosc-portal.eu | "]

        # this fixes encode errors experienced in some clouds
        try:
            logger(showThis, "#", "src/logging/header", override=True)
            if onlyTest is True:
                writeToFile("src/logging/header",
                            "(ONLY TEST EXECUTION)", True)
        except:
            header(noLogo=True, provider=provider, results=results)


# logo, no results, no provider
header()

# -----------------CMD OPTIONS--------------------------------------------
try:
    options, values = getopt.getopt(
        sys.argv[1:],
        "c:t:",
        ["only-test", "via-backend", "retry", "destroy=",
        "destroy-on-completion=", "no-terraform", "configs=", "testsCatalog="])
except getopt.GetoptError as err:
    print(err)
    stop(1)
for currentOption, currentValue in options:
    if currentOption in ['-c', '--configs']:
        cfgPath = currentValue
        #print("Using configs path: %s" % cfgPath)
    elif currentOption in ['-t', '--testsCatalog']:
        tcPath = currentValue
        #print("Using testsCatalog path: %s" % tcPath)
    elif currentOption in ['--only-test']:
        writeToFile("src/logging/header", "(ONLY TEST EXECUTION)", True)
        onlyTest = True
    elif currentOption in ['--retry']:
        retry = True
    elif currentOption in ['--destroy']:
        if checkClustersToDestroy(currentValue, clusters):
            answer = input(
                "WARNING - destroy infrastructure (%s)? yes/no: " %
                currentValue)
            if answer == "yes":
                destroyTF(baseCWD, clusters=currentValue.split(','))
            else:
                print("Aborting operation")
        elif currentValue == "all":
            answer = input(
                "WARNING - destroy infrastructure (%s)? yes/no: " %
                currentValue)
            if answer == "yes":
                destroyTF(baseCWD, clusters=clusters)
            else:
                print("Aborting operation")
        else:
            print(
                "The provided value '%s' for the option " \
                "--destroy is not valid." % currentValue)
        stop(0)
    elif currentOption in ['--destroy-on-completion']:
        if checkClustersToDestroy(currentValue, clusters):
            destroyOnCompletion = True
            clustersToDestroy = currentValue.split(',')
        elif currentValue == "all":
            destroyOnCompletion = True
            clustersToDestroy = clusters
        else:
            print("The provided value '%s' for the option " \
            "--destroy-on-completion is not valid." % currentValue)
            stop(1)
    elif currentOption in ['--no-terraform']:
        noTerraform = True

# -----------------CHECKS AND PREPARATION---------------------------------

selectedTests = init.initAndChecks(noTerraform,
                                   extraSupportedClouds,
                                   testsSharingCluster,
                                   customClustersTests,
                                   cfgPath=cfgPath,
                                   tcPath=tcPath)

configs = init.configs
testsCatalog = init.testsCatalog

# logo, no results but provider
header(provider=configs["providerName"])


if not selectedTests:
    writeToFile("src/logging/header",
                "No tests selected, nothing to do!", True)
    stop(0)

if retry is True:
    checkRequiredTFexist(selectedTests)


# -----------------CREATE RESULTS FOLDER AND GENERAL FILE------------------
s3ResDirBase = configs["providerName"] + "/" + str(
    datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S"))
resDir = "results/%s/detailed" % s3ResDirBase
os.makedirs(resDir)
generalResults = {
    "testing": []
}

# logo with provider and results
header(provider=configs["providerName"], results=s3ResDirBase)


# -----------------RUN TESTS-----------------------------------------------
queue = Queue()
init.queue = queue
cluster = 1

msgArr = ["CLUSTER %s: (parallel running tests):" % (cluster)]
for test in testsSharingCluster:
    if testsCatalog[test]["run"] is True:
        msgArr.append(test)

if len(msgArr) > 1:
    p = Process(target=sharedClusterTests, args=( # shared cluster provisioning
        msgArr, onlyTest, retry, noTerraform, resDir))
    procs.append(p)
    p.start()
    cluster += 1

for test in customClustersTests:
    if testsCatalog[test]["run"] is True:
        logger("CLUSTER %s: %s" % (cluster, test),
               "=", "src/logging/%s" % test)
        p = Process(target=eval(test), args=( # custom clusters provisioning
            onlyTest, retry, noTerraform, resDir))
        procs.append(p)
        p.start()
        cluster += 1

for p in procs:  # All tests launched (functions run): wait for completion
    p.join()

while not queue.empty():
    entry, cost = queue.get()
    if entry:
        generalResults["testing"].append(entry)
    totalCost += cost

if checkResultsExist(resDir) is True:
    # -----------------CALCULATE COSTS-----------------------------------------
    if totalCost > 0:
        generalResults["estimatedCost"] = totalCost
    else:
        writeToFile(
            "src/logging/footer",
            "(Costs aren't correctly set: calculation will not be made)",
            True)

    # -----------------MANAGE RESULTS------------------------------------------
    with open("results/" + s3ResDirBase + "/general.json", 'w') as outfile:
        json.dump(generalResults, outfile, indent=4, sort_keys=True)

    msg1 = "TESTING COMPLETED"
    # No results push if local run (only ts-backend has AWS creds for this)
    if viaBackend is True:
        s3Endpoint = "https://s3.cern.ch"
        bucket = "s3://ts-results"
        pushResults = runCMD(
            "aws s3 cp --endpoint-url=%s %s %s/%s --recursive > /dev/null" %
            (s3Endpoint, "results/" + s3ResDirBase, bucket, s3ResDirBase))
        runCMD("cp results/%s/general.json .. " % s3ResDirBase)
        if pushResults != 0:
            logger("S3 upload failed! Is 'awscli' installed and configured?",
                   "!", "src/logging/footer")
        else:
            logger([msg1, "Results on the S3 bucket"],
                   "#", "src/logging/footer")
    else:
        logger(msg1, "*", "src/logging/footer")

    if destroyOnCompletion == True:
        for cluster in clustersToDestroy: # TODO: check here whether VMs for the cluster were indeed provisioned before trying to destroy them. Maybe use for that general.json
            if checkClusterWasProvisioned(cluster, generalResults["testing"]):
                if destroyTF(baseCWD, clusters=[cluster])[0] != 0:
                    msg = "   ...destroy failed. Check 'logs' file for details"
                else:
                    msg = "   ...cluster destroyed"
                writeToFile("src/logging/footer", msg, True)
else:

    # logo with provider, no results
    header(provider=configs["providerName"])
    shutil.rmtree("results/" + s3ResDirBase, True)


logger("Test-Suite run completed!", "#", "src/logging/end")
stop(0)
