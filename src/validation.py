#!/usr/bin/env python3

import os
import sys

#jenkins library configuration
sys.path.append(os.path.abspath(os.environ['WORKSPACE'] + "/src/tests"))
sys.path.append(os.path.abspath(os.environ['WORKSPACE'] + "/src/tests/lib"))

from tests.lib.checker import *
from tests.lib.terraform import *
from tests.lib.kubern8s import *

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

#tests to be run (will be updated from CMD in the run)
dataRepatriationTest = False
cpuBenchmarkingTest = False
perfSonarTest = False
dodasTest = False
hpcTest = False
dlTest = False
s3Test = False

def validateYaml(provider):
    """ Validates configs.yaml and testsCatalog.yaml file against schemas.

    Parameters:
        provider (str): Provider on which the suite is being run. According to
                        it a specific YAML schema is used.
    """

    configsSchema = "schemas/configs_sch_%s.yaml" % provider if provider \
        in extraSupportedClouds else "schemas/configs_sch.yaml"

    try:
        jsonschema.validate(configs, loadFile(configsSchema))
    except jsonschema.exceptions.ValidationError as ex:
        print("Error validating configs.yaml: \n %s" % ex)
        stop(1)

    try:
        jsonschema.validate(
            testsCatalog,
            loadFile("schemas/testsCatalog_sch.yaml"))
    except jsonschema.exceptions.ValidationError as ex:
        print("Error validating testsCatalog.yaml: \n %s" % ex)
        stop(1)


def initAndChecks(configs, testsCatalog, instanceDefinition, 
                    extraInstanceConfig, dependencies, credentials, obtainCost):
    """Initial checks and initialization of variables.

    Returns:
        Array(str): Array containing the selected tests (strings)
    """

    # --------File check
    if runCMD("terraform version", hideLogs=True) != 0:
        print("Terraform is not installed")
        stop(1)
    if runCMD("kubectl", hideLogs=True) != 0:
        print("kubectl is not installed")
        stop(1)

    # SSH key checks: exists and permissions set to 600
    if os.path.isfile(configs["pathToKey"]) is False:
        print("Key file not found at '%s'" % configs["pathToKey"])
        stop(1)
    if "600" not in oct(os.stat(configs["pathToKey"]).st_mode & 0o777):
        print("Key permissions must be set to 600")
        stop(1)

    if configs['providerName'] not in provDict:
        writeToFile("logging/header", "Provider '%s' not supported" %
                    configs['providerName'], True)
        stop(1)

    # --------General config checks
    if configs['providerName'] not in extraSupportedClouds \
            and "NAME_PH" not in instanceDefinition:
        writeToFile(
            "logging/header",
            "ERROR: NAME_PH was not found in instanceDefinition file.",
            True)
        stop(1)

    # --------Tests config checks
    selected = []
    if s3Test is True:
        print("s3Test has been selected to be validated.")
        selected.append("s3Test")
        obtainCost = checkCost(
            obtainCost,
            configs["costCalculation"]["generalInstancePrice"])
        obtainCost = checkCost(
            obtainCost, configs["costCalculation"]["s3bucketPrice"])

    if perfSonarTest is True:
        print("perfSonarTest has been selected to be validated.")
        selected.append("perfsonarTest")
        obtainCost = checkCost(
            obtainCost,
            configs["costCalculation"]["generalInstancePrice"])

    if dataRepatriationTest is True:
        print("dataRepatriationTest has been selected to be validated.")
        selected.append("dataRepatriationTest")
        obtainCost = checkCost(
            obtainCost,
            configs["costCalculation"]["generalInstancePrice"])

    if cpuBenchmarkingTest is True:
        print("cpuBenchmarking has been selected to be validated.")
        selected.append("cpuBenchmarking")
        obtainCost = checkCost(
            obtainCost,
            configs["costCalculation"]["generalInstancePrice"])

    if dlTest is True:
        print("dlTest has been selected to be validated.")
        selected.append("dlTest")
        obtainCost = checkCost(
            obtainCost, configs["costCalculation"]["GPUInstancePrice"])

    if hpcTest is True:
        print("hpcTest has been selected to be validated.")
        selected.append("hpcTest")
        obtainCost = checkCost(
            obtainCost, configs["costCalculation"]["GPUInstancePrice"])

    if dodasTest is True:
        print("dodasTest has been selected to be validated.")
        selected.append("dodasTest")
        obtainCost = checkCost(
            obtainCost,
            configs["costCalculation"]["generalInstancePrice"])

# -----------------CMD OPTIONS--------------------------------------------
try:
    options, remainder = getopt.getopt(sys.argv[1:],
                "c:tc", ["--s3Test", "--perfSonarTest", "--dataRepatriationTest", 
                    "--cpuBenchmarkingTest", "--dodasTest", "configs=", "testsCatalog="])
except getopt.GetoptError as err:
    print(err)
    stop(1)

for opt, arg in options:
    if opt in ('-c', '--configs'):
        configs = arg
        print("Using configs path: " + arg)
    elif opt in ('-tc', '--testsCatalog'):
        testsCatalog = arg
        print("Using testsCatalog path: " + arg)
    elif opt in ('-d', '--destroy'):
        mode = "destroy"
    elif opt == '--dataRepatriationTest':
        dataRepatriationTest = True
    elif opt == '--cpuBenchmarkingTest':
        cpuBenchmarkingTest = True
    elif opt == '--perfSonarTest':
        perfSonarTest = True
    elif opt == '--dodasTest':
        dodasTest = True
    elif opt == '--s3Test':
        s3Test = True
    else:
        print("Bad option '%s'." % arg)
        stop(1)

# -----------------CONFIGURE PATHS ---------------------------------------
print("About to set paths to the config files.")
provDict = loadFile("schemas/provDict.yaml",
                    required=True)["allProviders"]
extraSupportedClouds = loadFile("schemas/provDict.yaml",
                                required=True)["extraSupportedClouds"] 

# TODO: instanceDefinition is now only required when not running on main clouds
instanceDefinition = loadFile("/var/jenkins_home/configurations/instanceDefinition")
extraInstanceConfig = loadFile("/var/jenkins_home/configurations/extraInstanceConfig")
dependencies = loadFile("/var/jenkins_home/configurations/dependencies")
credentials = loadFile("/var/jenkins_home/configurations/credentials")

# ----------------VALIDATION AND INIT RUN---------------------------------
# disabled schema validation for testing
# validateYaml(configs["providerName"], extraSupportedClouds)
print("About to run the required checks.")
initAndChecks(configs, testsCatalog, instanceDefinition, 
                extraInstanceConfig, dependencies, credentials, True)