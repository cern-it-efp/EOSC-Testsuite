#!/usr/bin/env python3

import sys
try:
    import yaml
    import json
    from kubernetes import client, config, utils
    from kubernetes.stream import stream
    from kubernetes.client.rest import ApiException
    from tempfile import NamedTemporaryFile
    import jsonschema
    import os
    import re
    import tarfile
    from pathlib import Path
    from enum import Enum
    import contextlib
    import io

except ModuleNotFoundError as ex:
    print(ex)
    sys.exit(1)

from aux import *
from checker import *


Action = Enum('Action', 'create delete cp exec')
Type = Enum('Type', 'pod daemonset mpijob configmap pv sa')


def checkCluster(test):
    """ Returns True if the cluster is reachable

    Parameters:
        test (str): Check this test's cluster

    Returns:
        bool: True in case the cluster is reachable. False otherwise
    """

    cmd = 'get nodes'
    opts = '--request-timeout=10s'
    kubeconfig = "src/tests/%s/config" % (test)

    if kubectlCLI(cmd, options=opts, kubeconfig=kubeconfig, hideLogs=True) != 0:
        writeToFile(
            "src/logging/%s" % test,
            "%s cluster not reachable, was infrastructure created?" % test,
            True)
        return False
    return True


def checkPodAlive(podName, resDir, toLog, resultFile, kubeconfig):
    """ Checks if a pod is alive

    Parameters:
        podName (str): Pod name.
        resDir (str): Path to the results folder for the current run.
        toLog (str): Path to the log file to which logs have to be sent
        resultFile (str): Name of the results file for the current test.
        kubeconfig (str): Path to kubeconfig file of the being managed cluster.

    Returns:
        bool: True in case the pod is alive, False otherwise
    """

    # kubectl get pods -o=json | jq .items[].metadata.name

    v1 = client.CoreV1Api()

    ############ TODO: list_namespaced_pod times out if the connection is lost
    while True:
        try:
            ret = v1.list_namespaced_pod("default")
            break
        except ApiException: # kubernetes.client.exceptions.ApiException,
            print("WARNING: Error from server: etcdserver - request timed out" \
                   " (%s). Retrying in 5 seconds" % podName)
            time.sleep(5)
    ############################################################################

    podNames = [i.metadata.name for i in ret.items] # i.status.pod_ip
    if podName not in podNames:
        writeFail(resDir,
                  resultFile,
                  "%s pod was destroyed (did not fetch %s)" % (podName,resultFile),
                  toLog)
        return False
    return True


def checkPodAlive_og(podName, resDir, toLog, resultFile, kubeconfig):
    """ Checks if a pod is alive

    Parameters:
        podName (str): Pod name.
        resDir (str): Path to the results folder for the current run.
        toLog (str): Path to the log file to which logs have to be sent
        resultFile (str): Name of the results file for the current test.
        kubeconfig (str): Path to kubeconfig file of the being managed cluster.

    Returns:
        bool: True in case the pod is alive, False otherwise
    """

    cmd = "get pod %s" % podName
    if kubectlCLI(cmd, kubeconfig=kubeconfig, hideLogs=True) != 0:
        writeFail(resDir,
                  resultFile,
                  "%s pod was destroyed (did not fetch %s)" % (podName,resultFile),
                  toLog)
        return False
    return True


def waitForResource(resourceName, resourceType, kubeconfig, retrials=None, sleepTime=None):
    """ Waits until the given resource is deployed, i.e. visible by kubectl. If
        after a specific number of retrials this does not happen, returns False.

    Parameters:
        resourceName (str): Resource name.
        resourceType (str): Resource type.
        kubeconfig (str): Path to kubeconfig file of the being managed cluster.
        retrials (int): Number of retrials.
        sleepTime (int): Sleep time in seconds between retrials.

    Returns:
        bool: True in case the resource is present, False otherwise
    """

    if retrials is None:
        retrials = 2
    if sleepTime is None:
        sleepTime = 2
    for i in range(retrials):
        cmd = "get %s %s" % (resourceType.name, resourceName)
        if kubectlCLI(cmd, kubeconfig=kubeconfig, hideLogs=True) == 0:
            return True
        print("Rsource of type '%s' with name '%s' not ready yet..." % (resourceType, resourceName))
        time.sleep(sleepTime)
    return False


def waitForPod(podName, kubeconfig, retrials=None, sleepTime=None):
    """ Waits until the given pod is deployed, i.e. visible by kubectl. If
        after a specific number of retrials this does not happen, returns False.

    Parameters:
        podName (str): Pod name.
        kubeconfig (str): Path to kubeconfig file of the being managed cluster.
        retrials (int): Number of retrials.
        sleepTime (int): Sleep time in seconds between retrials.

    Returns:
        bool: True in case the pod was deployed, False otherwise
    """

    if retrials is None:
        retrials = 2
    if sleepTime is None:
        sleepTime = 2
    for i in range(retrials):
        cmd = "get pod %s" % podName
        if kubectlCLI(cmd, kubeconfig=kubeconfig, hideLogs=True) == 0:
            return True
        print("Pod %s not ready yet..." % podName)
        time.sleep(sleepTime)
    return False


