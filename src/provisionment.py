#!/usr/bin/env python3


import sys
try:
    import os
    import time
    import random
    import string
    from ansible.module_utils.common.collections import ImmutableDict
    from ansible.parsing.dataloader import DataLoader
    from ansible.vars.manager import VariableManager
    from ansible.inventory.manager import InventoryManager
    from ansible import context
    from ansible.cli import CLI
    from ansible.executor.playbook_executor import PlaybookExecutor
    from configparser import ConfigParser
    import threading
    from multiprocessing import Process, Queue
    import contextlib
    import io
except ModuleNotFoundError as ex:
    print(ex)
    sys.exit(1)
from aux import *
from init import *


provisionFailMsg = "Failed to provision raw VMs. Check 'logs' file for details"
bootstrapFailMsg = "Failed to bootstrap '%s' k8s cluster. Check 'logs' file"
playbookPath = "src/provisionment/playbooks/bootstraper.yaml"
msgRoot = "WARNING: default user 'root' for ssh connections (running on %s)"

aggregateLogs = False
ansibleLogs = "src/logging/ansibleLogs%s"


def runTerraform(toLog, cmd, mainTfDir, baseCWD, test, msg, terraform_cli_vars=None):
    """Run Terraform cmds.

    Parameters:
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
    """Destroy infrastructure. 'clusters' is an array whose objects specify
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
            print("WARNING: terraform destroy did not succeed completely, tf files not deleted.")
        res.append(exitCode)

    return res


