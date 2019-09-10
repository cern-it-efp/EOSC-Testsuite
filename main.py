#!/usr/bin/env python3

import sys
try:
    import yaml
    import json
    from kubernetes import client, config, utils
    from kubernetes.stream import stream
    from tempfile import NamedTemporaryFile
    from kubernetes.client.rest import ApiException
    from multiprocessing import Process, Queue
    import jsonschema
    import getopt
    import os
    import datetime
    import time
    import subprocess
    import random
    import string
    import re
    import shutil
    import tarfile
    from pathlib import Path
    from enum import Enum

except ModuleNotFoundError as ex:
    print(ex)
    sys.exit(1)


def stop(code):
    """ Stops the TS run exiting using the provided status code

    Parameters:
        code (int): Exit code to be used
    """

    time.sleep(2)
    sys.exit(code)


def runCMD(cmd, hideLogs=None, read=None):
    """ Run the command.

    Parameters:
        cmd (str): Command to be run
        hideLogs (bool): Indicates whether cmd logs should be hidden
        read (bool): Indicates whether logs of the command should be returned

    Returns:
        int or str: Exit code returned by the command run. Logs of the command in case of read=True
    """

    if read is True:
        return os.popen(cmd).read().strip()
    if hideLogs is True:
        return subprocess.call(cmd, shell=True, stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)
    else:
        return os.system(cmd)


def logger(text, sym, file):
    """ Logs in a fancy way.

    Parameters:
        text (str): Text to log
        sym (bool): Symbol to use to create boxes and separation lines
        file (bool): File the logs should be sent to
    """

    size = 61  # longest msg on code
    frame = sym * (size + 6)
    blank = sym + "  " + " " * size + "  " + sym
    toPrint = frame + "\n" + blank
    if isinstance(text, list):
        for i in text:
            textLine = i.strip()
            toPrint += "\n" + sym + "  " + textLine + \
                " " * (size - len(textLine)) + "  " + sym
    else:
        text = text.strip()
        toPrint += "\n" + sym + "  " + text + \
            " " * (size - len(text)) + "  " + sym
    toPrint += "\n" + blank + "\n" + frame
    if file:
        runCMD("echo \"%s\" >> %s" %
               (toPrint, file))
    else:
        print(toPrint)


logger("OCRE Cloud Benchmarking Validation Test Suite (CERN)", "#", "logging/header")

onlyTest = False
killResources = False
configs = ""
testsCatalog = ""
instanceDefinition = ""
extraInstanceConfig = ""
dependencies = ""
credentials = ""
t = True
totalCost = 0
procs = []
testsRoot = "tests/"
viaBackend = False
testsSharingCluster = ["s3Test", "dataRepatriationTest",
                       "perfsonarTest", "cpuBenchmarking", "dodasTest"]
customClustersTests = ["dlTest", "hpcTest"]
baseCWD = os.getcwd()
resultsExist = False
provDict = {
    'openstack': 'openstack_compute_instance_v2.kubenode[count.index].network[0].fixed_ip_v4',
    'exoscale': 'element(exoscale_compute.kubenode.*.ip_address, count.index)',
    'aws': 'element(aws_instance.kubenode.*.private_ip, count.index)',
    'azurerm': 'element(azurerm_network_interface.terraformnic.*.private_ip_address, count.index)',
    'google': 'element(google_compute_instance.kubenode.*.network_interface.0.network_ip, count.index)',
    'opentelekomcloud': '',
    'cloudstack': '',
    'cloudscale': '',
    'ibm': ''
}
extraSupported = {
    'azurerm': 'azureProvision',
    'google': 'googleProvision',
    'aws': 'awsProvision',
    'exoscale': 'awsExoscale',
    'openstack': 'openstackProvision'
}
obtainCost = True
retry = None
publicRepo = "https://github.com/cern-it-efp/OCRE-Testsuite"
Action = Enum('Action', 'create delete cp exec')
Type = Enum('Type', 'pod daemonset mpijob configmap pv')


def loadFile(loadThis, required=None):
    """ Loads a file

    Parameters:
        loadThis (str): Path to the file to load
        required (bool): Indicates whether the file is required

    Returns:
        str or yaml: The loaded file or empty string if the file was not found and required is not True. Exits with code 1 otherwise.
    """

    if os.path.exists(loadThis) is False:
        if required is True:
            print(loadThis + " file not found")
            stop(1)
        else:
            return ""
    with open(loadThis, 'r') as inputfile:
        if ".yaml" in loadThis:
            try:
                return yaml.load(inputfile, Loader=yaml.FullLoader)
            except AttributeError:
                try:
                    return yaml.load(inputfile)
                except yaml.scanner.ScannerError:
                    print("Error loading yaml file " + loadThis)
                    stop(1)
            except yaml.scanner.ScannerError:
                print("Error loading yaml file " + loadThis)
                stop(1)
        else:
            return inputfile.read().strip()


def writeToFile(filePath, content, append):
    """ Writes stuff to a file.

    Parameters:
        filePath (str): Path to the file to load
        content (str): Content to write to the file
        append (bool): If true, the content has to be appended. False overrides the file or creates if not existing
    """

    mode = 'w'
    if append is True:
        mode = 'a'
    with open(filePath, mode) as outfile:
        outfile.write(content + '\n')


