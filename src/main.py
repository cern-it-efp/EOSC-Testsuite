#!/usr/bin/env python3

import sys
try:
    import yaml
    import json
    from multiprocessing import Process, Queue
    import argparse
    import jsonschema
    import os
    import datetime
    import time
    import subprocess
    import string
    import re
    import shutil
    import boto3

except ModuleNotFoundError as ex:
    print(ex)
    sys.exit(1)

from checker import *
from tests import *
import init


def header(noLogo=False, provider=None, results=None):
    """ Prints the header according to parameters.

    Parameters:
        noLogo (bool): Specifies whether "EOSC" has to be shown or not.
        provider (str): Provider on which the suite is being run.
        results (str): Path to the results folder for the current run.
    """

    if noLogo is True:
        if provider is not None:
            if results is None:
                showThis = ["EOSC Cloud Validation Test Suite",
                    "Developed by CERN IT-EFP (ignacio.peluaga.lozada AT cern.ch)",
                    ".........................................................",
                            "Cloud: %s" % provider]
            else:
                showThis = ["EOSC Cloud Validation Test Suite",
                    "Developed by CERN IT-EFP (ignacio.peluaga.lozada AT cern.ch)",
                    ".........................................................",
                    "Cloud: %s" % provider,
                    "Results: results/%s" % results]
        else:
            showThis = ["EOSC Cloud Validation Test Suite",
                "Developed by CERN IT-EFP (ignacio.peluaga.lozada AT cern.ch)",
                "........................................................."]

        logger(showThis, "#", "src/logging/header", override=True)
        if onlyTest is True:
            writeToFile("src/logging/header", "(ONLY TEST EXECUTION)", True)

    else:
        if provider is not None:
            if results is None:
                showThis = ["                 | Cloud Validation Test Suite",
                "█▀▀ █▀▀█ █▀▀ █▀▀ | Developed by CERN IT-EFP",
                "█▀▀ █  █  ▀▄ █   | Contact: ignacio.peluaga.lozada AT cern.ch",
                "▀▀▀ ▀▀▀▀ ▀▀▀ ▀▀▀ | ..........................................",
                "  eosc-portal.eu | Cloud: %s" % provider]
            else:
                showThis = ["                 | Cloud Validation Test Suite",
                "█▀▀ █▀▀█ █▀▀ █▀▀ | Developed by CERN IT-EFP",
                "█▀▀ █  █  ▀▄ █   | Contact: ignacio.peluaga.lozada AT cern.ch",
                "▀▀▀ ▀▀▀▀ ▀▀▀ ▀▀▀ | ..........................................",
                "  eosc-portal.eu | Cloud: %s" % provider,
                "                 | Results: results/%s" % results]
        else:
            showThis = ["                 | Cloud Validation Test Suite",
                "█▀▀ █▀▀█ █▀▀ █▀▀ | Developed by CERN IT-EFP",
                "█▀▀ █  █  ▀▄ █   | Contact: ignacio.peluaga.lozada AT cern.ch",
                "▀▀▀ ▀▀▀▀ ▀▀▀ ▀▀▀ | ..........................................",
                "  eosc-portal.eu | "]

        # this fixes encode errors experienced in some clouds
        try:
            logger(showThis, "#", "src/logging/header", override=True)
            if onlyTest is True:
                writeToFile("src/logging/header", "(ONLY TEST EXECUTION)", True)
        except BaseException as e:
            print("EOSC logo exception: " + str(e))
            header(noLogo=True, provider=provider, results=results)


def uploadDirectory(path, bucketName, client_s3):
    """ Uploads objects one by one to a CERN S3 bucket.

    Parameters:
        path (str): Path were the S3 results are located.
        bucketName (str): Name of the bucket.
        client_s3 (): boto3 client.

    Returns:
        bool: Operation result, True is success.
    """

    for root, dirs, files in os.walk("results/" + path):
        for file in files:
            try:
                currentResource = os.path.join(root, file)
                client_s3.upload_file(currentResource,
                                      bucketName,
                                      currentResource.replace("results/",""))
            except:
                return False
    return True


def publishResults(s3ResDirBase):
    """ Uploads objects (run results) one by one to a CERN S3
        bucket, maintaining the local file structure.

    Parameters:
        s3ResDirBase (str): Local path to the run results.

    Returns:
        bool: Operation result, True is success.
    """

    aws_access_key_id = os.environ.get('S3_ACC_KEY')
    aws_secret_access_key = os.environ.get('S3_SEC_KEY')
    endpoint_url = os.environ.get('S3_ENDPOINT', s3Endpoint)

    print(aws_secret_access_key)
    print(aws_access_key_id)

    if aws_access_key_id == None or aws_secret_access_key == None:
        print("WARNING: no credentials were provided, the results will not be published.")
        return False

    client_s3=boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        endpoint_url=endpoint_url
    )

    for root, dirs, files in os.walk("results/" + s3ResDirBase):
        for file in files:
            try:
                currentResource = os.path.join(root, file)
                client_s3.upload_file(currentResource,
                                      resultsBucket,
                                      currentResource.replace("results/",""))
            except:
                return False
    return True


# logo, no results, no provider
header()

# -----------------CMD OPTIONS--------------------------------------------
parser = argparse.ArgumentParser(prog="./test_suite",
                                 description='EOSC Test-Suite.',
                                 allow_abbrev=False)
parser.add_argument('-y',
                    help='No interactive (TBD).',
                    action='store_false',
                    dest="interactive")
