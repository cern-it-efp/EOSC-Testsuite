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

except ModuleNotFoundError as ex:
    print(ex)
    sys.exit(1)

from aux import *
Action = Enum('Action', 'create delete cp exec')
Type = Enum('Type', 'pod daemonset mpijob configmap pv')


def main():
    print(kubectl(Action.cp, localPath="./thisFile",
                  podPath="ps-pod:/tmp", fetch=False))
    #kubectl(Action.cp, localPath="/var/jenkins_home", podPath="ps-pod:/tmp/illofile", fetch=True)
    #kubectl(Action.cp, podPath="ps-pod:/tmp/illofile", localPath="/var/jenkins_home", fetch=True)


def checkDestinationIsDir(podName, pathOnPod, namespace=None):
    """Checks -in the case of copy to pod- if the destination is a directory.

    Parameters:
        podName (str): Name of the pod to which the file has to be sent
        pathOnPod (str): Path within the pod to locate the file
        namespace (str): Kubernetes namespace on which the pod is deployed

    Returns:
        bool: True means dest is a directory on the pod, False otherwise.
    """

    return True  # THIS IS A HACK

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

    config.load_kube_config()

    if namespace is None:
        namespace = "default"

    if action is Action.exec:
        try:
            resp = stream(
                client.CoreV1Api().connect_get_namespaced_pod_exec,
                name,
                namespace="default",
                command=[
                    '/bin/bash',
                    '-c',
                    cmd],
                stderr=True,
                stdin=True,
                stdout=True,
                tty=False)
        except BaseException:
            res = False

    # TODO: failing when fetch=True (at least): on jenkins (cern-openshift), jenkins run locally (docker)(?)
    elif action is Action.cp:

        podName = podPath.split(':')[0]
        # remove ending '/' if exists
        pathOnPod = re.sub("[/]$", "", podPath.split(':')[1])
        # remove ending '/' if exists
        localPath = re.sub("[/]$", "", localPath)

        with NamedTemporaryFile() as tarBuffer:
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

            resp = stream(
                client.CoreV1Api().connect_get_namespaced_pod_exec,
                podName,
                namespace=namespace,
                command=execCommand,
                stderr=True,
                stdin=True,
                stdout=True,
                tty=False,
                _preload_content=False)

            while resp.is_open():
                resp.update(timeout=1)

                print(commands)

                if resp.peek_stdout():
                    print("STDOUT: %s" % resp.read_stdout())
                if not fetch and commands:
                    resp.write_stdin(commands.pop(0).decode())
                    # UnicodeDecodeError: 'utf-8' codec can't decode byte 0x80 in position 108: invalid start byte
            resp.close()

            tarBuffer.flush()
            tarBuffer.seek(0)

    return 0 if res is True else 1

main()