def fetchResults(resDir, kubeconfig, podName, source, file, toLog):
    """ Fetch tests results file from pod.

    Parameters:
        resDir (str): Path to the results dir for the current run.
        kubeconfig (str): Path to kubeconfig file of the being managed cluster.
        podName (str): Pod name.
        source (str): Location of the results file on the pod.
        file (str): Name to be given to the file.
        toLog (str): Path to the log file to which logs have to be sent
    """

    source = "%s:%s" % (podName,source)
    while os.path.exists(resDir + "/" + file) is False:
        if checkPodAlive(podName,
                         resDir,
                         toLog,
                         file,
                         kubeconfig) is False: return
        with contextlib.redirect_stdout(io.StringIO()):  # to hide logs
            print("Fetching results...")
            kubectl(Action.cp, kubeconfig, podPath=source, localPath="%s/%s" %
                    (resDir, file), fetch=True)
    writeToFile(toLog, file + " fetched!", True)


def copyToPodAndRun(
        podName,
        kubeconfig,
        resDir,
        toLog,
        podPath,
        localPath,
        cmd,
        resultFile,
        resultOnPod):
    """ Copy from local FS to pod, run and fetch results.

    Parameters:
        podName (str): Pod name.
        kubeconfig (str): Path to kubeconfig file of the being managed cluster.
        resDir (str): Path to the results folder for the current run.
        toLog (str): Path to the log file to which logs have to be sent
        podPath (str): Pod path in case of 'cp'
        localPath (str): Local path in case of 'cp'
        cmd (str): Command to be run.
        resultFile (str): Name of the results file for the current test.
        resultOnPod (str): Path to the result file on the pod.
    """

    with contextlib.redirect_stdout(io.StringIO()):  # to hide logs
        while True:
            if checkPodAlive(podName,
                             resDir,
                             toLog,
                             resultFile,
                             kubeconfig) is False: return
            if kubectl(Action.cp,
                      kubeconfig,
                      podPath=podPath,
                      localPath=localPath,
                      fetch=False) == 0:
                break
    if kubectl(Action.exec, kubeconfig, name=podName, cmd=cmd) != 0:
        writeFail(resDir,
                  resultFile,
                  "Error running script test on pod %s" % podName,
                  toLog)
    else:
        fetchResults(resDir,kubeconfig,podName,resultOnPod,resultFile,toLog)


def checkDestinationIsDir(podName, pathOnPod, namespace=None):
    """ Checks -in the case of copy to pod- if the destination is a directory.

    Parameters:
        podName (str): Name of the pod to which the file has to be sent
        pathOnPod (str): Path within the pod to locate the file
        namespace (str): Kubernetes namespace where the pod is deployed

    Returns:
        bool: True means dest is a directory on the pod, False otherwise.
    """

    if namespace is None:
        namespace = "default"
    cmd = "test -d %s ; echo $?" % pathOnPod
    resp = stream(
        client.CoreV1Api().connect_get_namespaced_pod_exec,
        podName,
        namespace,
        command=[
            '/bin/bash',
            '-c',
            cmd],
        stderr=True,
        stdin=True,
        stdout=True,
        tty=False)
    if int(resp) == 1:
        return False
    return True


def reset(tarinfo):
    """ Resets tar file's user related metadata (uid and name).

    Parameters:
        tarinfo (TarInfo): TarInfo object.

    Returns:
        TarInfo: returns the modified TarInfo object received.
    """

    tarinfo.uid = tarinfo.gid = 0
    tarinfo.uname = tarinfo.gname = "root"
    return tarinfo