parser.add_argument('-o','--onlyTest',
                    help='Only test run.',
                    action='store_true')
parser.add_argument('--usePrivateIPs',
                    help='Use private IPs.',
                    action='store_true')
parser.add_argument('--noTerraform',
                    help='Skip Terraform, run only Ansible.',
                    action='store_true')
parser.add_argument('-c','--configs',
                    help='Path to configs.',
                    type=str,
                    dest="cfgPathCLI")
parser.add_argument('-t','--testsCatalog',
                    help='Path to tests catalog.',
                    metavar="CATALOG",
                    type=str,
                    dest="tcPathCLI")
parser.add_argument('--destroy',
                    nargs='+',
                    dest="clustersToDestroy",
                    help='Destroy infrastructure.',
                    metavar="CLUSTERS",
                    choices=['all']+clusters,
                    type=str)
parser.add_argument('--destroyOnCompletion',
                    nargs='+',
                    dest="clustersToDestroyOnCompletion",
                    help='Destroy infrastructure at the end of the run.',
                    metavar="CLUSTERS",
                    choices=['all']+clusters)
parser.add_argument('--customNodes',
                    help='Use a specific amount of nodes.',
                    metavar="NODES",
                    type=int)
parser.add_argument('--noWatch',
                    help='Do not use the watch function.',
                    action='store_true')
parser.add_argument('--publish',
                    help='Push results to CERN S3.',
                    action='store_true')
parser.add_argument('--freeMaster',
                    help='Do not allow running tests on the master node.',
                    action='store_true')

args = parser.parse_args()

if args.cfgPathCLI:
    cfgPathCLI = os.path.abspath(args.cfgPathCLI)
if args.tcPathCLI:
    tcPathCLI = os.path.abspath(args.tcPathCLI)
if args.interactive:
    interactive = args.interactive # disables prompts of overriding tf files and deleting infrastructure
if args.onlyTest:
    onlyTest = args.onlyTest
if args.usePrivateIPs:
    usePrivateIPs = args.usePrivateIPs
if args.customNodes:
    customNodes = args.customNodes
if args.noTerraform:
    noTerraform = True
if args.publish:
    publish = True
if args.freeMaster:
    freeMaster = True
if args.clustersToDestroy:
    clustersToDestroy = args.clustersToDestroy
    if "all" in clustersToDestroy:
        clustersToDestroy = clusters
    if interactive is False:
        destroyTF(baseCWD, clusters=clustersToDestroy)
    elif input(destroyWarning % clustersToDestroy) == "yes":
        destroyTF(baseCWD, clusters=clustersToDestroy)
    else:
        print("Aborting operation")
    stop(0)
if args.clustersToDestroyOnCompletion:
    clustersToDestroy = args.clustersToDestroyOnCompletion
    if "all" in clustersToDestroy:
        clustersToDestroy = clusters
    destroyOnCompletion = True


# -----------------CHECKS AND PREPARATION---------------------------------
selectedTests = init.initAndChecks(noTerraform,
                                   extraSupportedClouds,
                                   usePrivateIPs,
                                   cfgPathCLI=cfgPathCLI,
                                   tcPathCLI=tcPathCLI)

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
    if customNodes is not None:
        numberOfNodes = customNodes
    else:
        if freeMaster:
            numberOfNodes = len(msgArr) # No test/bmk will be deployed on the master node, hence an extra node.
        else:
            numberOfNodes = len(msgArr) - 1
    p = Process(target=sharedClusterTests, args=( # shared cluster provisioning
                                                msgArr,
                                                onlyTest,
                                                retry,
                                                noTerraform,
                                                resDir,
                                                numberOfNodes,
                                                usePrivateIPs,
                                                freeMaster))
    procs.append(p)
    p.start()
    cluster += 1

for test in customClustersTests:
    if testsCatalog[test]["run"] is True:
        logger("CLUSTER %s: %s" % (cluster, test),
               "=", "src/logging/%s" % test)
        p = Process(target=eval(test), args=( # custom clusters provisioning
                                            onlyTest,
                                            retry,
                                            noTerraform,
                                            resDir,
                                            usePrivateIPs,
                                            freeMaster))
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

    generalResults["info"] = configs
    generalResults["testsCatalog"] = testsCatalog

    with open("results/" + s3ResDirBase + "/general.json", 'w') as outfile:
        json.dump(generalResults, outfile, indent=4, sort_keys=True)

    msg1 = "TESTING COMPLETED"

    # -----------------S3 RESULTS UPLOAD---------------------------------------
    if publish is True:
        if publishResults(s3ResDirBase) is False:
            logger("S3 upload failed!", "!", "src/logging/footer")
        else:
            logger(["TESTING COMPLETED", "S3 upload OK"],"#", "src/logging/footer")
    else:
        logger(msg1, "*", "src/logging/footer")

    # -----------------RESOURCES DESTROY---------------------------------------
    if destroyOnCompletion is True:
        for cluster in clustersToDestroy:
            if checkClusterWasProvisioned(cluster, generalResults["testing"]):
                if destroyTF(baseCWD, clusters=[cluster])[0] != 0:
                    msg = "   ...destroy failed. Check 'logs' file for details"
                else:
                    msg = "   ...cluster destroyed"
                writeToFile("src/logging/footer", msg, True)
    else:
        writeToFile("src/logging/footer", "No destroy scheduled", True)

else:

    # logo with provider, no results
    header(provider=configs["providerName"])
    shutil.rmtree("results/" + s3ResDirBase, True)


logger("Run completed", "#", "src/logging/end")
stop(0)
