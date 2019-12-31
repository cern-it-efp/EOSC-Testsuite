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
