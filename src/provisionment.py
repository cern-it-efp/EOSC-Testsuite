#!/usr/bin/env python3

# uses ansible

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

from aux import *

provisionFailMsg = "Failed to provision raw VMs. Check 'logs' file for details"
rootAllowerFailMsg = "Failed to allow root ssh on VMs. Check 'logs' file"
bootstrapFailMsg = "Failed to bootstrap '%s' k8s cluster. Check 'logs' file"


def runTerraform(mainTfDir, baseCWD, test, msg, autoApprove=True):
    """Run Terraform cmds.

    Parameters:
        mainTfDir (str): Path where the .tf file is.
        baseCWD (str): Path to go back.
        test (str): Cluster identification.
        msg (str): Message to be shown.
        autoApprove (bool): If True (default) use '-auto-approve' option

    Returns:
        int: 0 for success, 1 for failure
    """

    toLog = "logging/%s" % test
    writeToFile(toLog, msg, True)
    os.chdir(mainTfDir)
    beautify = "terraform fmt > /dev/null &&"
    tfCMD = "terraform init && %s terraform apply -auto-approve" % beautify
    if autoApprove is False:
        tfCMD = "terraform init && %s terraform apply" % beautify

    tfScript = """
    ((%s) && touch /tmp/validTFrun) |

    while read line; do echo [ %s ] $line; done

    if [ -f /tmp/validTFrun ]; then
    	rm -f /tmp/validTFrun
    	exit 0
    fi
    exit 1
    """ % (tfCMD, test)

    exitCode = runCMD(tfScript)
    os.chdir(baseCWD)
    return exitCode