def initAndChecks():
    """Initial checks and initialization of variables.

    Returns:
        Array(str): Array containing the selected tests (strings)
    """

    # --------File check
    global configs
    global testsCatalog
    global instanceDefinition
    global extraInstanceConfig
    global dependencies
    global credentials
    global obtainCost

    if runCMD("terraform version", hideLogs=True) != 0:
        print("Terraform is not installed")
        stop(1)
    if runCMD("kubectl", hideLogs=True) != 0:
        print("kubectl is not installed")
        stop(1)

    configs = loadFile("configurations/configs.yaml", required=True)
    testsCatalog = loadFile("configurations/testsCatalog.yaml", required=True)

    if os.path.isfile(configs["pathToKey"]) is False:
        print("Key file not found at the specified path '%s'" % configs["pathToKey"])
        stop(1)
    if runCMD("ls -l %s | grep '\-rw\-\-\-\-\-\-\-'" % configs["pathToKey"], hideLogs=True) != 0:
        print("Key permissions must be set to 600")
        stop(1)

    # disable schema validation for testing
    #try:
    #    jsonschema.validate(configs, loadFile("schemas/configs_sch.yaml"))
    #except jsonschema.exceptions.ValidationError as ex:
    #    print("Error validating configs.yaml: \n %s" % ex)
    #    stop(1)

    #try:
    #    jsonschema.validate(testsCatalog, loadFile("schemas/testsCatalog_sch.yaml"))
    #except jsonschema.exceptions.ValidationError as ex:
    #    print("Error validating testsCatalog.yaml: \n %s" % ex)
    #    stop(1)

    instanceDefinition = loadFile("configurations/instanceDefinition") # this is now only required when not running on main clouds
    extraInstanceConfig = loadFile("configurations/extraInstanceConfig")
    dependencies = loadFile("configurations/dependencies")
    credentials = loadFile("configurations/credentials")

    # --------General config checks
    #if "\"#NAME" not in instanceDefinition: # this has to be checked now only when not running on main clouds
    #    writeToFile("logging/header", "The placeholder comment for name at configs.yaml was not found!", True)
    #    stop(1)
    #if configs['providerName'] not in provDict:
    #    writeToFile("logging/header", "Provider '%s' not supported" % configs['providerName'], True)
    #    stop(1)

    # --------Tests config checks
    selected = []
    if testsCatalog["s3Test"]["run"] is True:
        selected.append("s3Test")
        obtainCost = checkCost(configs["costCalculation"]["generalInstancePrice"])
        obtainCost = checkCost(configs["costCalculation"]["s3bucketPrice"])

    if testsCatalog["perfsonarTest"]["run"] is True:
        selected.append("perfsonarTest")
        obtainCost = checkCost(configs["costCalculation"]["generalInstancePrice"])

    if testsCatalog["dataRepatriationTest"]["run"] is True:
        selected.append("dataRepatriationTest")
        obtainCost = checkCost(configs["costCalculation"]["generalInstancePrice"])

    if testsCatalog["cpuBenchmarking"]["run"] is True:
        selected.append("cpuBenchmarking")
        obtainCost = checkCost(configs["costCalculation"]["generalInstancePrice"])

    if testsCatalog["dlTest"]["run"] is True:
        selected.append("dlTest")
        obtainCost = checkCost(configs["costCalculation"]["GPUInstancePrice"])

    if testsCatalog["hpcTest"]["run"] is True:
        selected.append("hpcTest")
        obtainCost = checkCost(configs["costCalculation"]["GPUInstancePrice"])

    if testsCatalog["dodasTest"]["run"] is True:
        selected.append("dodasTest")
        obtainCost = checkCost(configs["costCalculation"]["generalInstancePrice"])

    return selected


def checkCluster(test):
    """ Returns True if the cluster is reachable

    Parameters:
        test (str): Check this test's cluster

    Returns:
        bool: True in case the cluster is reachable. False otherwise
    """

    cmd = "kubectl get nodes --request-timeout=4s"
    if test != "shared":
        cmd += " --kubeconfig tests/%s/config" % (test)
    if runCMD(cmd, hideLogs=True) != 0:
        writeToFile("logging/" + test, test
                    + " cluster not reachable, was infrastructure created?", True)
        return False
    return True


def setName(instance, purpose, randomId):
    """Generates the name for a VM.

    Parameters:
        instance (str): Instance's raw name
        purpose (str): Cluster purpose, to differentiate the clusters
        randomId (str): A random id to name the node

    Returns:
        str: Name for the instance
    """

    newName = ("-%s${count.index}-%s-%s" %
               (configs["providerName"], purpose, str(randomId) + "\"")).lower()
    return instance.replace("\"#NAME", newName)


def fetchResults(source, file, toLog):
    """Fetch tests results file from pod.

    Parameters:
        source (str): Location of the results file.
        file (str): Name to be given to the file.
        toLog (str): Path to the log file to which logs have to be sent
    """

    while os.path.exists(resDir + "/" + file) is False:
        kubectl(Action.cp, podPath=source, localPath="%s/%s" % (resDir, file), fetch=True)
    writeToFile(toLog, file + " fetched!", True)


