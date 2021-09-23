#!/usr/bin/env python3

import sys
try:
    import os
    import time
    import string
    from multiprocessing import Process, Queue
    import contextlib
    import io
except ModuleNotFoundError as ex:
    print(ex)
    sys.exit(1)
from aux import *
from init import *
from kubernetesFunctions import *


def runTerraform(toLog,
                 cmd,
                 mainTfDir,
                 baseCWD,
                 test,
                 msg,
                 terraform_cli_vars=None):
    """ Run Terraform cmds.

    Parameters:
        toLog (str): File to which write the log msg.
        cmd (str): Command to be run.
        mainTfDir (str): Path where the .tf file is.
        baseCWD (str): Path to go back.
        test (str): Cluster identification.
        msg (str): Message to be shown.
        terraform_cli_vars (str): CLI vars to be appended to the cmd.

    Returns:
        int: 0 for success, 1 for failure
    """

    if terraform_cli_vars is not None:
        with open(mainTfDir + "/terraform.tfvars.json", 'w') as varfile:
            json.dump(terraform_cli_vars, varfile, indent=4, sort_keys=True)

    writeToFile(toLog, msg, True)
    os.chdir(mainTfDir)

    tfScript = """
    ((%s) && touch /tmp/validTFrun) |

    while read line; do echo [ %s ] $line; done

    if [ -f /tmp/validTFrun ]; then
    	rm -f /tmp/validTFrun
    	exit 0
    fi
    exit 1
    """ % (cmd, test)

    exitCode = runCMD(tfScript)
    os.chdir(baseCWD)
    return exitCode


def destroyTF(baseCWD, clusters=None):
    """ Destroy infrastructure. 'clusters' is an array whose objects specify
        the clusters that should be destroyed. In case no array is given, all
        clusters will be destroyed.

    Parameters:
        baseCWD (str): Path to go back.
        clusters (Array<str>): Clusters to destroy.

    Returns:
        Array<int>: 0 for success, 1 for failure
    """

    if clusters is None:
        clusters = ["shared", "dlTest", "hpcTest", "proGANTest"]

    res = []
    for cluster in clusters:
        toLog = "src/logging/footer"
        msg = "  -Destroying %s cluster..." % cluster
        mainTfDir = "src/tests/%s" % cluster
        cmd = "terraform destroy -auto-approve"
        exitCode = runTerraform(toLog, cmd, mainTfDir, baseCWD, cluster, msg)
        if exitCode == 0:
            if keepTFfiles is not True:
                cleanupTF("src/tests/%s/" % cluster)
            else:
                print("INFO: destroy succeed, tf files kept.")
        else:
            print("INFO: destroy did not succeed completely, tf files kept.")
        res.append(exitCode)

    return res


def cleanupTF(mainTfDir):
    """ Delete existing terraform stuff in the specified folder.

    Parameters:
        mainTfDir (str): Path to the .tf file.
    """

    for filename in [
        "hosts",
        "config",
        "main.tf",
        "versions.tf",
        "terraform.tfvars",
        "terraform.tfvars.json",
        "terraform.tfstate",
        "terraform.tfstate.backup",
        ".terraform.lock.hcl",
        ".terraform"]:
        file = "%s/%s" % (mainTfDir, filename)
        if os.path.isfile(file):
            os.remove(file)
        if os.path.isdir(file):
            shutil.rmtree(file, True)


