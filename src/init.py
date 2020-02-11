#!/usr/bin/env python3

from checker import *


configs = ""
testsCatalog = ""
instanceDefinition = ""
extraInstanceConfig = ""
dependencies = ""
credentials = ""
testsRoot = "src/tests/"
baseCWD = os.getcwd()
provDict = loadFile("src/schemas/provDict.yaml",
                    required=True)["allProviders"]
extraSupportedClouds = loadFile("src/schemas/provDict.yaml",
                                required=True)["extraSupportedClouds"]
obtainCost = True

def initAndChecks(noTerraform, extraSupportedClouds, testsSharingCluster, customClustersTests, cfgPath=None, tcPath=None):
    """Initial checks and initialization of variables.

    Returns:
        Array(str): Array containing the selected tests (strings)
    """

    global obtainCost
    global configs
    global testsCatalog
    global instanceDefinition
    global extraInstanceConfig
    global dependencies
    global credentials

    # --------File & deps check
    if runCMD("terraform version", hideLogs=True) != 0:
        print("Terraform is not installed")
        stop(1)
    if runCMD("kubectl", hideLogs=True) != 0:
        print("kubectl is not installed")
        stop(1)

    if cfgPath is None:
        cfgPath = "configurations/configs.yaml"
    if tcPath is None:
        tcPath = "configurations/testsCatalog.yaml"

    configs = loadFile(cfgPath, required=True)
    testsCatalog = loadFile(tcPath, required=True)

    # SSH key checks: exists and permissions set to 600
    if os.path.isfile(configs["pathToKey"]) is False:
        print("Key file not found at '%s'" % configs["pathToKey"])
        stop(1)
    if "600" not in oct(os.stat(configs["pathToKey"]).st_mode & 0o777):
        print("Key permissions must be set to 600")
        stop(1)

    validateYaml(configs, testsCatalog, noTerraform, extraSupportedClouds)

    instanceDefinition = loadFile("%s/instanceDefinition" % cfgPath) # TODO: these would fail when using '-c'
    extraInstanceConfig = loadFile("%s/extraInstanceConfig" % cfgPath)
    dependencies = loadFile("%s/dependencies" % cfgPath)
    credentials = loadFile("%s/credentials" % cfgPath)

    #if configs['providerName'] not in provDict: # TODO: since we will give support to providers that do not support terraform (like cloudsigma) this check has to be moved to the case --no-terraform is not used
    #    writeToFile("src/logging/header", "Provider '%s' not supported" %
    #                configs['providerName'], True)
    #    stop(1)

    # --------General config checks
    if configs['providerName'] not in extraSupportedClouds \
            and "NAME_PH" not in instanceDefinition \
            and noTerraform is False:
        writeToFile(
            "src/logging/header",
            "ERROR: NAME_PH was not found in instanceDefinition file.",
            True)
        stop(1)

    # --------Tests config checks
    selected = []
    if testsCatalog["s3Test"]["run"] is True:
        selected.append("s3Test")
        obtainCost = checkCost(
            obtainCost,
            configs["costCalculation"]["generalInstancePrice"])
        obtainCost = checkCost(
            obtainCost, configs["costCalculation"]["s3bucketPrice"])

    if testsCatalog["perfsonarTest"]["run"] is True:
        selected.append("perfsonarTest")
        obtainCost = checkCost(
            obtainCost,
            configs["costCalculation"]["generalInstancePrice"])

    if testsCatalog["dataRepatriationTest"]["run"] is True:
        selected.append("dataRepatriationTest")
        obtainCost = checkCost(
            obtainCost,
            configs["costCalculation"]["generalInstancePrice"])

    if testsCatalog["cpuBenchmarking"]["run"] is True:
        selected.append("cpuBenchmarking")
        obtainCost = checkCost(
            obtainCost,
            configs["costCalculation"]["generalInstancePrice"])

    if testsCatalog["dlTest"]["run"] is True:
        selected.append("dlTest")
        obtainCost = checkCost(
            obtainCost, configs["costCalculation"]["GPUInstancePrice"])

    if testsCatalog["hpcTest"]["run"] is True:
        selected.append("hpcTest")
        obtainCost = checkCost(
            obtainCost, configs["costCalculation"]["GPUInstancePrice"])

    if testsCatalog["dodasTest"]["run"] is True:
        selected.append("dodasTest")
        obtainCost = checkCost(
            obtainCost,
            configs["costCalculation"]["generalInstancePrice"])

    if noTerraform is True:
        checkProvidedIPs(selected, testsSharingCluster, customClustersTests, configs, testsCatalog)

    return selected
