#!/usr/bin/env python3

import os
import time
import random
import string

from aux import *

provisionFailMsg = "Failed to provision raw VMs. Check 'logs' file for details"
bootstrapFailMsg = "Failed to bootstrap '%s' k8s cluster. Check 'logs' file"


def runTerraform(mainTfDir, baseCWD, toLog, msg, autoApprove=True):
    """Run Terraform cmds.

    Parameters:
        mainTfDir (str): Path where the .tf file is.
        baseCWD (str): Path to go back.
        autoApprove (bool): If True (default) use '-auto-approve' option

    Returns:
        int: 0 for success, 1 for failure

    """
    writeToFile(toLog, msg, True)
    os.chdir(mainTfDir)
    beautify = "terraform fmt > /dev/null &&"
    tfCMD = 'terraform init && %s terraform apply -auto-approve' % beautify
    if autoApprove is False:
        tfCMD = 'terraform init && %s terraform apply' % beautify
    exitCode = runCMD(tfCMD)
    os.chdir(baseCWD)
    return exitCode


def cleanupTF(mainTfDir):
    """ Delete existing terraform stuff in the specified folder.
    """

    for filename in [
        "join.sh",
        "main.tf",
        "terraform.tfstate",
        "terraform.tfstate.backup",
            ".terraform"]:
        file = "%s/%s" % (mainTfDir, filename)
        if os.path.isfile(file):
            os.remove(file)
        if os.path.isdir(file):
            shutil.rmtree(file, True)


def stackVersioning(variables, configs):

    if configs["dockerCE"]:
        variables = variables.replace("DOCKER_CE_PH", str(configs["dockerCE"]))
    else:
        variables = variables.replace("DOCKER_CE_PH", "")

    if configs["dockerEngine"]:
        variables = variables.replace(
            "DOCKER_EN_PH", str(configs["dockerEngine"]))
    else:
        variables = variables.replace("DOCKER_EN_PH", "")

    if configs["kubernetes"]:
        variables = variables.replace("K8S_PH", str(configs["kubernetes"]))
    else:
        variables = variables.replace("K8S_PH", "")

    return variables


