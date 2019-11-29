#!/usr/bin/env python3

import os
import sys

#jenkins library configuration
sys.path.append(os.path.abspath("./lib/"))
from lib.aux import *

try:
    import jsonschema

except ModuleNotFoundError as ex:
    print(ex)
    sys.exit(1)    

def validateYaml(provider, extraSupportedClouds, configs, testsCatalog):
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

def checkCost(obtainCost, value):
    """ Checks the provided value is not None and is greater than 0.

    Parameters:
        value: Value to be checked.
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