def cleanupTF(mainTfDir):
    """Delete existing terraform stuff in the specified folder.

    Parameters:
        mainTfDir (str): Path to the .tf file.
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
    """Adds stack versioning related stuff to the variables section of the
       .tf file.

    Parameters:
        variables (str): Variables section of the .tf file.
        configs (dict): Object containing configs.yaml's configurations.

    Returns:
        string: modified variables section, stack versioning stuff added.
    """

    variables = variables.replace(
        "DOCKER_CE_PH", tryTakeFromYaml(configs, "dockerCE", ""))
    variables = variables.replace(
        "DOCKER_EN_PH", tryTakeFromYaml(configs, "dockerEngine", ""))
    variables = variables.replace(
        "K8S_PH", tryTakeFromYaml(configs, "kubernetes", ""))

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
        configs (dict): Object containing configs.yaml's configurations.
        testsRoot (str):
        retry ():
        instanceDefinition ():
        credentials ():
        dependencies ():
        baseCWD ():
        provDict ():
        extraSupportedClouds ():

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
    kubeconfig = "%s/tests/%s/config" % (baseCWD, test) # "config"
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
        nodeName = ("kubenode-%s-%s-%s" %
                    (configs["providerName"], test, str(randomId))).lower()

        # ---------------- delete TF stuff from previous run if existing
        # TODO: here, if there are tf files, first should try to: talk to it, check number of nodes available, etc
        #       and in case of success use the existing cluster.
        cleanupTF(mainTfDir)

        # ---------------- manage general variables

        openUserDefault = "root"
        msgExcept = "WARNING: using default user '%s' for ssh connections (running on %s)" % (
            openUserDefault, configs["providerName"])
        openUser = tryTakeFromYaml(
            configs, "openUser", openUserDefault, msgExcept=msgExcept)

        variables = loadFile("templates/general/variables.tf",
                             required=True).replace(
            "NODES_PH", str(nodes)).replace(
            "PATH_TO_KEY_VALUE", str(configs["pathToKey"])).replace(
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
                "SUBSCRIPTION_PH", configs['subscriptionId']).replace(
                "LOCATION_PH", configs['location']).replace(
                "PUB_SSH_PH", configs['pubSSH']).replace(
                "RGROUP_PH", configs['resourceGroupName']).replace(
                "RANDOMID_PH", randomId).replace(
                "VM_SIZE_PH", flavor).replace(
                "SECGROUPID_PH", configs['securityGroupID']).replace(
                "SUBNETID_PH", configs['subnetId']).replace(
                "PUBLISHER_PH", publisher).replace(
                "OFFER_PH", offer).replace(
                "SKU_PH", str(sku)).replace(
                "VERSION_PH", str(version))
            writeToFile(mainTfDir + "/main.tf", variables, False)

            # ---------------- main.tf: add raw VMs provisioner
            rawProvisioning = loadFile(
                "%s/rawProvision.tf" % templatesPath, required=True)

        elif configs["providerName"] == "openstack":

            # manage optional related vars
            region = tryTakeFromYaml(configs, "region", "")
            availabilityZone = tryTakeFromYaml(configs, "availabilityZone", "")
            securityGroups = tryTakeFromYaml(configs, "securityGroups", "[]")

            # ---------------- main.tf: manage openstack specific vars and add them
            variables = variables.replace(
                "FLAVOR_PH", flavor).replace(
                "IMAGE_PH", configs['imageName']).replace(
                "KEY_PAIR_PH", configs['keyPair']).replace(
                "\"SEC_GROUPS_PH\"", securityGroups).replace(
                "REGION_PH", region).replace(
                "AV_ZONE_PH", availabilityZone)
            writeToFile(mainTfDir + "/main.tf", variables, False)

            # ---------------- main.tf: add raw VMs provisioner
            rawProvisioning = loadFile(
                "%s/rawProvision.tf" % templatesPath, required=True)

        elif configs["providerName"] == "google":

            # manage gpu related vars
            gpuCount = str(nodes) if test == "dlTest" else "0"
            gpuType = tryTakeFromYaml(configs, "gpuType", "")

            # ---------------- main.tf: manage google specific vars and add them
            variables = variables.replace(
                "CREDENTIALS_PATH_PH", configs['pathToCredentials']).replace(
                "PROJECT_PH", configs['project']).replace(
                "MACHINE_TYPE_PH", flavor).replace(
                "ZONE_PH", configs['zone']).replace(
                "IMAGE_PH", configs['image']).replace(
                "GPU_COUNT_PH", gpuCount).replace(
                "GPU_TYPE_PH", gpuType)
            writeToFile(mainTfDir + "/main.tf", variables, False)

            # ---------------- main.tf: add raw VMs provisioner
            rawProvisioning = loadFile(
                "%s/rawProvision.tf" % templatesPath, required=True)

        elif configs["providerName"] == "aws":

            # manage optional vars

            awsTemplate = "%s/rawProvision.tf" % templatesPath
            volumeSize = tryTakeFromYaml(configs, "volumeSize", "")
            if volumeSize is "":
                awsTemplate = "%s/rawProvision_noVolumeSize.tf" % templatesPath

            # ---------------- main.tf: manage aws specific vars and add them
            variables = variables.replace(
                "REGION_PH", configs['region']).replace(
                "SHARED_CREDENTIALS_FILE_PH", configs['sharedCredentialsFile']).replace(
                "INSTANCE_TYPE_PH", flavor).replace(
                "AMI_PH", configs['ami']).replace(
                "NAME_KEY_PH", configs['keyName']).replace(
                "VOLUME_SIZE_PH", str(volumeSize))
            writeToFile(mainTfDir + "/main.tf", variables, False)

            # ---------------- main.tf: add raw VMs provisioner
            rawProvisioning = loadFile(awsTemplate, required=True)

        elif configs["providerName"] == "cloudstack":

            # manage optional vars
            securityGroups = tryTakeFromYaml(configs, "securityGroups", "[]")
            diskSize = tryTakeFromYaml(configs, "diskSize", "")
            if diskSize is "":
                csTemplate = "%s/rawProvision_noDiskSize.tf" % templatesPath
            else:
                csTemplate = "%s/rawProvision.tf" % templatesPath

            # ---------------- main.tf: manage aws specific vars and add them
            variables = variables.replace(
                "CONFIG_PATH_PH", configs['configPath']).replace(
                "ZONE_PH", configs['zone']).replace(
                "EXO_SIZE_PH", flavor).replace(
                "TEMPLATE_PH", configs['template']).replace(
                "KEY_PAIR_PH", configs['keyPair']).replace(
                "\"SEC_GROUPS_PH\"", securityGroups).replace(
                "DISK_SIZE_PH", str(diskSize))
            writeToFile(mainTfDir + "/main.tf", variables, False)

            # ---------------- main.tf: add raw VMs provisioner
            rawProvisioning = loadFile(csTemplate, required=True)

        elif configs["providerName"] == "exoscale":

            # manage optional vars
            securityGroups = tryTakeFromYaml(configs, "securityGroups", "[]")

            # ---------------- main.tf: manage aws specific vars and add them
            variables = variables.replace(
                "CONFIG_PATH_PH", configs['configPath']).replace(
                "ZONE_PH", configs['zone']).replace(
                "EXO_SIZE_PH", flavor).replace(
                "TEMPLATE_PH", configs['template']).replace(
                "KEY_PAIR_PH", configs['keyPair']).replace(
                "\"SEC_GROUPS_PH\"", securityGroups).replace(
                "DISK_SIZE_PH", str(configs['diskSize']))
            writeToFile(mainTfDir + "/main.tf", variables, False)

            # ---------------- main.tf: add raw VMs provisioner
            rawProvisioning = loadFile(
                "%s/rawProvision.tf" % templatesPath, required=True)

        else:
            # ---------------- main.tf: add vars
            writeToFile(mainTfDir + "/main.tf", variables, False)

            # ---------------- main.tf: add raw VMs provisioner
            instanceDefinition = "%s \n %s" % (flavor, instanceDefinition.replace(
                "NAME_PH", "${var.instanceName}-${count.index}"
            ))

            if extraInstanceConfig:
                instanceDefinition += "\n" + extraInstanceConfig

            rawProvisioning = loadFile("%s/rawProvision.tf" % templatesPath).replace(
                "CREDENTIALS_PLACEHOLDER", credentials).replace(
                "DEPENDENCIES_PLACEHOLDER", dependencies.replace(
                    "DEP_COUNT_PH", "count = %s" % nodes)).replace(
                "PROVIDER_NAME", str(configs["providerName"])).replace(
                "PROVIDER_INSTANCE_NAME", str(
                    configs["providerInstanceName"])).replace(
                "NODE_DEFINITION_PLACEHOLDER", instanceDefinition)

        writeToFile(mainTfDir + "/main.tf", rawProvisioning, True)

        # ---------------- RUN TERRAFORM - phase 1: provision VMs
        if runTerraform(mainTfDir,
                        baseCWD,
                        test,
                        "Provisioning '%s' VMs..." % flavor) != 0:
            return False, provisionFailMsg

# ----------------- TODO: at this point, add only the root allower and run ansible

        # ---------------- RUN TERRAFORM - phase 2: allow root ssh on machines # TODO: can these 2 be done at once? wouldn't that fail in Azure though?
        if openUser is not "root":
            rootAllower = loadFile("templates/general/rootAllower.tf", required=True).replace(
                "LIST_IP_GETTER", provDict[configs["providerName"]]).replace(
                "ALLOW_ROOT_COUNT", "var.customCount")
            writeToFile(mainTfDir + "/main.tf", rootAllower, True)
            if runTerraform(mainTfDir,
                            baseCWD,
                            test,
                            "...running root allower on machines...") != 0:
                return False, rootAllowerFailMsg % flavor

    # ---------------- RUN ANSIBLE (first create hosts file)
    writeToFile("logging/%s" % test, "...bootstraping Kubernetes cluster...", True)
    playbookPath = "provisionment/playbooks/bootstraper.yaml"
    hostsFilePath = "%s/hosts" % mainTfDir # "tests/sharedCluster/hosts"
    os.chdir(mainTfDir)
    tfShow = os.popen("terraform show -json").read().strip()
    os.chdir(baseCWD)
    resources = json.loads(tfShow)["values"]["root_module"]["resources"]
    createHostsFile(resources, configs["providerName"], hostsFilePath)
    result = runPlaybook(playbookPath, hostsFilePath, kubeconfig, sshKeyPath=configs["pathToKey"])
    if result != 0:
        return False, bootstrapFailMsg % flavor


# --------------------------------------------------------------------------------

    # ---------------- wait for default service account to be ready and finish
    # TODO: this has to have a timeout
    while runCMD(
        'kubectl --kubeconfig %s get sa default' %
        kubeconfig,
            hideLogs=True) != 0:
        time.sleep(1)

    writeToFile(toLog, "...'%s' CLUSTER CREATED (masterIP: %s) => STARTING TESTS\n" % (flavor,getMasterIP(hostsFilePath)), True)

    return True, ""


def runPlaybook(playbookPath, hostsFilePath, kubeconfig, sshKeyPath):
    """Runs ansible-playbook with the given playbook."""

    loader = DataLoader()

    context.CLIARGS = ImmutableDict(
        tags={},
        private_key_file=sshKeyPath,
        connection='ssh',
        remote_user='root',
        become_method='sudo',
        become_user='root',
        ssh_common_args='-o StrictHostKeyChecking=no',
        extra_vars=[{'kubeconfig': kubeconfig}],
        forks=100,
        become=True,
        verbosity=True,
        listtags=False,
        listtasks=False,
        listhosts=False,
        syntax=False,
        check=False,
        start_at_task=None,
        # module_path=None,
        # ssh_extra_args=None,
        # sftp_extra_args=None,
        # scp_extra_args=None,
    )

    inventory = InventoryManager(loader=loader, sources=hostsFilePath)
    variable_manager = VariableManager(loader=loader,
                                       inventory=inventory,
                                       version_info=CLI.version_info(gitinfo=False))

    return PlaybookExecutor(playbooks=[playbookPath],
                            inventory=inventory,
                            variable_manager=variable_manager,
                            loader=loader,
                            passwords=None).run()


def getIP(resource, provider):
    """Given a terraform resource json description, returns the resource's
       IP address if such exists"""
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
    except KeyError:
        return None


def createHostsFile(resources, provider, destination):
    """Creates the hosts file required by ansible. Note destination contains
       the string 'hosts' too."""

    IPs = []
    for resource in resources:
        ip = getIP(resource, provider)
        if ip is not None:
            IPs.append(ip)

    config = ConfigParser(allow_no_value=True)
    config.add_section('master')
    config.add_section('slaves')
    config.set('master',IPs[0])
    for ip in IPs[1:]:
        config.set('slaves',ip)
    with open(destination, 'w') as hostsfile:
        config.write(hostsfile)


def destroyTF(baseCWD, clusters=None):
    """Destroy infrastructure. 'clusters' is an array whose objects specify
       the clusters that should be destroyed. In case no array is given, all
       clusters will be destroyed"""

    if clusters is None:
        clusters = ["sharedCluster", "dlTest", "hpcTest"]

    res = []

    for cluster in clusters:
        logger("Destroying %s cluster..." % cluster, "~", "logging/footer")

        os.chdir("tests/%s" % cluster)
        exitCode = runCMD("terraform destroy -auto-approve")
        res.append(exitCode)
        os.chdir(baseCWD)

    return res # TODO: return a dict with the destroy status of each cluster