def terraformProvisionment(
        test,
        nodes,
        flavor,
        extraInstanceConfig,
        toLog,
        configs,
        testsRoot,
        retry,
        instanceDefinition,
        credentials,
        dependencies,
        baseCWD,
        provDict,
        extraSupportedClouds):
    """Provisions VMs on the provider side and creates a k8s cluster with them.

    Parameters:
        test (str): Indicates the test for which to provision the cluster
        nodes (int): Number of nodes the cluster must contain.
        flavor (str): Flavor to be used for the VMs.
        extraInstanceConfig (str): Extra HCL code to configure VM
        toLog (str): File to which write the log msg.
        configs ...
        testsRoot ...

    Returns:
        bool: True if the cluster was succesfully provisioned. False otherwise.
        str: Message informing of the provisionment task result.
    """

    templatesPath = "templates/"
    if configs["providerName"] in extraSupportedClouds:
        templatesPath += configs["providerName"]
    else:
        templatesPath += "general"

    mainTfDir = testsRoot + test
    kubeconfig = "config"
    if test == "shared":
        flavor = configs["flavor"]
        mainTfDir = testsRoot + "sharedCluster"
        os.makedirs(mainTfDir, exist_ok=True)
        kubeconfig = "~/.kube/config"

    # if retry is None:

    randomId = ''.join(
        random.SystemRandom().choice(
            string.ascii_lowercase +
            string.digits) for _ in range(4))  # One randomId per cluster
    nodeName = ("kubenode-%s-%s-%s" %
                (configs["providerName"], test, str(randomId))).lower()

    # ---------------- delete TF stuff from previous run if existing
    cleanupTF(mainTfDir)

    # ---------------- manage general variables

    # TODO: the schema validate must check configs' openUser: it is a required
    # property for providers that do not allow ssh with the root user (exoscale
    # would be the only one that allows root ssh)
    openUser = "" if configs['openUser'] is None else configs['openUser']

    str(configs['openUser'])

    variables = loadFile("templates/general/variables.tf",
                         required=True).replace(
        "NODES_PH", str(nodes)).replace(
        "PATH_TO_KEY_VALUE", str(configs["pathToKey"])).replace(
        "KUBECONFIG_DST", kubeconfig).replace(
        "OPEN_USER_PH", openUser).replace(
        "NAME_PH", nodeName)
    variables = stackVersioning(variables, configs)

    if configs["providerName"] == "azurerm":

        # manage image related vars
        publisher = "OpenLogic" if configs["image"]["publisher"] is None \
            else configs["image"]["publisher"]
        offer = "CentOS" if configs["image"]["offer"] is None \
            else configs["image"]["offer"]
        sku = "7.5" if configs["image"]["sku"] is None \
            else configs["image"]["sku"]
        version = "latest" if configs["image"]["version"] is None \
            else configs["image"]["version"]

        # ---------------- main.tf: manage azure specific vars and add them
        variables = variables.replace(
            "LOCATION_PH", configs['location']).replace(
            "PUB_SSH_PH", configs['pubSSH']).replace(
            "RGROUP_PH", configs['resourceGroupName']).replace(
            "RANDOMID_PH", randomId).replace(
            "VM_SIZE_PH", configs['flavor']).replace(
            "SECGROUPID_PH", configs['securityGroupID']).replace(
            "SUBNETID_PH", configs['subnetId']).replace(
            "PUBLISHER_PH", publisher).replace(
            "OFFER_PH", offer).replace(
            "SKU_PH", sku).replace(
            "VERSION_PH", version)
        writeToFile(mainTfDir + "/main.tf", variables, False)

        # ---------------- main.tf: add raw VMs provisioner
        rawProvisioning = loadFile(
            "%s/rawProvision.tf" % templatesPath, required=True)
        writeToFile(mainTfDir + "/main.tf", rawProvisioning, True)

    elif configs["providerName"] == "openstack":

        # manage optional related vars
        region = "" if configs["region"] is None \
            else configs["region"]
        availabilityZone = "" if configs["availabilityZone"] is None \
            else configs["availabilityZone"]
        securityGroups = "[]" if configs["securityGroups"] is None \
            else configs["securityGroups"]

        # ---------------- main.tf: manage openstack specific vars and add them
        variables = variables.replace(
            "FLAVOR_PH", configs['flavor']).replace(
            "IMAGE_PH", configs['imageName']).replace(
            "KEY_PAIR_PH", configs['keyPair']).replace(
            "\"SEC_GROUPS_PH\"", securityGroups).replace(
            "REGION_PH", region).replace(
            "AV_ZONE_PH", availabilityZone)
        writeToFile(mainTfDir + "/main.tf", variables, False)

        # ---------------- main.tf: add raw VMs provisioner
        rawProvisioning = loadFile(
            "%s/rawProvision.tf" % templatesPath, required=True)
        writeToFile(mainTfDir + "/main.tf", rawProvisioning, True)

    elif configs["providerName"] == "google":

        # manage gpu related vars
        gpuCount = str(nodes) if test == "dlTest" else "0"
        gpuType = configs["gpuType"] if test == "dlTest" else ""

        # ---------------- main.tf: manage google specific vars and add them
        variables = variables.replace(
            "CREDENTIALS_PATH_PH", configs['pathToCredentials']).replace(
            "PROJECT_PH", configs['project']).replace(
            "MACHINE_TYPE_PH", configs['flavor']).replace(
            "ZONE_PH", configs['zone']).replace(
            "IMAGE_PH", configs['image']).replace(
            "GPU_COUNT_PH", gpuCount).replace(
            "GPU_TYPE_PH", gpuType)
        writeToFile(mainTfDir + "/main.tf", variables, False)

        # ---------------- main.tf: add raw VMs provisioner
        rawProvisioning = loadFile(
            "%s/rawProvision.tf" % templatesPath, required=True)
        writeToFile(mainTfDir + "/main.tf", rawProvisioning, True)


    elif configs["providerName"] == "aws":

        # manage optional vars
        volumeSize = "" if configs["volumeSize"] is None \
            else str(configs["volumeSize"])

        # ---------------- main.tf: manage aws specific vars and add them
        variables = variables.replace(
            "REGION_PH", configs['region']).replace(
            "SHARED_CREDENTIALS_FILE_PH", configs['sharedCredentialsFile']).replace(
            "INSTANCE_TYPE_PH", configs['flavor']).replace(
            "AMI_PH", configs['ami']).replace(
            "NAME_KEY_PH", configs['keyName']).replace(
            "VOLUME_SIZE_PH", volumeSize)
        writeToFile(mainTfDir + "/main.tf", variables, False)

        # ---------------- main.tf: add raw VMs provisioner
        rawProvisioning = loadFile(
            "%s/rawProvision.tf" % templatesPath, required=True)
        writeToFile(mainTfDir + "/main.tf", rawProvisioning, True)


    elif configs["providerName"] == "cloudstack":


    elif configs["providerName"] == "exoscale":

        # manage optional related vars
        securityGroups = "[]" if configs["securityGroups"] is None \
            else configs["securityGroups"]

        # ---------------- main.tf: manage aws specific vars and add them
        variables = variables.replace(
            "CONFIG_PATH_PH", configs['configPath']).replace(
            "ZONE_PH", configs['zone']).replace(
            "EXO_SIZE_PH", configs['flavor']).replace(
            "TEMPLATE_PH", configs['template']).replace(
            "KEY_PAIR_PH", configs['keyPair']).replace(
            "\"SEC_GROUPS_PH\"", securityGroups).replace(
            "DISK_SIZE_PH", str(configs['diskSize']))
        writeToFile(mainTfDir + "/main.tf", variables, False)

        # ---------------- main.tf: add raw VMs provisioner
        rawProvisioning = loadFile(
            "%s/rawProvision.tf" % templatesPath, required=True)
        writeToFile(mainTfDir + "/main.tf", rawProvisioning, True)


    else:
        # ---------------- main.tf: add vars
        writeToFile(mainTfDir + "/main.tf", variables, False)

        # ---------------- main.tf: add raw VMs provisioner
        instanceDefinition = "%s \n %s" % (flavor, instanceDefinition.replace(
            "NAME_PH", "${var.instanceName}-${count.index}"
        ))

        if extraInstanceConfig:
            instanceDefinition += "\n" + extraInstanceConfig

        rawProvision = loadFile("%s/rawProvision.tf" % templatesPath).replace(
            "CREDENTIALS_PLACEHOLDER", credentials).replace(
            "DEPENDENCIES_PLACEHOLDER", dependencies.replace(
                "DEP_COUNT_PH", "count = %s" % nodes)).replace(
            "PROVIDER_NAME", str(configs["providerName"])).replace(
            "PROVIDER_INSTANCE_NAME", str(
                configs["providerInstanceName"])).replace(
            "NODE_DEFINITION_PLACEHOLDER", instanceDefinition)

        writeToFile(mainTfDir + "/main.tf", rawProvision, True)

    # ---------------- RUN TERRAFORM - phase 1: provision VMs
    if runTerraform(mainTfDir,
                    baseCWD,
                    toLog,
                    "Provisioning '%s' VMs..." % flavor) != 0:
        return False, provisionFailMsg

    # ---------------- main.tf: add root allower + k8s bootstraper
    bootstrap = loadFile("templates/general/bootstrap.tf", required=True)

    if configs['openUser'] is not None:
        bootstrap = bootstrap.replace("ALLOW_ROOT_COUNT", "var.customCount")
    else:
        bootstrap = bootstrap.replace("ALLOW_ROOT_COUNT", "0")

    bootstrap = bootstrap.replace(
        "LIST_IP_GETTER", provDict[configs["providerName"]])

    writeToFile(mainTfDir + "/main.tf", bootstrap, True)

    # if retry is True and os.path.isfile("main.tf") is False: # TODO: improve
    #    print("ERROR: run with option --retry before normal run.")
    #    stop(1)

    # ---------------- RUN TERRAFORM - phase 2: bootstrap the k8s cluster
    if runTerraform(mainTfDir,
                    baseCWD,
                    toLog,
                    "...bootstraping Kubernetes cluster...") != 0:
        return False, bootstrapFailMsg % flavor

    # ---------------- wait for default service account to be ready and finish
    kubeconfig = "~/.kube/config" if test == "shared" else "%s/%s" % (
        mainTfDir, kubeconfig)

    while runCMD(
        'kubectl --kubeconfig %s get sa default' %
        kubeconfig,
            hideLogs=True) != 0:
        time.sleep(1)

    writeToFile(toLog, "...'%s' CLUSTER CREATED => STARTING TESTS\n" %
                flavor, True)

    return True, ""