def checkDestinationIsDir(podName, pathOnPod, namespace=None):
    """Checks -in the case of copy to pod- whether the destination is a directory.

    Parameters:
        podName (str): Name of the pod to which the file has to be sent
        pathOnPod (str): Path within the pod to locate the file
        namespace (str): Kubernetes namespace on which the pod is deployed

    Returns:
        bool: True means dest is a directory on the pod, False otherwise.
    """

    if namespace is None:
        namespace = "default"
    cmd = "test -d %s ; echo $?" % pathOnPod
    resp = stream(client.CoreV1Api().connect_get_namespaced_pod_exec, podName, namespace, command=['/bin/bash', '-c', cmd], stderr=True, stdin=True, stdout=True, tty=False)
    if int(resp) == 1:
        return False
    return True


def kubectl(action, type=None, name=None, file=None, cmd=None, kubeconfig=None, namespace=None, podPath=None, localPath=None, fetch=None, toLog=None, ignoreErr=None):
    """Manage stuff on a Kubernetes cluster.

    Parameters:
        action (str): Action to be carried out. One of: create, delete or cp.
        type (str): Resource type in case of 'delete'.
        name (str): Resource name.
        file (str): YAML defining the resource to create in case of 'create'.
        cmd (str): Command to be run in case of 'exec'.
        kubeconfig (str): Path to the kubeconfig file of the being managed cluster.
        namespace (str): Namespace on which to carry the action.
        podPath (str): Pod path in case of 'cp'
        localPath (str): Local path in case of 'cp'
        fetch (bool): True indicates copy from pod to local, False from local to pod
        toLog (str): Path to the log file to which logs have to be sent
        ignoreErr (bool): If True, in case of error, catch exception and continue

    Returns:
        int: 0 for success, 1 for failure
    """

    res = True
    if kubeconfig:
        config.load_kube_config(config_file=kubeconfig)
    else:
        config.load_kube_config()

    if namespace is None:
        namespace = "default"

    if action is Action.create:
        try:
            utils.create_from_yaml(client.api_client.ApiClient(), file)
            if toLog:
                writeToFile(toLog, "Created resource from file '%s'" %
                            file, True)
        except AttributeError as ex:
            with open(file, 'r') as inputfile:
                body = yaml.load(inputfile, Loader=yaml.FullLoader)
            try:
                apiResponse = client.CustomObjectsApi().create_namespaced_custom_object(
                    'kubeflow.org', 'v1alpha1', namespace, 'mpijobs', body)
                writeToFile(toLog, "Created resource from file '%s'" %
                            file, True)
            except ApiException as ex:
                print(ex)
                if ignoreErr is not True:
                    res = False
        except ApiException as ex:
            print(ex)
            if ignoreErr is not True:
                res = False
        except:
            if ignoreErr is not True:
                res = False

    elif action is Action.delete:
        try:
            if type is Type.pod:
                apiResponse = client.CoreV1Api().delete_namespaced_pod(
                    name=name, namespace=namespace)
            elif type is Type.daemonset:
                apiResponse = client.AppsV1Api().delete_namespaced_daemon_set(
                    name=name, namespace=namespace)
            elif type is Type.mpijob:
                try:
                    apiResponse = client.CustomObjectsApi().delete_namespaced_custom_object(
                        'kubeflow.org', 'v1alpha1', namespace, 'mpijobs', name, client.V1DeleteOptions())
                except:  # except ApiException as ex:
                    res = False
            elif type is Type.configmap:
                apiResponse = client.CoreV1Api().delete_namespaced_config_map(
                    name=name, namespace=namespace)
            elif type is Type.pv:
                apiResponse = client.CoreV1Api().delete_persistent_volume(name=name)
        except:  # except ApiException as ex:
            res = False

    elif action is Action.exec:
        try:
            resp = stream(client.CoreV1Api().connect_get_namespaced_pod_exec, name, namespace, command=['/bin/bash', '-c', cmd], stderr=True, stdin=True, stdout=True, tty=False)
        except:  # except ApiException as ex:
            res = False

    elif action is Action.cp:

        podName = podPath.split(':')[0]
        # remove ending '/' if exists
        pathOnPod = re.sub("[/]$", "", podPath.split(':')[1])
        # remove ending '/' if exists
        localPath = re.sub("[/]$", "", localPath)

        try:
            with NamedTemporaryFile() as tarBuffer:
                if fetch:
                    # copy from pod: compress on pod
                    execCommand = ['tar', 'cf', '-', pathOnPod]
                else:
                    if checkDestinationIsDir(podName, pathOnPod) is False:
                        fileNameOnDest = pathOnPod.split('/')[-1]
                        pathOnPod = os.path.dirname(pathOnPod)
                    else:
                        fileNameOnDest = Path(localPath).name
                    # copy to pod: extract on pod
                    execCommand = ['tar', 'xf', '-', '-C', pathOnPod]

                    with tarfile.open(fileobj=tarBuffer, mode='w') as tar:
                        tar.add(localPath, arcname=fileNameOnDest)
                    tarBuffer.seek(0)
                    commands = [tarBuffer.read()]

                resp = stream(client.CoreV1Api().connect_get_namespaced_pod_exec, podName, namespace, command=execCommand, stderr=True, stdin=True, stdout=True, tty=False, _preload_content=False)

                while resp.is_open():
                    resp.update(timeout=1)
                    if resp.peek_stdout():
                        if fetch:
                            tarBuffer.write(resp.read_stdout().encode())
                        else:
                            print("STDOUT: %s" % resp.read_stdout())
                    if not fetch and commands:
                        resp.write_stdin(commands.pop(0).decode())
                resp.close()

                tarBuffer.flush()
                tarBuffer.seek(0)

                if fetch:
                    tar = tarfile.open(tarBuffer.name)
                    try:
                        member = tar.getmembers()[0]
                        member.name = os.path.basename(member.name)
                        if os.path.isdir(localPath) is False:  # check if localPath is a locally existing directory.
                            member.name = os.path.basename(localPath)
                            localPath = os.path.dirname(localPath)
                        tar.extract(member, localPath)
                        tar.close()
                    except IndexError:  # File not found
                        res = False
        except:  # except ApiException as ex:
            res = False

    return 0 if res is True else 1

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
    exitCode = runCMD('terraform init && %s terraform apply -auto-approve' % beautify)
    os.chdir(baseCWD)
    return exitCode


