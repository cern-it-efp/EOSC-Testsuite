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
from kubernetesFunctions import *
from ansibleFunctions import *
from terraformFunctions import *


bootstrapFailMsg = "Failed to bootstrap '%s' k8s cluster. Check 'logs' file"
msgRoot = "WARNING: default user 'root' for ssh connections (running on %s)"
clusterCreatedMsg = "...%s CLUSTER CREATED (masterIP: %s) => STARTING TESTS\n"
TOserviceAccountMsg = "ERROR: timed out waiting for %s cluster's service account\n"


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
        extraSupportedClouds (dict): Extra supported clouds.

    Returns:
        bool: True if the cluster was succesfully provisioned. False otherwise.
        str: Message informing of the provisionment task result.
    """

    #TODO: the calls to terraform and ansible should all be done from here (currently terraformFunctions calls ansiblePlaybook, bc of calling terraformProvisionment in line 113 here)

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
                writeToFile(toLog, clusterCreatedMsg % (test, masterIP), True)
                return True, ""
            else:
                return False, TOserviceAccountMsg % test

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
                                      extraSupportedClouds)
