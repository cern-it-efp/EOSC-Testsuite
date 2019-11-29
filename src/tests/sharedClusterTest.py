#!/usr/bin/env python3

from lib.checker import *
from lib.terraform import *
from lib.kubern8s import *  

from multiprocessing import Process

def sharedClusterTest(msgArr, onlyTest, configs, retry, instanceDefinition, credentials, dependencies, 
baseCWD, provDict, extraSupportedClouds, obtainCost, resDir):
    """Runs the test that shared the general purpose cluster.

    Parameters:
        msgArray (Array<str>): Stuff to show on the banner. Contains the
                               tests to be deployed on the shared cluster.

    Returns:
        None: In case of errors the function stops (returns None)
    """

    start = time.time()
    sharedClusterProcs = []
    testCost = 0
    testsRoot =  "../"
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
    for test in msgArr[1:]:
        p = Process(target=eval(test))
        sharedClusterProcs.append(p)
        p.start()
    for p in sharedClusterProcs:
        p.join()
    if obtainCost is True:  # duration * instancePrice * numberOfInstances
        testCost = ((time.time() - start) / 3600) * \
            configs["costCalculation"]["generalInstancePrice"] * \
            len(msgArr[1:])