def cleanupTF(mainTfDir):
    """Delete existing terraform stuff in the specified folder.

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


def waitForSA(kubeconfig):
    """Wait for cluster's service account to be ready.

    Parameters:
        kubeconfig (str): Path to a kubeconfig file.

    Returns:
        int: 0 for success, 1 for failure
    """

    res = 1
    for i in range(15):
        if runCMD(
            'kubectl --kubeconfig %s get sa default' % kubeconfig,
                hideLogs=True) == 0:
            res = 0
            break
        time.sleep(2)
    return res


def provisionAndBootstrap(test,
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
                          provDict,
                          extraSupportedClouds,
                          noTerraform):
    """Provision infrastructure and/or bootstrap the k8s cluster.

    Parameters:
        test (str): Indicates the test for which to provision the cluster
        nodes (int): Number of nodes the cluster must contain.
        flavor (str): Flavor to be used for the VMs.
        extraInstanceConfig (str): Extra HCL code to configure VM
        toLog (str): File to which write the log msg.
        configs (dict): Object containing configs.yaml's configurations.
        testsRoot (str): Tests directory root.
        retry (bool): If true, retrying after a failure.
        instanceDefinition (str): HCL code definition of an instance.
        credentials (str): HCL code related to authentication/credentials.
        dependencies (str): HCL code related to infrastructure dependencies.
        baseCWD (str): Path to the base directory.
        provDict (dict): Dictionary containing the supported clouds.
        extraSupportedClouds (dict): Extra supported clouds.

    Returns:
        bool: True if the cluster was succesfully provisioned. False otherwise.
        str: Message informing of the provisionment task result.
    """

    if noTerraform is True:  # Only ansible
        mainTfDir = testsRoot + test
        kubeconfig = "%s/src/tests/%s/config" % (baseCWD, test)  # "config"


        openUser = tryTakeFromYaml(configs,
                                   "openUser",
                                   "root",
                                   msgExcept=msgRoot % configs["providerName"])

        if test == "shared":
            mainTfDir = testsRoot + "shared"
            os.makedirs(mainTfDir, exist_ok=True)
            kubeconfig = "~/.kube/config"
        result, masterIP = ansiblePlaybook(mainTfDir,
                                           baseCWD,
                                           configs["providerName"],
                                           kubeconfig,
                                           noTerraform,
                                           test,
                                           configs["pathToKey"],
                                           openUser,
                                           configs)
        if result != 0:
            return False, bootstrapFailMsg % test
        else:
            # -------- wait for default service account to be ready and finish
            if waitForSA(kubeconfig) == 0:
                writeToFile(toLog, "...%s CLUSTER CREATED (masterIP: %s) => "
                            "STARTING TESTS\n" % (test, masterIP), True)
                return True, ""
            else:
                return False, "ERROR: timed out waiting for %s cluster's " \
                    "service account\n" % test
    else:  # Both terraform and ansible
        return terraformProvisionment(test,
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
                                      provDict,
                                      extraSupportedClouds)


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
        provDict,
        extraSupportedClouds):
    """Provisions VMs on the provider side and creates a k8s cluster with them.

    Parameters:
        test (str): Indicates the test for which to provision the cluster
        nodes (int): Number of nodes the cluster must contain.
        flavor (str): Flavor to be used for the VMs.
        extraInstanceConfig (str): Extra HCL code to configure VM
        toLog (str): File to which write the log msg.
        configs (dict): Object containing configs.yaml's configurations.
        testsRoot (str): Tests directory root.
        retry (bool): If true, retrying after a failure.
        instanceDefinition (str): HCL code definition of an instance.
        credentials (str): HCL code related to authentication/credentials.
        dependencies (str): HCL code related to infrastructure dependencies.
        baseCWD (str): Path to the base directory.
        provDict (dict): Dictionary containing the supported clouds.
        extraSupportedClouds (dict): Extra supported clouds.

    Returns:
        bool: True if the cluster was succesfully provisioned. False otherwise.
        str: Message informing of the provisionment task result.
    """

    templatesPath = "src/provisionment/tfTemplates/"
    if configs["providerName"] in extraSupportedClouds:
        templatesPath += configs["providerName"]
    else:
        templatesPath += "general"

    mainTfDir = testsRoot + test
    terraform_cli_vars = {}
    cfgPath = "%s/%s" % (baseCWD, cfgPath)
    kubeconfig = "%s/src/tests/%s/config" % (baseCWD, test)

    if test == "shared":
        flavor = configs["flavor"]
        mainTfDir = testsRoot + "shared"
        os.makedirs(mainTfDir, exist_ok=True)
        kubeconfig = "~/.kube/config"

    if retry is None:
        randomId = getRandomID() # One randomId per cluster

        nodeName = ("kubenode-%s-%s-%s" % (
                            configs["providerName"],
                            test,
                            randomId)
                    ).lower()

        # ---------------- delete TF stuff from previous run if existing
        cleanupTF(mainTfDir)

        # ---------------- manage general variables

        openUser = tryTakeFromYaml(configs,
                                   "openUser",
                                   "root",
                                   msgExcept=msgRoot % configs["providerName"])

        variables = loadFile("src/provisionment/tfTemplates/general/variables.tf",
                             required=True).replace(
            "NODES_PH", str(nodes)).replace(
            "PATH_TO_KEY_VALUE", str(configs["pathToKey"])).replace(
            "NAME_PH", nodeName)

        #terraform_cli_vars["dockerCE"] = tryTakeFromYaml(configs, "dockerCE", "")
        #terraform_cli_vars["dockerEngine"] = tryTakeFromYaml(configs, "dockerEngine", "")
        #terraform_cli_vars["kubernetes"] = tryTakeFromYaml(configs, "kubernetes", "")
        terraform_cli_vars["dockerCE"] = tryTakeFromYaml(configs, "dockerCE", None)
        terraform_cli_vars["dockerEngine"] = tryTakeFromYaml(configs, "dockerEngine", None)
        terraform_cli_vars["kubernetes"] = tryTakeFromYaml(configs, "kubernetes", None)

        if configs["providerName"] in extraSupportedClouds:

            writeToFile(mainTfDir + "/main.tf", variables, False) # TODO: do this with terraform_cli_vars too (yamldecode)
            rawProvisioning = loadFile("%s/rawProvision.tf" % templatesPath, required=True)

            terraform_cli_vars["configsFile"] = cfgPath
            terraform_cli_vars["flavor"] = flavor
            terraform_cli_vars["customCount"] = nodes
            terraform_cli_vars["instanceName"] = nodeName

            if configs["providerName"] == "azurerm":

                terraform_cli_vars["clusterRandomID"] = randomId # var.clusterRandomID to have unique interfaces and disks names
                terraform_cli_vars["publisher"] = tryTakeFromYaml(configs, "image.publisher", "OpenLogic")
                terraform_cli_vars["offer"] = tryTakeFromYaml(configs, "image.offer", "CentOS")
                terraform_cli_vars["sku"] = str(tryTakeFromYaml(configs, "image.sku", 7.5))
                terraform_cli_vars["imageVersion"] = str(tryTakeFromYaml(configs, "image.version", "latest"))

            if configs["providerName"] == "openstack":

                networkName = tryTakeFromYaml(configs, "networkName", False)
                if networkName is not False:
                    terraform_cli_vars["useDefaultNetwork"] = False
                terraform_cli_vars["region"] = tryTakeFromYaml(configs, "region", None)
                terraform_cli_vars["availabilityZone"] = tryTakeFromYaml(configs, "availabilityZone", None)

            if configs["providerName"] == "google":

                terraform_cli_vars["gpuCount"] = nodes if test == "dlTest" else "0"
                terraform_cli_vars["gpuType"] = tryTakeFromYaml(configs, "gpuType", None)
                #terraform_cli_vars["storageCapacity"] = tryTakeFromYaml(configs, "storageCapacity", 0) # TODO: this is fixed to 100

            if configs["providerName"] in ("aws", "cloudstack", "google", "openstack", "opentelekomcloud", "exoscale"):

                terraform_cli_vars["securityGroups"] = tryTakeFromYaml(configs, "securityGroups", None)

            if configs["providerName"] in ("cloudstack", "oci", "aws"):

                terraform_cli_vars["storageCapacity"] = tryTakeFromYaml(configs, "storageCapacity", None)

        else:
            # ---------------- main.tf: add vars
            writeToFile(mainTfDir + "/main.tf", variables, False)

            # ---------------- main.tf: add raw VMs provisioner
            instanceDefinition = "%s \n %s" % (flavor,
                instanceDefinition.replace(
                    "NAME_PH", "${var.instanceName}-${count.index}"))

            if extraInstanceConfig:
                instanceDefinition += "\n" + extraInstanceConfig

            rawProvisioning = loadFile("%s/rawProvision.tf" %
                                       templatesPath).replace(
                "CREDENTIALS_PLACEHOLDER", credentials).replace(
                "DEPENDENCIES_PLACEHOLDER", dependencies.replace(
                    "DEP_COUNT_PH", "count = %s" % nodes)).replace(
                "PROVIDER_NAME", str(configs["providerName"])).replace(
                "PROVIDER_INSTANCE_NAME", str(
                    configs["providerInstanceName"])).replace(
                "NODE_DEFINITION_PLACEHOLDER", instanceDefinition)

        writeToFile(mainTfDir + "/main.tf", rawProvisioning, True)

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

    # ---------------- RUN ANSIBLE (first create hosts file)
    result, masterIP = ansiblePlaybook(mainTfDir,
                                       baseCWD,
                                       configs["providerName"],
                                       kubeconfig,
                                       None,
                                       test,
                                       configs["pathToKey"],
                                       openUser,
                                       configs)
    if result != 0:
        return False, bootstrapFailMsg % test

    # ---------------- wait for default service account to be ready and finish
    if waitForSA(kubeconfig) == 0:
        writeToFile(toLog, "...%s CLUSTER CREATED (masterIP: %s) => "
                    "STARTING TESTS\n" % (test, masterIP), True)
        return True, ""
    else:
        return False, "ERROR: timed out waiting for %s cluster's " \
            "service account\n" % test

    return True, ""


def subprocPrint(test):
    """This runs on a child process. Reads the ansible log file, adds clusterID
       to each line and prints it.

    Parameters:
        test (str): Cluster identification.
    """

    line = None
    with open(ansibleLogs % test, 'r') as f:
        while True:
            line = f.readline()
            if len(line) > 0 and line != '\n':
                print("[ %s ] %s" % (test, line.replace('\n', '')))


def ansiblePlaybook(mainTfDir,
                    baseCWD,
                    providerName,
                    kubeconfig,
                    noTerraform,
                    test,
                    sshKeyPath,
                    openUser,
                    configs):
    """Runs ansible-playbook with the given playbook.

    Parameters:
        mainTfDir (str): Path where the .tf file is.
        baseCWD (str): Path to go back.
        providerName (str): Provider name.
        kubeconfig (str): Path to kubeconfig file.
        noTerraform (bool): Specifies whether current run uses terraform.
        test (str): Cluster identification.
        sshKeyPath (str): Path to SSH key file.
        openUser (str): User for initial SSH connection.
        configs (dict): Content of configs.yaml.

    Returns:
        int: 0 for success, 1 for failure
    """

    btspMsg = "...bootstraping Kubernetes cluster..."
    writeToFile("src/logging/%s" % test, btspMsg, True)

    hostsFilePath = "%s/hosts" % mainTfDir

    createHostsFile(mainTfDir,
                    baseCWD,
                    providerName,
                    hostsFilePath,
                    configs,
                    noTerraform=noTerraform,
                    test=test)

    loader = DataLoader()

    context.CLIARGS = ImmutableDict(
        tags={},
        private_key_file=sshKeyPath,
        connection='ssh',
        remote_user=openUser,
        become_method='sudo',
        ssh_common_args='-o StrictHostKeyChecking=no',
        extra_vars=[{'kubeconfig': kubeconfig}],
        forks=100,
        verbosity=False,  # True,
        listtags=False,
        listtasks=False,
        listhosts=False,
        syntax=False,
        check=False,
        start_at_task=None
    )

    inventory = InventoryManager(loader=loader, sources=hostsFilePath)
    variable_manager = VariableManager(loader=loader,
                                       inventory=inventory,
                                       version_info=CLI.version_info(
                                           gitinfo=False))

    # ----- to hide ansible logs
    if aggregateLogs:
        p = Process(target=subprocPrint, args=(test,))
        p.start()

    with open(ansibleLogs % test, 'a') as f:
        with contextlib.redirect_stdout(f):
            with contextlib.redirect_stderr(f):
                res = PlaybookExecutor(playbooks=[playbookPath],
                                       inventory=inventory,
                                       variable_manager=variable_manager,
                                       loader=loader,
                                       passwords=None).run(), getMasterIP(
                    hostsFilePath)

    if aggregateLogs:
        p.terminate()
    return res


def getIP(resource, provider):
    """Given a terraform resource json description, returns the resource's
       IP address if such exists

    Parameters:
        resource (object): Terraform resource definition.
        provider (str): Provider name.

    Returns:
        str: Resource's IP address.
    """

    try:
        if provider == "exoscale" or provider == "cloudstack":
            return resource["values"]["ip_address"]
        elif provider == "aws":
            return resource["values"]["private_ip"]
        elif provider == "azurerm":
            return resource["values"]["private_ip_address"]
        elif provider == "openstack":
            return resource["values"]["network"][0]["fixed_ip_v4"]
        elif provider == "google":
            return resource["values"]["network_interface"][0]["network_ip"]
        elif provider == "opentelekomcloud":
            return resource["values"]["access_ip_v4"]
        elif provider == "oci":
            return resource["values"]["private_ip"]
    except KeyError:
        return None


def createHostsFile(mainTfDir,
                    baseCWD,
                    provider,
                    destination,
                    configs,
                    noTerraform=None,
                    test=None):
    """Creates the hosts file required by ansible. Note destination contains
       the string 'hosts' too.

    Parameters:
        mainTfDir (str): Path where the .tf file is.
        baseCWD (str): Path to go back.
        provider (str): Provider name.
        destination (str): Destination of hosts file.
        configs (dict): Content of configs.yaml.
        noTerraform (bool): Specifies whether current run uses terraform.
        test (str): Cluster identification.

    Returns:
        int: 0 for success, 1 for failure
    """

    IPs = []

    if noTerraform is not True:
        os.chdir(mainTfDir)

        tfShowJson = json.loads(runCMD("terraform show -json", read=True))
        resources = tfShowJson["values"]["root_module"]["resources"]

        os.chdir(baseCWD)

        for resource in resources:
            ip = getIP(resource, provider)
            if ip is not None:
                IPs.append(ip)
    else:
        IPs = configs["clusters"][test]  # one of shared, dlTest, hpcTest

    config = ConfigParser(allow_no_value=True)
    config.add_section('master')
    config.add_section('slaves')
    config.set('master', IPs[0])
    for ip in IPs[1:]:
        config.set('slaves', ip)
    with open(destination, 'w') as hostsfile:
        config.write(hostsfile)