def terraformProvisionmentAzure(test, nodes, flavor, extraInstanceConfig, toLog):
    """Provisions VMs on azure and creates a k8s cluster with them."""

    kubeconfig = "config"
    mainTfDir = testsRoot + test
    if test == "shared":
        flavor = configs["flavor"]
        mainTfDir = testsRoot + "sharedCluster"
        os.makedirs(mainTfDir, exist_ok=True)
        kubeconfig = "~/.kube/config"

    # in order to have a single file for the infrastructure ("main.tf") put variables at the  beginning of it
    randomId = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(4))  # A randomId is needed for each cluster
    nodeName = ("kubenode-%s-%s-%s" %(configs["providerName"], test, str(randomId))).lower()
    variables = loadFile("templates/azure/variables.tf", required=True).replace(
        "OPEN_USER_PH", configs['openUser']).replace(
        "PATH_TO_KEY_VALUE", str(configs["pathToKey"])).replace(
        "KUBECONFIG_DST", kubeconfig).replace(
        "LOCATION_PH", configs['location']).replace(
        "PUB_SSH_PH", configs['pubSSH']).replace(
        "RGROUP_PH", configs['resourceGroupName']).replace(
        "AMOUNT_PH", str(nodes)).replace(
        "RANDOMID_PH", randomId).replace(
        "VM_SIZE_PH", configs['flavor']).replace(
        "SECGROUPID_PH", configs['secGroupId']).replace(
        "SUBNETID_PH", configs['subnetId']).replace(
        "INSTANCE_NAME_PH", nodeName)

    # ------------------------- stack versioning
    variables = variables.replace("DOCKER_CE_PH", str(configs["dockerCE"])) if configs["dockerCE"] else variables.replace("DOCKER_CE_PH", "")
    variables = variables.replace("DOCKER_EN_PH", str(configs["dockerEngine"])) if configs["dockerEngine"] else variables.replace("DOCKER_EN_PH", "")
    variables = variables.replace("K8S_PH", str(configs["kubernetes"])) if configs["kubernetes"] else variables.replace("K8S_PH", "")

    writeToFile(mainTfDir + "/main.tf", variables, False)

    # Add VM provisionment to main.tf
    rawProvisioning = loadFile("templates/azure/rawProvision.tf", required=True)
    writeToFile(mainTfDir + "/main.tf", rawProvisioning, True)

    # run terraform
    if runTerraform(mainTfDir, baseCWD) != 0:
        return False, "Failed to provision raw VMs. Check 'logs' file for details"

    # On completion of TF, add the bootstraping section to main.tf
    bootstrap = loadFile("templates/azure/bootstrap.tf", required=True)
    writeToFile(mainTfDir + "/main.tf", bootstrap, True)

    # Run terraform again
    writeToFile(toLog, "...bootstraping Kubernetes cluster...", True)
    if runTerraform(mainTfDir, baseCWD) != 0:
        return False, "Failed to bootstrap '%s' k8s cluster. Check 'logs' file " % flavor

    # ---------------- wait for default service account to be ready
    while runCMD('kubectl --kubeconfig %s get sa default' % kubeconfig, hideLogs=True) != 0:
        time.sleep(1)

    os.chdir(baseCWD)

    writeToFile(toLog, "...'%s' CLUSTER CREATED => STARTING TESTS\n" % flavor, True)
    return True, ""


