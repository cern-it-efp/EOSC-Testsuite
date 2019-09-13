#!/usr/bin/env python3

import os
import time
import random
import string

from aux import *

def runTerraform(mainTfDir, baseCWD):
    """Run Terraform cmds.

    Parameters:
        mainTfDir (str): Path where the .tf file is.
        baseCWD (str): Path to go back.

    Returns:
        int: 0 for success, 1 for failure

    """
    os.chdir(mainTfDir)
    beautify = "terraform fmt > /dev/null &&"
    exitCode = runCMD(
        'terraform init && %s terraform apply -auto-approve' % beautify)
    os.chdir(baseCWD)
    return exitCode


def terraformProvisionmentAzure(
        test,
        nodes,
        flavor,
        extraInstanceConfig,
        toLog):
    """Provisions VMs on azure and creates a k8s cluster with them."""

    mainTfDir = testsRoot + test
    kubeconfig = "config"
    if test == "shared":
        flavor = configs["flavor"]
        mainTfDir = testsRoot + "sharedCluster"
        os.makedirs(mainTfDir, exist_ok=True)
        kubeconfig = "~/.kube/config"

    # in order to have a single file for the infrastructure ("main.tf") put
    # variables at the  beginning of it
    randomId = ''.join(
        random.SystemRandom().choice(
            string.ascii_lowercase +
            string.digits) for _ in range(4))  # One randomId per cluster
    nodeName = ("kubenode-%s-%s-%s" %
                (configs["providerName"], test, str(randomId))).lower()
    variables = loadFile("templates/azure/variables.tf", required=True).replace(
        "OPEN_USER_PH", configs['openUser']).replace(
        "PATH_TO_KEY_VALUE", str(configs["pathToKey"])).replace(
        # ssh_connect.sh is always called from where the config file should be
        # placed, except for "shared", whose kubeconfig goes to ~/.kube/config
        # and not tests/sharedCluster/config
        "KUBECONFIG_DST", kubeconfig).replace(
        "LOCATION_PH", configs['location']).replace(
        "PUB_SSH_PH", configs['pubSSH']).replace(
        "RGROUP_PH", configs['resourceGroupName']).replace(
        "NODES_PH", str(nodes)).replace(
        "RANDOMID_PH", randomId).replace(
        "VM_SIZE_PH", configs['flavor']).replace(
        "SECGROUPID_PH", configs['securityGroupID']).replace(
        "SUBNETID_PH", configs['subnetId']).replace(
        "INSTANCE_NAME_PH", nodeName)

    # ------------------------- stack versioning
    variables = variables.replace(
        "DOCKER_CE_PH", str(
            configs["dockerCE"])) if configs["dockerCE"] else variables.replace(
        "DOCKER_CE_PH", "")
    variables = variables.replace(
        "DOCKER_EN_PH", str(
            configs["dockerEngine"])) if configs["dockerEngine"] else variables.replace(
        "DOCKER_EN_PH", "")
    variables = variables.replace(
        "K8S_PH", str(
            configs["kubernetes"])) if configs["kubernetes"] else variables.replace(
        "K8S_PH", "")

    writeToFile(mainTfDir + "/main.tf", variables, False)

    # Add VM provisionment to main.tf
    rawProvisioning = loadFile(
        "templates/azure/rawProvision.tf", required=True)
    writeToFile(mainTfDir + "/main.tf", rawProvisioning, True)

    # run terraform
    writeToFile(toLog, "Provisioning '" + flavor + "' VMs...", True)
    if runTerraform(mainTfDir, baseCWD) != 0:
        return False, "Failed to provision raw VMs. Check 'logs' file for details"

    # On completion of TF, add the bootstrap section to main.tf
    bootstrap = loadFile("templates/azure/bootstrap.tf", required=True)
    writeToFile(mainTfDir + "/main.tf", bootstrap, True)

    # Run terraform again
    writeToFile(toLog, "...bootstraping Kubernetes cluster...", True)
    if runTerraform(mainTfDir, baseCWD) != 0:
        return False, "Failed to bootstrap '%s' k8s cluster. Check 'logs' file " % flavor

    # ---------------- wait for default service account to be ready

    if test == "shared":  # TODO: improve this
        kubeconfig = "~/.kube/config"
    else:
        kubeconfig = "%s/%s" % (mainTfDir, kubeconfig)

    while runCMD(
        'kubectl --kubeconfig %s get sa default' %
        kubeconfig,
            hideLogs=True) != 0:
        time.sleep(1)

    writeToFile(toLog, "...'%s' CLUSTER CREATED => STARTING TESTS\n" %
                flavor, True)
    return True, ""