def terraformProvisionment(
        test,
        nodes,
        flavor,
        toLog,
        configs,
        cfgPath,
        testsRoot,
        retry,
        baseCWD,
        extraSupportedClouds,
        usePrivateIPs):
    """ Provisions VMs on the provider.

    Parameters:
        test (str): Indicates the test for which to provision the cluster
        nodes (int): Number of nodes the cluster must contain.
        flavor (str): Flavor to be used for the VMs.
        toLog (str): File to which write the log msg.
        configs (dict): Object containing configs.yaml's configurations.
        cfgPath (str): Path to the configs file.
        testsRoot (str): Tests directory root.
        retry (bool): If true, retrying after a failure.
        baseCWD (str): Path to the base directory.
        extraSupportedClouds (dict): Extra supported clouds.
        usePrivateIPs (bool): If True, the current run is not using bastion.

    Returns:
        bool: True if the cluster was succesfully provisioned. False otherwise.
        str: Message informing of the provisionment task result.
    """

    templatesPath_base = "src/provisionment/tfTemplates/%s"
    templatesPath = templatesPath_base % configs["providerName"]

    ########### TODO: add OVH to Opentack's tf script
    if configs["providerName"] == "openstack" and configs["vendor"] == "ovh":
        templatesPath = templatesPath_base % "ovh"
    ###########

    mainTfDir = testsRoot + test
    terraform_cli_vars = {}
    kubeconfig = "%s/src/tests/%s/config" % (baseCWD, test)

    if retry is None:
        randomId = getRandomID() # One randomId per cluster

        nodeName = getNodeName(configs, test, randomId)

        # ---------------- delete TF stuff from previous run if existing
        cleanupTF(mainTfDir)

        # ---------------- variables
        variables = loadFile(templatesPath_base % "variables.tf",
                             required=True)
        writeToFile(mainTfDir + "/main.tf", variables, False)

        terraform_cli_vars["customCount"] = nodes
        terraform_cli_vars["dockerCE"] = tryTakeFromYaml(configs,
                                                         "dockerCE",
                                                         None)
        terraform_cli_vars["dockerEngine"] = tryTakeFromYaml(configs,
                                                             "dockerEngine",
                                                             None)
        terraform_cli_vars["kubernetes"] = tryTakeFromYaml(configs,
                                                           "kubernetes",
                                                           None)


        rawProvisioning = loadFile("%s/rawProvision.tf" % templatesPath,
                                   required=True)
        #print(rawProvisioning) # OK
        writeToFile(mainTfDir + "/main.tf", rawProvisioning, True)
        #print("\n %s" % open(mainTfDir + "/main.tf").read()) # FU

        terraform_cli_vars["configsFile"] = cfgPath
        terraform_cli_vars["flavor"] = flavor
        terraform_cli_vars["instanceName"] = nodeName

        if configs["providerName"] == "cloudsigma":

            staticIPs = tryTakeFromYaml(configs,"staticIPs",None)
            if staticIPs is not None:
                terraform_cli_vars["customCount"] = len(staticIPs)
                terraform_cli_vars["staticIPs"] = staticIPs

        if configs["providerName"] == "azurerm":

            terraform_cli_vars["clusterRandomID"] = randomId # var.clusterRandomID to have unique interfaces and disks names
            terraform_cli_vars["publisher"] = tryTakeFromYaml(
                                                configs,
                                                "image.publisher",
                                                "OpenLogic")
            terraform_cli_vars["offer"] = tryTakeFromYaml(
                                            configs,
                                            "image.offer",
                                            "CentOS")
            terraform_cli_vars["sku"] = str(tryTakeFromYaml(
                                                configs,
                                                "image.sku",
                                                7.5))
            terraform_cli_vars["imageVersion"] = str(tryTakeFromYaml(
                                                    configs,
                                                    "image.version",
                                                    "latest"))
            terraform_cli_vars["usePrivateIPs"] = usePrivateIPs

        if configs["providerName"] == "openstack":

            networkName = tryTakeFromYaml(configs, "networkName", False)
            if networkName is not False:
                terraform_cli_vars["useDefaultNetwork"] = False
            terraform_cli_vars["region"] = tryTakeFromYaml(configs,
                                                           "region",
                                                           None)
            terraform_cli_vars["availabilityZone"] = tryTakeFromYaml(
                                                        configs,
                                                        "availabilityZone",
                                                        None)
            terraform_cli_vars["region"] = tryTakeFromYaml(
                                                        configs,
                                                        "region",
                                                        None)
            terraform_cli_vars["authUrl"] = tryTakeFromYaml(
                                                        configs,
                                                        "authUrl",
                                                        None)

        if configs["providerName"] == "opentelekomcloud":

            networkID = tryTakeFromYaml(configs, "networkID", False)
            if networkID is not False:
                terraform_cli_vars["useDefaultNetwork"] = False
            terraform_cli_vars["availabilityZone"] = tryTakeFromYaml(
                                                        configs,
                                                        "availabilityZone",
                                                        None)

        if configs["providerName"] == "google":

            pathToPubKey = tryTakeFromYaml(configs,"pathToPubKey",None)
            if pathToPubKey is None:
                terraform_cli_vars["gcp_keyAsMetadata"] = "UseProjectWideKey!"
            else:
                terraform_cli_vars["gcp_keyAsMetadata"] = "%s:%s" % (configs["openUser"],loadFile(pathToPubKey))

            if test in ("dlTest", "proGANTest") :
                terraform_cli_vars["gpuCount"] = tryTakeFromYaml(configs,
                                                                "gpusPerNode",
                                                                1) # default is one
            else:
                terraform_cli_vars["gpuCount"] = "0"

            terraform_cli_vars["gpuType"] = tryTakeFromYaml(configs,
                                                            "gpuType",
                                                            "")

        if configs["providerName"] in ("aws", "google",
                            "openstack", "opentelekomcloud", "exoscale"):

            terraform_cli_vars["securityGroups"] = tryTakeFromYaml(
                                                    configs,
                                                    "securityGroups",
                                                    None)

        if configs["providerName"] in ("oci", "aws", "google", "azurerm"):

            terraform_cli_vars["storageCapacity"] = tryTakeFromYaml(
                                                        configs,
                                                        "storageCapacity",
                                                        None)


        # ---------------- RUN TERRAFORM: provision VMs
             # terraform 0.13upgrade -yes && \
        cmd = "terraform init && \
               terraform fmt > /dev/null && \
               terraform apply -auto-approve && \
               terraform refresh"
        if runTerraform("src/logging/%s" % test,
                        cmd,
                        mainTfDir,
                        baseCWD,
                        test,
                        "Provisioning %d '%s' VMs..." % (terraform_cli_vars["customCount"], flavor), # "Provisioning %d '%s' VMs..." % (nodes, flavor),
                        terraform_cli_vars=terraform_cli_vars) != 0:
            return False, provisionFailMsg

        return True, ""