def terraformProvisionment(test, nodes, flavor, extraInstanceConfig, toLog):
    """Provisions VMs on the provider side and creates a k8s cluster with them.

    Parameters:
        test (str): String indicating the test for which to provision the cluster
        nodes (int): Number of nodes the cluster must contain.
        flavor (str): Flavor to be used for the VMs.
        extraInstanceConfig (str): Extra HCL code to configure compute instance
        toLog (str): File to which write the log msg.

    Returns:
        bool: True in case the cluster was succesfully provisioned. False otherwise.
        str: Message informing of the provisionment task result.
    """

    # if configs["providerName"] in extraSupported:
    #    return eval(extraSupported[configs["providerName"](test, nodes, flavor, extraInstanceConfig, toLog))

    if configs["providerName"] == "azurerm":
        return terraformProvisionmentAzure(test, nodes, flavor, extraInstanceConfig, toLog)

    kubeconfig = "config"
    mainTfDir = testsRoot + test
    if test == "shared":
        flavor = configs["flavor"]
        mainTfDir = testsRoot + "sharedCluster"
        os.makedirs(mainTfDir, exist_ok=True)
        kubeconfig = "~/.kube/config"

    if retry is None:
        randomId = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(4))  # A randomId is needed for each cluster
        # ---------------- delete TF stuff from previous run if existing
        for filename in ["join.sh", "main.tf", "terraform.tfstate", "terraform.tfstate.backup", ".terraform"]:
            file = "%s/%s" % (mainTfDir, filename)
            if os.path.isfile(file):
                os.remove(file)
            if os.path.isdir(file):
                shutil.rmtree(file, True)

        # ---------------- create provisioner main.tf file
        global instanceDefinition
        instanceDefinition = setName("%s \n %s" % (flavor, instanceDefinition), test, randomId)
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
            bootstrap = bootstrap.replace("ALLOW_ROOT_PH", "").replace("ALLOW_ROOT_DEP_PH", "")

        bootstrap = bootstrap.replace(
            "PATH_TO_KEY_VALUE", str(configs["pathToKey"])).replace(
            "LIST_IP_GETTER", provDict[configs["providerName"]]).replace(
            "KUBECONFIG_DST", kubeconfig)

        # ------------------------- stack versioning
        bootstrap = bootstrap.replace("DOCKER_CE_PH", str(configs["docker-ce"])) if configs["dockerCE"] else bootstrap.replace("DOCKER_CE_PH", "")
        bootstrap = bootstrap.replace("DOCKER_EN_PH", str(configs["dockerEngine"])) if configs["dockerEngine"] else bootstrap.replace("DOCKER_EN_PH", "")
        bootstrap = bootstrap.replace("K8S_PH", str(configs["kubernetes"])) if configs["kubernetes"] else bootstrap.replace("K8S_PH", "")

        bootstrap = "\n" + bootstrap.replace(
            "PROVIDER_INSTANCE_NAME", str(configs["providerInstanceName"])).replace(
            "NODES_PH", str(nodes))
        writeToFile(mainTfDir + "/main.tf", bootstrap, True)

    # ---------------- locate where main.tf is and run terraform, use '-auto-approve'
    writeToFile(toLog, "...bootstraping Kubernetes cluster...", True)

    #if retry is True and os.path.isfile("main.tf") is False: # TODO: improve
    #    print("ERROR: run with option --retry before normal run.")
    #    stop(1)

    if runTerraform(mainTfDir, baseCWD) != 0:
        return False, "Failed to bootstrap '%s' k8s cluster. Check 'logs' file " % flavor

    # ---------------- wait for default service account to be ready
    while runCMD('kubectl --kubeconfig %s get sa default' % kubeconfig, hideLogs=True) != 0:
        time.sleep(1)

    os.chdir(baseCWD)

    writeToFile(toLog, "...'%s' CLUSTER CREATED => STARTING TESTS\n" % flavor, True)
    return True, ""


def checkDLsupport():
    """Check whether infrastructure supports DL.

    Returns:
        bool: True in case cluster supports DL (dl_stack.sh was already run), False otherwise.
    """

    pods = runCMD('kubectl --kubeconfig tests/dlTest/config get pods -n kubeflow', read=True)
    return len(pods) > 0 and "No resources found." not in pods


def writeFail(file, msg, toLog):
    """Writes results file in case of errors.

    Parameters:
        file (str): Name of the results file.
        msg (str): Message to write to results file.
        toLog (str): File to which write the log msg.
    """

    writeToFile(toLog, msg, True)
    with open(resDir + "/" + file, 'w') as outfile:
        json.dump({"info": msg, "result": "fail"}, outfile, indent=4, sort_keys=True)


def checkCost(value):
    """ Returns True if the provided value is not None and is greater than 0. False otherwise.

    Parameters:
        value: Value to be checked.
    """

    return value >= 0 and obtainCost is True if value else False


def s3Test():
    """Run S3 endpoints test."""

    res = False
    testCost = 0
    with open(testsRoot + "s3/raw/s3pod_raw.yaml", 'r') as infile:
        with open(testsRoot + "s3/s3pod.yaml", 'w') as outfile:
            outfile.write(infile.read().replace("ENDPOINT_PH", testsCatalog["s3Test"]["endpoint"])
                          .replace("ACCESS_PH", testsCatalog["s3Test"]["accessKey"])
                          .replace("SECRET_PH", testsCatalog["s3Test"]["secretKey"]))

    start = time.time()  # create bucket
    if kubectl(Action.create, file=testsRoot + "s3/s3pod.yaml", toLog="logging/shared") != 0:
        writeFail("s3Test.json", "Error deploying s3pod.", "logging/shared")
    else:
        fetchResults("s3pod:/home/s3_test.json", "s3_test.json", "logging/shared")
        end = time.time()  # bucket deletion
        # cleanup
        writeToFile("logging/shared", "Cluster cleanup...", True)
        kubectl(Action.delete, type=Type.pod, name="s3pod")
        res = True
        if obtainCost is True:
            testCost = float(configs["costCalculation"]["s3bucketPrice"]) * (end - start) / 3600

    queue.put(({"test": "s3Test", "deployed": res}, testCost))


