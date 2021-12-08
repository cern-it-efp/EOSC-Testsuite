#!/usr/bin/env python3

import sys
try:
    import os
    import time
    import string
    from ansible.module_utils.common.collections import ImmutableDict
    from ansible.parsing.dataloader import DataLoader
    from ansible.vars.manager import VariableManager
    from ansible.inventory.manager import InventoryManager
    from ansible import context
    from ansible.cli import CLI
    from ansible.executor.playbook_executor import PlaybookExecutor
    from configparser import ConfigParser
    from multiprocessing import Process, Queue
    import contextlib
    import io
except ModuleNotFoundError as ex:
    print(ex)
    sys.exit(1)
from aux import *
from init import *


def createHostsFile(mainTfDir,
                    baseCWD,
                    provider,
                    destination,
                    configs,
                    usePrivateIPs,
                    noTerraform=None,
                    test=None):
    """Creates the hosts file required by ansible. Note destination contains
       the string 'hosts' too.

    Parameters:
        mainTfDir (str): Location of the .tf file.
        baseCWD (str): Original location, used to go back.
        provider (str): Provider name.
        destination (str): Destination of hosts file.
        configs (dict): Content of configs.yaml.
        usePrivateIPs (bool): Indicates whether private IPs should be used.
        noTerraform (bool): Specifies whether current run uses terraform.
        test (str): Cluster identification.
    """

    IPs = []

    if noTerraform is True:
        IPs = configs["clusters"][test]  # one of shared, dlTest, hpcTest, proGANTest

    else:
        os.chdir(mainTfDir)
        tfShowJson = json.loads(runCMD("terraform show -json", read=True))
        resources = tfShowJson["values"]["root_module"]["resources"]
        os.chdir(baseCWD)

        for resource in resources:
            ip = getIP(resource, configs, public=not usePrivateIPs)
            if ip is not None and ip not in IPs:
                IPs.append(ip)

    config = ConfigParser(allow_no_value=True)
    config.add_section('master')
    config.add_section('slaves')
    config.set('master', IPs[0])
    for ip in IPs[1:]:
        config.set('slaves', ip)
    with open(destination, 'w') as hostsfile:
        config.write(hostsfile)


def ansiblePlaybook(mainTfDir,
                    baseCWD,
                    providerName,
                    kubeconfig,
                    noTerraform,
                    test,
                    configs,
                    usePrivateIPs,
                    freeMaster):
    """Runs ansible-playbook with the given playbook.

    Parameters:
        mainTfDir (str): Path where the .tf file is.
        baseCWD (str): Path to go back.
        providerName (str): Provider name.
        kubeconfig (str): Path to kubeconfig file.
        noTerraform (bool): Specifies whether current run uses terraform.
        test (str): Cluster identification.
        configs (dict): Content of configs.yaml.
        usePrivateIPs (bool): Indicates whether private IPs should be used.

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
                    usePrivateIPs,
                    noTerraform=noTerraform,
                    test=test)

    loader = DataLoader()

    masterIP = getMasterIP(hostsFilePath)

    context.CLIARGS = ImmutableDict(
        tags={},
        private_key_file=configs["pathToKey"],
        connection='ssh',
        timeout=120,
        remote_user=tryTakeFromYaml(configs, "openUser", "root"),
        become_method='sudo',
        ssh_common_args='-o StrictHostKeyChecking=no',
        extra_vars=[{'kubeconfig': kubeconfig, 'masterIP': masterIP}],
        forks=100,
        verbosity=4, #True,
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

    with open(ansibleLogs % test, 'a') as f: # from now on, logs go to ansibleLogs
        with contextlib.redirect_stdout(f):
            with contextlib.redirect_stderr(f):

                playbooksArray = [playbookPath]

                if not freeMaster:
                    playbooksArray.append("src/provisionment/playbooks/allowMasterRuns.yaml")

                # --------------- GPU support
                if test in ("dlTest", "proGANTest"):
                    playbooksArray.append("src/provisionment/playbooks/gpuSupport.yaml")

                # --------------- MPI support
                if test in ("dlTest", "hpcTest"):
                    playbooksArray.append("src/provisionment/playbooks/kubeflow_mpiOperator.yaml")

                # TODO: this is a workaround for Orange
                if providerName == "flexibleengine":
                    playbooksArray.insert(0, "src/provisionment/playbooks/orange_dns.yaml")

                res = PlaybookExecutor(playbooks=playbooksArray,
                                       inventory=inventory,
                                       variable_manager=variable_manager,
                                       loader=loader,
                                       passwords=None).run(), masterIP

    if aggregateLogs:
        p.terminate()
    return res
