#!/usr/bin/env python3

from checker import *
from aux import *

onlyTest = False
killResources = False
noTerraform = False
testsCatalog = ""
cfgPathCLI = None
tcPathCLI = None
freeMaster = False
usePrivateIPs = False
totalCost = 0
procs = []
publish = False
resultsExist = False
interactive = True
retry = None
destroy = None
destroyOnCompletion = None
clustersToDestroy = None
customNodes = None
s3Endpoint = "https://s3.cern.ch"
resultsBucket = "ocre-results" # "ts-results"

configs = ""
testsCatalog = ""
cfgPath = None
tcPath = None
testsRoot = "src/tests/"
baseCWD = os.getcwd()
defaultKubeconfig = "%s/src/tests/shared/config" % baseCWD
obtainCost = True
keepTFfiles = False
extraSupportedClouds = ["openstack",
                        "aws",
                        "azurerm",
                        "google",
                        "exoscale",
                        "opentelekomcloud",
                        "oci",
                        "ionoscloud",
                        "cloudsigma",
                        "ibm",
                        "layershift",
                        "flexibleengine",
                        "yandex"]
testsSharingCluster = ["s3Test",
                       "dataRepatriationTest",
                       "perfsonarTest",
                       "cpuBenchmarking",
                       "dodasTest"]
customClustersTests = ["dlTest", "hpcTest", "proGANTest"]
clusters = ["shared", "dlTest", "hpcTest", "proGANTest"]
allTests = testsSharingCluster + customClustersTests
playbookPath = "src/provisionment/playbooks/bootstraper.yaml"
aggregateLogs = False
ansibleLogs = "src/logging/ansibleLogs%s"
publicRepo = "https://eosc-testsuite.rtfd.io"

# ---- Messages
bootstrapFailMsg = "Failed to bootstrap '%s' k8s cluster. Check 'logs' file"
clusterCreatedMsg = "...%s CLUSTER CREATED (masterIP: %s) => STARTING TESTS\n"
TOserviceAccountMsg = "ERROR: timed out waiting for %s cluster's service account\n"
destroyWarning = "WARNING - destroy infrastructure (%s)? yes/no: "
provisionFailMsg = "Failed to provision raw VMs. Check 'logs' file for details"


def initAndChecks(noTerraform,
                  extraSupportedClouds,
                  onlyTest,
                  usePrivateIPs,
                  cfgPathCLI=None,
                  tcPathCLI=None):
    """ Initial checks and initialization of variables.

    Parameters:
        noTerraform (bool): Specifies whether current run uses terraform.
        extraSupportedClouds (dict): Extra supported clouds.
        onlyTest (str): If True the provisioning phase is skipped.
        usePrivateIPs (bool): If True, the current run is not using bastion.
        cfgPathCLI (str): Path to configs.yaml file.
        tcPathCLI (str): Path to testsCatalog.yaml file.

    Returns:
        Array(str): Array containing the selected tests.
    """

    global obtainCost
    global configs
    global cfgPath
    global tcPath
    global testsCatalog

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

    configs, testsCatalog = validateConfigs(cfgPath,
                                            tcPath,
                                            noTerraform,
                                            extraSupportedClouds,
                                            allTests)

    # authFile validattion (only YAML so no AWS and GCP)
    if configs['providerName'] in ("oci",
                                   "opentelekomcloud",
                                   "cloudsigma",
                                   "exoscale",
                                   "flexibleengine",
                                   "ibm",
                                   "ionoscloud"):
        authFile = loadFile(configs["authFile"], required=True)
        schema = loadFile("src/schemas/authFile_sch_%s.yaml" \
                % configs["providerName"], required=True)
        validateAuth(authFile, schema)

    if configs['providerName'] in ("azurerm") and usePrivateIPs is True:
        try:
            configs['subnetId']
        except:
            print("Used --usePrivateIPs but did not provide subnetId")
            stop(1)

    # allows only providers in extraSupportedClouds to run w/o --no-terraform
    if noTerraform is False and configs['providerName'] not in extraSupportedClouds:
        writeToFile("src/logging/header", "Provider '%s' not fully supported," \
            " run using '--no-terraform'" % configs['providerName'], True)
        stop(1)

    if onlyTest is False:
        # SSH key checks: exists and permissions set to 600
        if os.path.isfile(configs["pathToKey"]) is False:
            print("Key file not found at '%s'" % configs["pathToKey"])
            stop(1)
        if "600" not in oct(os.stat(configs["pathToKey"]).st_mode & 0o777):
            print("Key permissions must be set to 600")
            stop(1)

    # --------Tests config checks
    selected = []

    for test in allTests:

        if testsCatalog[test]["run"] is True:
            selected.append(test)

            if test == "dlTest" or test == "proGANTest":
                instancePrice = tryTakeFromYaml(configs,
                                        "costCalculation.GPUInstancePrice",
                                        None)
            elif test == "hpcTest":
                instancePrice = tryTakeFromYaml(configs,
                                        "costCalculation.HPCInstancePrice",
                                        None)
            else:
                instancePrice = tryTakeFromYaml(configs,
                                        "costCalculation.generalInstancePrice",
                                        None)

            if test == "s3Test":
                s3bucketPrice = tryTakeFromYaml(configs,
                                        "costCalculation.s3bucketPrice",
                                        None)
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