def dataRepatriationTest():
    """Run Data Repatriation Test -Exporting from cloud to Zenodo-."""

    res = False
    testCost = 0
    with open(testsRoot + "data_repatriation/raw/repatriation_pod_raw.yaml", 'r') as infile:
        with open(testsRoot + "data_repatriation/repatriation_pod.yaml", 'w') as outfile:
            outfile.write(infile.read().replace("PROVIDER_PH", configs["providerName"]))

    if kubectl(Action.create, file="%sdata_repatriation/repatriation_pod.yaml" % testsRoot, toLog="logging/shared") != 0:
        writeFail("data_repatriation_test.json", "Error deploying data_repatriation pod.", "logging/shared")

    else:
        fetchResults("repatriation-pod:/home/data_repatriation_test.json", "data_repatriation_test.json", "logging/shared")
        # cleanup
        writeToFile("logging/shared", "Cluster cleanup...", True)
        kubectl(Action.delete, type=Type.pod, name="repatriation-pod")
        res = True

    queue.put(({"test": "dataRepatriationTest", "deployed": res}, testCost))


def cpuBenchmarking():
    """Run containerised CPU Benchmarking test."""

    res = False
    testCost = 0
    with open(testsRoot + "cpu_benchmarking/raw/cpu_benchmarking_pod_raw.yaml", 'r') as infile:
        with open(testsRoot + "cpu_benchmarking/cpu_benchmarking_pod.yaml", 'w') as outfile:
            outfile.write(infile.read().replace("PROVIDER_PH", configs["providerName"]))

    if kubectl(Action.create, file="%scpu_benchmarking/cpu_benchmarking_pod.yaml" % testsRoot, toLog="logging/shared") != 0:
        writeFail("cpu_benchmarking.json", "Error deploying cpu_benchmarking_pod.", "logging/shared")
    else:
        fetchResults("cpu-benchmarking-pod:/tmp/cern-benchmark_root/bmk_tmp/result_profile.json", "cpu_benchmarking.json", "logging/shared")
        # cleanup
        writeToFile("logging/shared", "Cluster cleanup...", True)
        kubectl(Action.delete, type=Type.pod, name="cpu-benchmarking-pod")
        res = True

    queue.put(({"test": "cpuBenchmarking", "deployed": res}, testCost))


def perfsonarTest():
    """Run Networking Performance test -perfSONAR toolkit-."""

    res = False
    testCost = 0
    if kubectl(Action.create, file=testsRoot + "perfsonar/ps_pod.yaml", toLog="logging/shared") != 0:
        writeFail("perfsonar_results.json", "Error deploying perfsonar pod.", "logging/shared")
    else:
        while kubectl(Action.cp, podPath="ps-pod:/tmp", localPath=testsRoot + "perfsonar/ps_test.py", fetch=False) != 0:
            pass  # Copy script to pod
        # Run copied script
        prepareAndRun = "yum -y install python-dateutil python-requests && python /tmp/ps_test.py --ep %s" % testsCatalog[
            "perfsonarTest"]["endpoint"]
        if kubectl(Action.exec, name="ps-pod", cmd=prepareAndRun) != 0:
            writeFail("perfsonar_results.json", "Error running script test on pod.", "logging/shared")
        else:
            fetchResults("ps-pod:/tmp/perfsonar_results.json", "perfsonar_results.json", "logging/shared")
            res = True
            # cleanup
            writeToFile("logging/shared", "Cluster cleanup...", True)
            kubectl(Action.delete, type=Type.pod, name="ps-pod")

    queue.put(({"test": "perfsonarTest", "deployed": res}, testCost))


def dodasTest():
    """Run DODAS test."""

    res = False
    testCost = 0
    if kubectl(Action.create, file=testsRoot + "dodas/dodas_pod.yaml", toLog="logging/shared") != 0:
        writeFail("dodas_test.json", "Error deploying DODAS pod.", "logging/shared")
    else:
        while kubectl(Action.cp, localPath="%sdodas/custom_entrypoint.sh" % testsRoot, podPath="dodas-pod:/CMSSW/CMSSW_9_4_0/src", fetch=False) != 0:
            pass  # Copy script to pod
        # Run copied script
        if kubectl(Action.exec, name="dodas-pod", cmd="sh /CMSSW/CMSSW_9_4_0/src/custom_entrypoint.sh") != 0:
            writeFail("dodas_results.json", "Error running script test on pod.", "logging/shared")
        else:
            fetchResults("dodas-pod:/tmp/dodas_test.json", "dodas_results.json", "logging/shared")
            res = True
            # cleanup
            writeToFile("logging/shared", "Cluster cleanup...", True)
            kubectl(Action.delete, type=Type.pod, name="dodas-pod")

    queue.put(({"test": "dodasTest", "deployed": res}, testCost))


