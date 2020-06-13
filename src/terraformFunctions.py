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
        clusters = ["shared", "dlTest", "hpcTest"]

    res = []
    for cluster in clusters:
        toLog = "src/logging/footer"
        msg = "  -Destroying %s cluster..." % cluster
        mainTfDir = "src/tests/%s" % cluster
        cmd = "terraform destroy -auto-approve"
        exitCode = runTerraform(toLog, cmd, mainTfDir, baseCWD, cluster, msg)
        #if all(x == 0 for x in exitCode) is True:
        if exitCode is 0:
            cleanupTF("src/tests/%s/" % cluster)
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
        "terraform.tfvars",
        "terraform.tfvars.json",
        "terraform.tfstate",
        "terraform.tfstate.backup",
            ".terraform"]:
        file = "%s/%s" % (mainTfDir, filename)
        if os.path.isfile(file):
            os.remove(file)
        if os.path.isdir(file):
            shutil.rmtree(file, True)


def useGeneralTfTemplate(instanceDefinition,
                         flavor,
                         extraInstanceConfig,
                         tepmplatesPath,
                         credentials,
                         dependencies,
                         nodes,
                         configs):
    """ Uses the generic tfTemplate, which is populated with the HCL code the
        user provides as part of the configuration.

    Parameters:
        instanceDefinition (str): Instance definition.
        flavor (str): Machine flavor.
        extraInstanceConfig (str): Extra instance definition.
        tepmplatesPath (str): Path to the templates folder.
        credentials (src): Portion of HCL containing auth. stuff.
        dependencies (src): Dependencies related HCL.
        nodes (int): Number of nodes to be deployed.
        configs (dict): Content of the configs file.
    """

    instanceDefinition = "%s \n %s" % (flavor,instanceDefinition.replace(
        "NAME_PH", "${var.instanceName}-${count.index}"))

    if extraInstanceConfig:
        instanceDefinition += "\n" + extraInstanceConfig

    substitution = [
        {
            "before": "NODE_DEFINITION_PLACEHOLDER",
            "after": instanceDefinition
        },
        {
            "before": "DEPENDENCIES_PLACEHOLDER",
            "after": dependencies
        },
        {
            "before": "DEP_COUNT_PH",
            "after": "count = %s" % nodes
        },
        {
            "before": "PROVIDER_NAME",
            "after": str(configs["providerName"])
        },
        {
            "before": "PROVIDER_INSTANCE_NAME",
            "after": str(configs["providerInstanceName"])
        },
        {
            "before": "CREDENTIALS_PLACEHOLDER",
            "after": credentials
        }
    ]

    groupReplace("%s/rawProvision.tf" % templatesPath,
                 substitution,
                 "%s/main.tf" % mainTfDir)


def terraformProvisionment(
        test,
        nodes,
        flavor,
        extraInstanceConfig,
        toLog,
        configs,
        cfgPath,
        testsRoot,
        retry,
        instanceDefinition,
        credentials,
        dependencies,
        baseCWD,
        extraSupportedClouds):
    """ Provisions VMs on the provider and creates a k8s cluster with them.

    Parameters:
        test (str): Indicates the test for which to provision the cluster
        nodes (int): Number of nodes the cluster must contain.
        flavor (str): Flavor to be used for the VMs.
        extraInstanceConfig (str): Extra HCL code to configure VM
        toLog (str): File to which write the log msg.
        configs (dict): Object containing configs.yaml's configurations.
        cfgPath (str): Path to the configs file.
        testsRoot (str): Tests directory root.
        retry (bool): If true, retrying after a failure.
        instanceDefinition (str): HCL code definition of an instance.
        credentials (str): HCL code related to authentication/credentials.
        dependencies (str): HCL code related to infrastructure dependencies.
        baseCWD (str): Path to the base directory.
        extraSupportedClouds (dict): Extra supported clouds.

    Returns:
        bool: True if the cluster was succesfully provisioned. False otherwise.
        str: Message informing of the provisionment task result.
    """

    templatesPath_base = "src/provisionment/tfTemplates/%s"
    if configs["providerName"] in extraSupportedClouds:
        templatesPath = templatesPath_base % configs["providerName"]
    else:
        templatesPath = templatesPath_base % "general"

    mainTfDir = testsRoot + test
    terraform_cli_vars = {}
    cfgPath = "%s/%s" % (baseCWD, cfgPath)
    kubeconfig = "%s/src/tests/%s/config" % (baseCWD, test)

    if retry is None:
        randomId = getRandomID() # One randomId per cluster

        nodeName = getNodeName(configs, test, randomId)

        # ---------------- delete TF stuff from previous run if existing
        cleanupTF(mainTfDir)

        # ---------------- variables
        variables = loadFile(templatesPath_base % "general/variables.tf",
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

        if configs["providerName"] not in extraSupportedClouds:
            rawProvisioning = useGeneralTfTemplate()

        else:

            rawProvisioning = loadFile("%s/rawProvision.tf" % templatesPath,
                                       required=True)
            #print(rawProvisioning) # OK
            writeToFile(mainTfDir + "/main.tf", rawProvisioning, True)
            #print("\n %s" % open(mainTfDir + "/main.tf").read()) # FU

            terraform_cli_vars["configsFile"] = cfgPath
            terraform_cli_vars["flavor"] = flavor
            terraform_cli_vars["instanceName"] = nodeName

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

            if configs["providerName"] == "opentelekomcloud":

                networkID = tryTakeFromYaml(configs, "networkID", False)
                if networkID is not False:
                    terraform_cli_vars["useDefaultNetwork"] = False
                terraform_cli_vars["availabilityZone"] = tryTakeFromYaml(
                                                            configs,
                                                            "availabilityZone",
                                                            None)

            if configs["providerName"] == "google":

                if test == "dlTest":
                    terraform_cli_vars["gpuCount"] = nodes
                else:
                    terraform_cli_vars["gpuCount"] = "0"

                terraform_cli_vars["gpuType"] = tryTakeFromYaml(configs,
                                                                "gpuType",
                                                                None)

            if configs["providerName"] in ("aws", "cloudstack", "google",
                                "openstack", "opentelekomcloud", "exoscale"):

                terraform_cli_vars["securityGroups"] = tryTakeFromYaml(
                                                        configs,
                                                        "securityGroups",
                                                        None)

            if configs["providerName"] in ("cloudstack", "oci",
                                            "aws", "google"):

                terraform_cli_vars["storageCapacity"] = tryTakeFromYaml(
                                                            configs,
                                                            "storageCapacity",
                                                            None)


        # ---------------- RUN TERRAFORM: provision VMs
        beautify = "terraform fmt > /dev/null &&"
        cmd = "terraform init && %s terraform apply -auto-approve" % beautify
        if runTerraform("src/logging/%s" % test,
                        cmd,
                        mainTfDir,
                        baseCWD,
                        test,
                        "Provisioning '%s' VMs..." % flavor,
                        terraform_cli_vars=terraform_cli_vars) != 0:
            return False, provisionFailMsg

        return True, ""
