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
from checker import * # TODO: in case of fail, move checkPodAlive from checker.py here


Action = Enum('Action', 'create delete cp exec')
Type = Enum('Type', 'pod daemonset mpijob configmap pv')


def checkCluster(test):
    """ Returns True if the cluster is reachable

    Parameters:
        test (str): Check this test's cluster

    Returns:
        bool: True in case the cluster is reachable. False otherwise
    """

    cmd = "kubectl get nodes --request-timeout=4s"
    if test != "shared":
        cmd += " --kubeconfig src/tests/%s/config" % (test)
    if runCMD(cmd, hideLogs=True) != 0:
        writeToFile(
            "src/logging/%s" % test,
            "%s cluster not reachable, was infrastructure created?" % test,
            True)
        return False
    return True


def fetchResults_while(resDir, pod, source, file, toLog): # the original
    """Fetch tests results file from pod.

    Parameters:
        resDir (str): Path to the results dir for the current run.
        pod (str): Pod from which the result file has to be collected.
        source (str): Location of the results file on the pod.
        file (str): Name to be given to the file.
        toLog (str): Path to the log file to which logs have to be sent
    """

    source = "%s:%s" % (pod,source)
    while os.path.exists(resDir + "/" + file) is False:
        with contextlib.redirect_stdout(io.StringIO()):  # to hide logs
            print("Fetching results...")
            kubectl(Action.cp, podPath=source, localPath="%s/%s" %
                    (resDir, file), fetch=True)
    writeToFile(toLog, file + " fetched!", True)


def fetchResults_if(resDir, pod, source, file, toLog):
    """Fetch tests results file from pod.

    Parameters:
        resDir (str): Path to the results dir for the current run.
        pod (str): Pod from which the result file has to be collected.
        source (str): Location of the results file on the pod.
        file (str): Name to be given to the file.
        toLog (str): Path to the log file to which logs have to be sent
    """

    source = "%s:%s" % (pod,source)
    if os.path.exists(resDir + "/" + file) is False:
        with contextlib.redirect_stdout(io.StringIO()):  # to hide logs
            print("Fetching results...")
            kubectl(Action.cp, podPath=source, localPath="%s/%s" %
                    (resDir, file), fetch=True)
    else:
        writeToFile(toLog, file + " fetched!", True)


def fetchResults_simple(resDir, pod, source, file):
    """Fetch tests results file from pod.

    Parameters:
        resDir (str): Path to the results dir for the current run.
        pod (str): Pod from which the result file has to be collected.
        source (str): Location of the results file on the pod.
        file (str): Name to be given to the file.
    """

    source = "%s:%s" % (pod,source)
    with contextlib.redirect_stdout(io.StringIO()):  # to hide logs
        print("Fetching results...")
        kubectl(Action.cp, podPath=source, localPath="%s/%s" %
                (resDir, file), fetch=True)


def fetchResults(resDir, podName, source, file, toLog):
    """Fetch tests results file from pod.

    Parameters:
        resDir (str): Path to the results dir for the current run.
        pod (str): Pod from which the result file has to be collected.
        source (str): Location of the results file on the pod.
        file (str): Name to be given to the file.
    """

    source = "%s:%s" % (podName,source)
    while os.path.exists(resDir + "/" + file) is False:
        if checkPodAlive(podName,
                         resDir,
                         toLog,
                         file) is False: return
        with contextlib.redirect_stdout(io.StringIO()):  # to hide logs
            print("Fetching results...")
            kubectl(Action.cp, podPath=source, localPath="%s/%s" %
                    (resDir, file), fetch=True)
    writeToFile(toLog, file + " fetched!", True)


def copyToPod(podName, resDir, toLog, file, podPath, localPath):
    """Copy from local to pod"""

    while True:
        if checkPodAlive(podName,
                         resDir,
                         toLog,
                         file) is False: return
        if kubectl(Action.cp,
                  podPath=podPath,
                  localPath=localPath,
                  fetch=False) == 0:
            break


def checkDestinationIsDir(podName, pathOnPod, namespace=None):
    """Checks -in the case of copy to pod- if the destination is a directory.

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
    """Resets tar file's user related metadata (uid and name).

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
        type=None,
        name=None,
        file=None,
        cmd=None,
        kubeconfig=None,
        namespace=None,
        podPath=None,
        localPath=None,
        fetch=None,
        toLog=None,
        ignoreErr=None):
    """Manage stuff on a Kubernetes cluster.

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
                client.CustomObjectsApi().create_namespaced_custom_object(
                    'kubeflow.org',
                    'v1alpha1',
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
                        'v1alpha1',
                        namespace,
                        'mpijobs',
                        name,
                        client.V1DeleteOptions())
                except BaseException:
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