def dlTest():
    """Run Deep Learning test -GAN training- on GPU nodes (Kubeflow, Tensorflow, MPI).

    Returns:
        None: In case of errors the function stops (returns None)
    """

    start = time.time()
    testCost = 0
    dl = testsCatalog["dlTest"]
    if onlyTest is False:
        gpuProvisionment = extraInstanceConfig
        prov, msg = terraformProvisionment(
            "dlTest", dl["nodes"], dl["flavor"], gpuProvisionment, "logging/dlTest")
        if prov is False:
            writeFail("bb_train_history.json", msg, "logging/dlTest")
            return
    else:
        if not checkCluster("dlTest"):
            return  # Cluster not reachable, do not add cost for this test
    res = False

    #### This should be done at the end of this function ##########################
    if obtainCost is True:
        testCost = ((time.time() - start) / 3600) * configs["costCalculation"]["GPUInstancePrice"] * dl["nodes"]
    #########################################################################################################

    #########################################################################################################
    writeFail("bb_train_history.json", "Unable to download training data: bucket endpoint not reachable.", "logging/dlTest")
    queue.put(({"test": "dlTest", "deployed": res}, testCost))
    return
    #########################################################################################################

    # 1) Install the stuff needed for this test: device plugin yaml file (contains driver too) and dl_stack.sh for kubeflow and mpi
    if checkDLsupport() is False and viaBackend is False:  # backend run assumes dl support
        writeToFile("logging/dlTest", "Preparing cluster for DL test...", True)
        retries = 10
        masterIP = runCMD("kubectl --kubeconfig tests/dlTest/config get nodes -owide | grep master | awk '{print $6}'", read=True)
        if runCMD("terraform/ssh_connect.sh --usr root --ip %s --file tests/dlTest/installKubeflow.sh --retries %s" % (masterIP, retries)) != 0:
            writeFail("bb_train_history.json", "Failed to prepare GPU/DL cluster (Kubeflow/Tensorflow/MPI)", "logging/dlTest")
            return
    kubectl(Action.create, file=testsRoot + "dlTest/device_plugin.yaml", ignoreErr=True)
    kubectl(Action.create, file=testsRoot + "dlTest/pv-volume.yaml", ignoreErr=True)
    kubectl(Action.create, file=testsRoot + "dlTest/3dgan-datafile-lists-configmap.yaml", ignoreErr=True)

    # 2) Deploy the required files.
    if dl["nodes"] and isinstance(dl["nodes"], int) and dl["nodes"] > 1 and dl["nodes"]:
        nodesToUse = dl["nodes"]
    else:
        writeToFile("logging/dlTest", "Provided value for 'nodes' not valid or unset, trying to use 5.", True)
        nodesToUse = 5
    with open(testsRoot + 'dlTest/train-mpi_3dGAN_raw.yaml', 'r') as inputfile:
        with open(testsRoot + "dlTest/train-mpi_3dGAN.yaml", 'w') as outfile:
            outfile.write(str(inputfile.read()).replace("REP_PH", str(nodesToUse)))

    if kubectl(Action.create, file=testsRoot + "dlTest/train-mpi_3dGAN.yaml", toLog="logging/dlTest") != 0:
        writeFail("bb_train_history.json",
                  "Error deploying train-mpi_3dGAN.", "logging/dlTest")
    elif runCMD('kubectl describe pods | grep \"Insufficient nvidia.com/gpu\"', read=True):
        writeFail("bb_train_history.json",
                  "Cluster doesn't have enough GPU support. GPU flavor required.", "logging/dlTest")
    else:
        fetchResults("train-mpijob-worker-0:/mpi_learn/bb_train_history.json", "bb_train_history.json", "logging/dlTest")
        res = True
    # cleanup
    writeToFile("logging/dlTest", "Cluster cleanup...", True)
    kubectl(Action.delete, type=Type.mpijob, name="train-mpijob")
    kubectl(Action.delete, type=Type.configmap, name="3dgan-datafile-lists")
    kubectl(Action.delete, type=Type.pv, name="pv-volume1")
    kubectl(Action.delete, type=Type.pv, name="pv-volume2")
    kubectl(Action.delete, type=Type.pv, name="pv-volume3")

    queue.put(({"test": "dlTest", "deployed": res}, testCost))


def hpcTest():
    """HPC test."""

    start = time.time()
    testCost = 0
    hpc = testsCatalog["hpcTest"]
    if onlyTest is False:
        prov, msg = terraformProvisionment(
            "hpcTest", hpc["nodes"], hpc["flavor"], None, "logging/hpcTest")
        if prov is False:
            writeFail("hpcTest_result.json", msg, "logging/hpcTest")
            return
    else:
        if not checkCluster("hpcTest"):
            return  # Cluster not reachable, do not add cost for this test
    writeToFile("logging/hpcTest", "(to be done)", True)
    res = False

    if obtainCost is True:
        testCost = ((time.time() - start) / 3600) * configs["costCalculation"]["HPCInstancePrice"] * hpc["nodes"]

    queue.put(({"test": "hpcTest", "deployed": res}, testCost))
    return  # This is needed in case anything goes wrong and the run has to be killed


