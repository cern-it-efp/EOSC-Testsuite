#!/usr/bin/env python3

import os
from aux import *


def checkCost(obtainCost, value):
    """ Checks the provided value is not None and is greater than 0.

    Parameters:
        obtainCost: Flag indicating if the cost can be calculated.
        value: Value to be checked.

    Returns:
        bool: True in case the given value can be used for cost estimation.
    """

    return value >= 0 and obtainCost is True if value else False


def checkDLsupport():
    """Check whether infrastructure supports DL.

    Returns:
        bool: True in case cluster supports DL, False otherwise.
    """

    pods = runCMD(
        'kubectl --kubeconfig tests/dlTest/config get pods -n kubeflow',
        read=True)
    return len(pods) > 0 and "No resources found." not in pods


def checkResultsExist(resDir):
    """Checks results exist inside the results dir created for the current run.

    Parameters:
        resDir (str): Path to the folder to check

    Returns:
        bool: True in case results exist. False otherwise.
    """

    for dirpath, dirnames, files in os.walk(resDir):
        return len(files) > 0


def checkProvidedIPs(testsSharingCluster, customClustersTests, configs, testsCatalog):
    """Checks, when the option '--no-terraform' has been used that the
       IPs for the selected tests were provided at testsCatalog.yaml

    Parameters:
        testsSharingCluster (Array<str>): Tests sharing general purpose cluster.
        customClustersTests (Array<str>): Tests using custom dedicated clusters.
        configs (dict): Object containing configs.yaml's configurations.
        testsCatalog (dict): Object containing testsCatalog.yaml's content.
    """

    for test in testsSharingCluster:
        if testsCatalog[test]["run"] is True:
            try:
                configs["clusters"]["shared"]
                break
            except KeyError as ex:
                print("IPs missing at configs.yaml for the shared cluster.")
                stop(1)

    for test in customClustersTests:
        if testsCatalog[test]["run"] is True:
            try:
                configs["clusters"][test]
            except KeyError as ex:
                print("IPs missing at configs.yaml for %s." % test)
                stop(1)


def checkRequiredTFexist(selectedTests):
    """Called when --retry option is used, checks the main.tf files exist for
       the required tests: those with run: true at testsCatalog.yaml

    Parameters:
        selectedTests (Array<str>): Array containing the selected tests.
    """

    pathToMain = "src/tests/%s/main.tf"

    if ("s3Test" in selectedTests or
            "dataRepatriationTest" in selectedTests or
            "cpuBenchmarking" in selectedTests or
            "perfsonarTest" in selectedTests or
            "dodasTest" in selectedTests) \
            and os.path.isfile(pathToMain % "shared") is False:
        writeToFile("src/logging/header",
                    "ERROR: terraform files not found for shared cluster. "
                    "\nNormal run is required before run with '--retry'.", True)
        stop(1)

    if "dlTest" in selectedTests and not os.path.isfile(pathToMain % "dlTest"):
        writeToFile("src/logging/header",
                    "ERROR: terraform files not found for dlTest. "
                    "\nNormal run is required before run with '--retry'.", True)
        stop(1)

    if "hpcTest" in selectedTests and not os.path.isfile(pathToMain % "hpcTest"):
        writeToFile("src/logging/header",
                    "ERROR: terraform files not found for hpcTest. "
                    "\nNormal run is required before run with '--retry'.", True)
        stop(1)


def checkClustersToDestroy(cliParameterValue, clusters):
    """Checks the given argument matches cluster to be destroyed

    Parameters:
        cliParameterValue (str): CLI arguments.
        clusters (Array<str>): Array containing 'shared','dlTest' and 'hpcTest'.

    Returns:
        bool: True in case the given argument is correct. False otherwise.
    """

    try:
        for value in cliParameterValue.split(','):
            if value not in clusters:
                return False
    except:
        return False
    return True