def kubectl(
        action,
        kubeconfig,
        type=None,
        name=None,
        file=None,
        cmd=None,
        namespace=None,
        podPath=None,
        localPath=None,
        fetch=None,
        toLog=None,
        ignoreErr=None):
    """ Manage stuff on a Kubernetes cluster.

    Parameters:
        action (str): Action to be carried out. One of: create, delete or cp.
        type (str): Resource type in case of 'delete'.
        name (str): Resource name.
        file (str): YAML defining the resource to create in case of 'create'.
        cmd (str): Command to be run in case of 'exec'.
        kubeconfig (str): Path to kubeconfig file of the being managed cluster.
        namespace (str): Namespace on which to carry the action.
        podPath (str): Pod path in case of 'cp'
        localPath (str): Local path in case of 'cp'
        fetch (bool): True indicates copy from pod to local, False vice versa.
        toLog (str): Path to the log file to which logs have to be sent
        ignoreErr (bool): If True, catch exception and continue (if errors)

    Returns:
        int: 0 for success, 1 for failure
    """

    res = True
    config.load_kube_config(config_file=kubeconfig)

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
                client.CustomObjectsApi().create_namespaced_custom_object(
                    'kubeflow.org',
                    'v1alpha2',
                    namespace,
                    'mpijobs',
                    body)
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
        except BaseException:
            if ignoreErr is not True:
                res = False

    elif action is Action.delete:
        try:
            if type is Type.pod:
                client.CoreV1Api().delete_namespaced_pod(
                    name=name, namespace=namespace)
            elif type is Type.daemonset:
                client.AppsV1Api().delete_namespaced_daemon_set(
                    name=name, namespace=namespace)
            elif type is Type.mpijob:
                try:
                    client.CustomObjectsApi().delete_namespaced_custom_object(
                        'kubeflow.org',
                        'v1alpha2',
                        namespace,
                        'mpijobs',
                        name)
                        #client.V1DeleteOptions())
                except BaseException as ex:
                    print(ex)
                    res = False
            elif type is Type.configmap:
                client.CoreV1Api().delete_namespaced_config_map(
                    name=name, namespace=namespace)
            elif type is Type.pv:
                client.CoreV1Api().delete_persistent_volume(name=name)
        except BaseException:
            res = False

    elif action is Action.exec:
        try:
            # w/a to get the exit code
            cmd = "(%s) &> /dev/null ; echo $?" % cmd
            resp = stream(
                client.CoreV1Api().connect_get_namespaced_pod_exec,
                name,
                namespace,
                command=[
                    '/bin/bash',
                    '-c',
                    cmd],
                stderr=True,
                stdin=True,
                stdout=True,
                tty=False)
            # ------------------------------------------
            #print("resp raw: " + resp)
            resp = int(resp)
            #print("resp cast to int: " + str(resp))
            # ------------------------------------------
            return resp
        except BaseException as e:
            print("Exception at .exec" + str(e))
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
                        tar.add(localPath, arcname=fileNameOnDest, filter=reset)
                    tarBuffer.seek(0)
                    commands = [tarBuffer.read()]

                resp = stream(
                    client.CoreV1Api().connect_get_namespaced_pod_exec,
                    podName,
                    namespace,
                    command=execCommand,
                    stderr=True,
                    stdin=True,
                    stdout=True,
                    tty=False,
                    _preload_content=False)

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
                        # check if localPath is a locally existing directory.
                        if os.path.isdir(localPath) is False:
                            member.name = os.path.basename(localPath)
                            localPath = os.path.dirname(localPath)
                        tar.extract(member, localPath)
                        tar.close()
                    except IndexError as e:  # File not found
                        print(e)
                        res = False
        except BaseException as e:
            print(e)
            res = False

    return 0 if res is True else 1


def kubectlCLI(cmd, kubeconfig, options="", hideLogs=None, read=None):
    """ Runs kubectl CLI tool.

    Parameters:
        cmd (str): Command to be run, without the "kubectl" part.
        kubeconfig (str): Path to kubeconfig file.
        options (str): Options to be added to the command.
        hideLogs (bool): Specifies whether the output of the
                         command should be displayed.

    Returns:
        int: Exit code of the kubectl command.
    """

    kubeconfig = '--kubeconfig=%s' % kubeconfig
    kubeCMD = "kubectl %s %s %s" % (kubeconfig,cmd,options)
    return runCMD(kubeCMD, hideLogs=hideLogs, read=read)


def getGpusPerNode(kubeconfig):
    """ Gets the number of GPUs each node has.

    Parameters:
        kubeconfig (str): Path to a kubeconfig file.

    Returns:
        Integer: Number of GPUs each node has.
    """

    cmd = "get nodes"
    options = "-ojson | jq '.items[0].status.allocatable.\"nvidia.com/gpu\"'"
    gpusPerNode = 0
    tries = 60
    while gpusPerNode == 0 and tries != 0:
        time.sleep(2)
        kubectlResponse = kubectlCLI(cmd, kubeconfig, options=options, read=True) # "kubectl get nodes -ojson | jq '.items[0].status.allocatable.\"nvidia.com/gpu\"'"
        print("From kubectl: %s" % str(kubectlResponse))
        try:
            gpusPerNode = int(kubectlResponse.replace("\"",""))
        except ValueError:
            gpusPerNode = 0
        print("End of attempt %s: %s" % (tries, str(gpusPerNode)))
        tries -= 1
    if gpusPerNode == 0:
        print("ERROR: Cluster %s doesn't have GPUs or is missing support for them!" % kubeconfig)
    return gpusPerNode


def updateKubeconfig(masterIP, kubeconfig):
    """ Updates the given kubeconfig file.
        Done after fetching a kubeconfig file and before checking the SA.

    Parameters:
        masterIP (str): IP address of the master node.
        kubeconfig (str): Path to a kubeconfig file.
    """

    kubeconfigContent = loadYAML(kubeconfig)
    address = "https://%s:6443"
    kubeconfigContent["clusters"][0]["cluster"]["server"] = address % masterIP

    yaml.dump(kubeconfigContent, open(kubeconfig, 'w'))
