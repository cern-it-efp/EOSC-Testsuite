#!/usr/bin/env python3

from lib.checker import *
from lib.terraform import *
from lib.kubern8s import *    

def hpcTest(testsCatalog, onlyTest, configs, retry, instanceDefinition, 
credentials, dependencies, baseCWD, provDict, extraSupportedClouds, resDir, obtainCost):
    """HPC test."""

    start = time.time()
    testsRoot =  "../"
    hpc = testsCatalog["hpcTest"]
    if onlyTest is False:
        prov, msg = terraformProvisionment("hpcTest",
                                           hpc["nodes"],
                                           hpc["flavor"],
                                           None,
                                           "logging/hpcTest",
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
            writeFail(resDir, "hpcTest_result.json", msg, "logging/hpcTest")
            return
    else:
        if not checkCluster("hpcTest"):
            return  # Cluster not reachable, do not add cost for this test
    writeToFile("logging/hpcTest", "(to be done)", True)
    res = False

    if obtainCost is True:
        testCost = ((time.time() - start) / 3600) * \
            configs["costCalculation"]["HPCInstancePrice"] * hpc["nodes"]

    return  # if errors: finish run