def terraformProvisionment(test, nodes, flavor, extraInstanceConfig, toLog, configs, testsRoot, retry, instanceDefinition, credentials, dependencies, baseCWD, provDict):
    """Provisions VMs on the provider side and creates a k8s cluster with them.

    Parameters:
        test (str): Indicates the test for which to provision the cluster
        nodes (int): Number of nodes the cluster must contain.
        flavor (str): Flavor to be used for the VMs.
        extraInstanceConfig (str): Extra HCL code to configure compute instance
        toLog (str): File to which write the log msg.
        configs ...
        testsRoot ...

    Returns:
        bool: True if the cluster was succesfully provisioned. False otherwise.
        str: Message informing of the provisionment task result.
    """

    # if configs["providerName"] in extraSupported:
    # return eval(extraSupported[configs["providerName"](test, nodes, flavor,
    # extraInstanceConfig, toLog))

    if configs["providerName"] == "azurerm":
        return terraformProvisionmentAzure(
            test, nodes, flavor, extraInstanceConfig, toLog)

    mainTfDir = testsRoot + test
    kubeconfig = "config" # kubeconfig = mainTfDir + "/config"
    if test == "shared":
        flavor = configs["flavor"]
        mainTfDir = testsRoot + "sharedCluster"
        os.makedirs(mainTfDir, exist_ok=True)
        kubeconfig = "~/.kube/config"

    if retry is None:
        randomId = ''.join(
            random.SystemRandom().choice(
                string.ascii_lowercase +
                string.digits) for _ in range(4))  # One randomId per cluster
        # ---------------- delete TF stuff from previous run if existing
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

        # ---------------- create provisioner main.tf file
        instanceDefinition = setName("%s \n %s" % (
            flavor, instanceDefinition), configs["providerName"], test, randomId)
        if extraInstanceConfig:
            instanceDefinition += "\n" + extraInstanceConfig

        mainStr = loadFile("terraform/main_raw").replace(
            "CREDENTIALS_PLACEHOLDER", credentials).replace(
            "DEPENDENCIES_PLACEHOLDER", dependencies.replace(
                "DEP_COUNT_PH", "count = %s" % nodes)).replace(
            "NODES_PH", str(nodes)).replace(
            "PROVIDER_NAME", str(configs["providerName"])).replace(
            "PROVIDER_INSTANCE_NAME", str(configs["providerInstanceName"])).replace(
            "NODE_DEFINITION_PLACEHOLDER", instanceDefinition)

        writeToFile(mainTfDir + "/main.tf", mainStr, False)

        writeToFile(toLog, "Provisioning '" + flavor + "' VMs...", True)
        if runTerraform(mainTfDir, baseCWD) != 0:
            return False, "Failed to provision raw VMs. Check 'logs' file for details"
        os.chdir(baseCWD)

        # ---------------- create bootstraper main.tf file: Vars + root allower + k8s bootstraper
        bootstrap = loadFile("terraform/bootstrap")

        if configs['openUser'] is not None:
            bootstrap = bootstrap.replace(
                "ALLOW_ROOT_PH", loadFile("terraform/allowRoot")).replace(
                "OPEN_USER_PH", configs['openUser']).replace(
                "ALLOW_ROOT_DEP_PH", "null_resource.allow_root")
        else:
            bootstrap = bootstrap.replace(
                "ALLOW_ROOT_PH", "").replace("ALLOW_ROOT_DEP_PH", "")

        bootstrap = bootstrap.replace(
            "PATH_TO_KEY_VALUE", str(configs["pathToKey"])).replace(
            "LIST_IP_GETTER", provDict[configs["providerName"]]).replace(
            "KUBECONFIG_DST", kubeconfig)

        # ------------------------- stack versioning
        bootstrap = bootstrap.replace("DOCKER_CE_PH", str(
            configs["docker-ce"])) if configs["dockerCE"] else bootstrap.replace("DOCKER_CE_PH", "")
        bootstrap = bootstrap.replace(
            "DOCKER_EN_PH", str(
                configs["dockerEngine"])) if configs["dockerEngine"] else bootstrap.replace(
            "DOCKER_EN_PH", "")
        bootstrap = bootstrap.replace(
            "K8S_PH", str(
                configs["kubernetes"])) if configs["kubernetes"] else bootstrap.replace(
            "K8S_PH", "")

        bootstrap = "\n" + bootstrap.replace(
            "PROVIDER_INSTANCE_NAME", str(
                configs["providerInstanceName"])).replace(
            "NODES_PH", str(nodes))
        writeToFile(mainTfDir + "/main.tf", bootstrap, True)

    # if retry is True and os.path.isfile("main.tf") is False: # TODO: improve
    #    print("ERROR: run with option --retry before normal run.")
    #    stop(1)

    # ---------------- locate where main.tf is and run terraform, use '-auto-approve'
    writeToFile(toLog, "...bootstraping Kubernetes cluster...", True)
    if runTerraform(mainTfDir, baseCWD) != 0:
        return False, "Failed to bootstrap '%s' k8s cluster. Check 'logs' file " % flavor

    # ---------------- wait for default service account to be ready
    if test == "shared":  # TODO: improve this
        kubeconfig = "~/.kube/config"
    else:
        kubeconfig = "%s/%s" % (mainTfDir, kubeconfig)

    while runCMD(
        'kubectl --kubeconfig %s get sa default' %
        kubeconfig,
            hideLogs=True) != 0:
        time.sleep(1)

    writeToFile(toLog, "...'%s' CLUSTER CREATED => STARTING TESTS\n" %
                flavor, True)
    return True, ""