def sharedClusterTests(msgArr):
    """Runs the test that shared the general purpose cluster.

    Parameters:
        msgArray (Array<str>): Stuff to show on the banner. Contains the tests to be deployed on the shared cluster.

    Returns:
        None: In case of errors the function stops (returns None)
    """

    start = time.time()
    sharedClusterProcs = []
    testCost = 0
    logger(msgArr, "=", "logging/shared")
    if onlyTest is False:
        # minus 1 because the array contains the string message
        prov, msg = terraformProvisionment(
            "shared", len(msgArr) - 1, None, None, "logging/shared")
        if prov is False:
            writeFail("sharedCluster_result.json", msg, "logging/shared")
            return
    else:
        if not checkCluster("shared"):
            return  # Cluster not reachable, do not add cost for this test
    for test in msgArr[1:]:
        p = Process(target=eval(test))
        sharedClusterProcs.append(p)
        p.start()
    for p in sharedClusterProcs:
        p.join()
    if obtainCost is True:  # duration * instancePrice * numberOfInstances
        testCost = ((time.time() - start) / 3600) * configs["costCalculation"]["generalInstancePrice"] * len(msgArr[1:])
    queue.put((None, testCost))


def checkResultsExist(resDir):
    """Returns True if results exist inside the results folder created, false otherwise

    Parameters:
        resDir (str): Path to the folder to check

    Returns:
        bool: True in case results exist. False otherwise.
    """

    for dirpath, dirnames, files in os.walk(resDir):
        return len(files) > 0


# -----------------CMD OPTIONS---------------------------------------------------
try:
    opts, args = getopt.getopt(
        sys.argv, "ul", ["--only-test", "--via-backend", "--retry"])
except getopt.GetoptError as err:
    writeToFile("logging/header", err, True)
    stop(1)
for arg in args[1:len(args)]:
    if arg == '--only-test':
        writeToFile("logging/header", "(ONLY TEST EXECUTION)", True)
        #runCMD("kubectl delete pods --all", hideLogs=True)
        onlyTest = True
    elif arg == '--retry':
        retry = True
    else:
        writeToFile("logging/header", "Bad option '%s'. Docs at %s " %
                    (arg, publicRepo), True)
        stop(1)

# -----------------CHECKS AND PREPARATION----------------------------------------
if not initAndChecks():
    writeToFile("logging/header", "No tests selected, nothing to do!", True)
    stop(0)


# ----------------CREATE RESULTS FOLDER AND GENERAL FILE------------------------
s3ResDirBase = configs["providerName"] + "/" + \
    str(datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S"))
resDir = "results/%s/detailed" % s3ResDirBase
os.makedirs(resDir)
generalResults = {
    "testing": []
}

# ----------------RUN TESTS-----------------------------------------------------
queue = Queue()
cluster = 1

msgArr = ["CLUSTER %s: (parallel running tests):" % (cluster)]
for test in testsSharingCluster:
    if testsCatalog[test]["run"] is True:
        msgArr.append(test)

if len(msgArr) > 1:
    p = Process(target=sharedClusterTests, args=(msgArr,))
    procs.append(p)
    p.start()
    cluster += 1

for test in customClustersTests:
    if testsCatalog[test]["run"] is True:
        logger("CLUSTER %s: %s" % (cluster, test), "=", "logging/%s" % test)
        p = Process(target=eval(test))
        procs.append(p)
        p.start()
        cluster += 1

for p in procs:  # All tests launched (functions run): wait for completion
    p.join()

while not queue.empty():
    entry, cost = queue.get()
    if entry:
        generalResults["testing"].append(entry)
    totalCost += cost

if checkResultsExist(resDir) is True:
    # ----------------CALCULATE COSTS-----------------------------------------------
    if totalCost > 0:
        generalResults["estimatedCost"] = totalCost
    else:
        writeToFile("logging/footer", "(Required costs aren't correctly set: calculation will not be made)", True)

    # ----------------MANAGE RESULTS------------------------------------------------
    with open("results/" + s3ResDirBase + "/general.json", 'w') as outfile:
        json.dump(generalResults, outfile, indent=4, sort_keys=True)

    msg1 = "TESTING COMPLETED. Results at:"
    # No pushing results in case of local run (only ts-backend has AWS creds for this)
    if viaBackend is True:
        awscliCmd = "aws s3 cp --endpoint-url=https://s3.cern.ch %s s3://ts-results/%s --recursive > /dev/null" % (
            "results/" + s3ResDirBase, s3ResDirBase)
        pushResults = runCMD(awscliCmd)
        runCMD("cp results/%s/general.json .. " % s3ResDirBase)
        if pushResults != 0:
            logger("S3 upload failed! Is 'awscli' installed and configured?",
                   "!", "logging/footer")
        else:
            logger([msg1, "S3 bucket"], "#", "logging/footer")
    else:
        logger([msg1, "results/" + s3ResDirBase], "#", "logging/footer")
else:
    shutil.rmtree("results/" + s3ResDirBase, True)

stop(0)
