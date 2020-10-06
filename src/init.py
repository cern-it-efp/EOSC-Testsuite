#!/usr/bin/env python3

from checker import *
from aux import *

configs = ""
testsCatalog = ""
cfgPath = None
tcPath = None
instanceDefinition = ""
extraInstanceConfig = ""
dependencies = ""
credentials = ""
testsRoot = "src/tests/"
allowAllTfClouds = False
baseCWD = os.getcwd()
defaultKubeconfig = "%s/src/tests/shared/config" % baseCWD
obtainCost = True
extraSupportedClouds = ["openstack",
                        "aws",
                        "azurerm",
                        "google",
                        "exoscale",
                        "cloudstack",
                        "opentelekomcloud",
                        "oci"]
testsSharingCluster = ["s3Test",
                       "dataRepatriationTest",
                       "perfsonarTest",
                       "cpuBenchmarking",
                       "dodasTest"]
customClustersTests = ["dlTest", "hpcTest", "proGANTest"]

bootstrapFailMsg = "Failed to bootstrap '%s' k8s cluster. Check 'logs' file"
clusterCreatedMsg = "...%s CLUSTER CREATED (masterIP: %s) => STARTING TESTS\n"
TOserviceAccountMsg = "ERROR: timed out waiting for %s cluster's service account\n"
destroyWarning = "WARNING - destroy infrastructure (%s)? yes/no: "
playbookPath = "src/provisionment/playbooks/bootstraper.yaml"
aggregateLogs = False
ansibleLogs = "src/logging/ansibleLogs%s"

provisionFailMsg = "Failed to provision raw VMs. Check 'logs' file for details"

publicRepo = "https://eosc-testsuite.rtfd.io"
clusters = ["shared", "dlTest", "hpcTest", "proGANTest"]


def initAndChecks(noTerraform,
                  extraSupportedClouds,
                  cfgPathCLI=None,
                  tcPathCLI=None):
    """ Initial checks and initialization of variables.

    Parameters:
        noTerraform (bool): Specifies whether current run uses terraform.
        extraSupportedClouds (dict): Extra supported clouds.
        cfgPath (str): Path to configs.yaml file.
        tcPath (str): Path to testsCatalog.yaml file.

    Returns:
        Arrayay(str): Array containing the selected tests.
    """

    global obtainCost
    global configs
    global cfgPath
    global tcPath
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

    if cfgPathCLI is None:
        cfgPath = "configurations/configs.yaml"
    else:
        cfgPath = cfgPathCLI
    if tcPathCLI is None:
        tcPath = "configurations/testsCatalog.yaml"
    else:
        tcPath = tcPathCLI

    configs = loadFile(cfgPath, required=True)
    testsCatalog = loadFile(tcPath, required=True)

    validateConfigs(configs, testsCatalog, noTerraform, extraSupportedClouds)

    if configs['providerName'] in ("oci", "opentelekomcloud"): # authFile validate (only YAML)
        authFile = loadFile(configs["authFile"], required=True)
        schema = loadFile("src/schemas/authFile_sch_%s.yaml" % configs["providerName"], required=True)
        validateAuth(authFile, schema)

    #if noTerraform is False and supportedProvider(configs) is False: # allows all terraform supporting providers to run w/o --no-terraform
    if noTerraform is False and configs['providerName'] not in extraSupportedClouds: # allows only providers in extraSupportedClouds to run w/o --no-terraform
        writeToFile("src/logging/header", "Provider '%s' not fully supported, run using '--no-terraform'" %
                    configs['providerName'], True)
        stop(1)

    # SSH key checks: exists and permissions set to 600
    if os.path.isfile(configs["pathToKey"]) is False:
        print("Key file not found at '%s'" % configs["pathToKey"])
        stop(1)
    if "600" not in oct(os.stat(configs["pathToKey"]).st_mode & 0o777):
        print("Key permissions must be set to 600")
        stop(1)


    # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    if allowAllTfClouds is True:
        instanceDefinition = loadFile("configurations/instanceDefinition")
        extraInstanceConfig = loadFile("configurations/extraInstanceConfig")
        dependencies = loadFile("configurations/dependencies")
        credentials = loadFile("configurations/credentials")
        if configs['providerName'] not in extraSupportedClouds \
                and "NAME_PH" not in instanceDefinition \
                and noTerraform is False:
            writeToFile(
                "src/logging/header",
                "ERROR: NAME_PH was not found in instanceDefinition file.",
                True)
            stop(1)
    # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------


    # --------Tests config checks
    selected = []

    for test in testsSharingCluster + customClustersTests:

        if testsCatalog[test]["run"] is True:
            selected.append(test)

            if test == "dlTest" or test == "proGANTest":
                instancePrice = tryTakeFromYaml(configs, "costCalculation.GPUInstancePrice", None)
            if test == "hpcTest":
                instancePrice = tryTakeFromYaml(configs, "costCalculation.HPCInstancePrice", None)
            else:
                instancePrice = tryTakeFromYaml(configs, "costCalculation.generalInstancePrice", None)

            if test == "s3Test":
                s3bucketPrice = tryTakeFromYaml(configs, "costCalculation.s3bucketPrice", None)
                obtainCost = checkCost(obtainCost, s3bucketPrice)

            obtainCost = checkCost(obtainCost, instancePrice)

    if obtainCost is not True:
        print("Cost estimation will not be provided.")

    if noTerraform is True:
        checkProvidedIPs(testsSharingCluster,
                         customClustersTests,
                         configs,
                         testsCatalog)

    return selected
