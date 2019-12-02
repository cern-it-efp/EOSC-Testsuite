#!/usr/bin/env python3

from lib.checker import *
from lib.terraform import *
from lib.kubern8s import *  

import time

def dlTest(testsCatalog, onlyTest, extraInstanceConfig, configs, retry, 
dependencies, baseCWD, provDict, extraSupportedClouds, instanceDefinition, 
obtainCost, credentials, resDir, viaBackend):
    """Run Deep Learning test -GAN training- on GPU nodes.

    Returns:
        None: In case of errors the function stops (returns None)
    """

    testsRoot =  "../"
    start = time.time()
    testCost = 0
    dl = testsCatalog["dlTest"]
    kubeconfig = "tests/dlTest/config"
    if onlyTest is False:
        prov, msg = terraformProvisionment("dlTest",
                                           dl["nodes"],
                                           dl["flavor"],
                                           extraInstanceConfig,
                                           "logging/dlTest",
                                           configs,
                                           testsRoot,
                                           retry,
                                           instanceDefinition,
                                           credentials,
                                           dependencies,
                                           baseCWD,
                                           provDict,
                                           extraSupportedClouds)
        if prov is False:
            writeFail(resDir, "bb_train_history.json", msg, "logging/dlTest")
            return
    else:
        if not checkCluster("dlTest"):
            return  # Cluster not reachable, do not add cost for this test
    res = False

    #### This should be done at the end of this function #####################
    if obtainCost is True:
        testCost = ((time.time() - start) / 3600) * \
            configs["costCalculation"]["GPUInstancePrice"] * dl["nodes"]
    ##########################################################################

    ##########################################################################
    writeFail(
        resDir,
        "bb_train_history.json",
        "Unable to download training data: bucket endpoint not reachable.",
        "logging/dlTest")
    ##########################################################################

    # 1) Install the stuff needed for this test: device plugin yaml file
    # (contains driver too) and dl_stack.sh for kubeflow and mpi.
    # (backend run assumes dl support)
    if checkDLsupport() is False and viaBackend is False:
        writeToFile("logging/dlTest", "Preparing cluster for DL test...", True)
        masterIP = runCMD(
            "kubectl --kubeconfig %s get nodes -owide |\
            grep master | awk '{print $6}'" %
            kubeconfig, read=True)
        script = "tests/dlTest/installKubeflow.sh"
        retries = 10
        if runCMD(
            "terraform/ssh_connect.sh --usr root --ip %s\
            --file %s --retries %s" %
                (masterIP, script, retries)) != 0:
            writeFail(
                resDir,
                "bb_train_history.json",
                "Failed to prepare GPU/DL cluster (Kubeflow/Tensorflow/MPI)",
                "logging/dlTest")
            return
    kubectl(Action.create, file=testsRoot +
            "dlTest/device_plugin.yaml", ignoreErr=True)
    kubectl(Action.create, file=testsRoot +
            "dlTest/pv-volume.yaml", ignoreErr=True)
    kubectl(Action.create, file=testsRoot +
            "dlTest/3dgan-datafile-lists-configmap.yaml", ignoreErr=True)

    # 2) Deploy the required files.
    if dl["nodes"] and isinstance(dl["nodes"],
                                  int) and dl["nodes"] > 1 and dl["nodes"]:
        nodesToUse = dl["nodes"]
    else:
        writeToFile(
            "logging/dlTest",
            "Provided value for 'nodes' not valid or unset, trying to use 5.",
            True)
        nodesToUse = 5
    with open(testsRoot + 'dlTest/train-mpi_3dGAN_raw.yaml', 'r') as inputfile:
        with open(testsRoot + "dlTest/train-mpi_3dGAN.yaml", 'w') as outfile:
            outfile.write(str(inputfile.read()).replace(
                "REP_PH", str(nodesToUse)))

    if kubectl(
        Action.create,
        file=testsRoot +
        "dlTest/train-mpi_3dGAN.yaml",
            toLog="logging/dlTest") != 0:
        writeFail(resDir, "bb_train_history.json",
                  "Error deploying train-mpi_3dGAN.", "logging/dlTest")
    elif runCMD(
            'kubectl describe pods | grep \"Insufficient nvidia.com/gpu\"',
            read=True):
        writeFail(
            resDir,
            "bb_train_history.json",
            "Cluster doesn't have enough GPU support. GPU flavor required.",
            "logging/dlTest")
    else:
        fetchResults(
            resDir,
            "train-mpijob-worker-0:/mpi_learn/bb_train_history.json",
            "bb_train_history.json",
            "logging/dlTest")
        res = True
    # cleanup
    writeToFile("logging/dlTest", "Cluster cleanup...", True)
    kubectl(Action.delete, type=Type.mpijob, name="train-mpijob")
    kubectl(Action.delete, type=Type.configmap, name="3dgan-datafile-lists")
    kubectl(Action.delete, type=Type.pv, name="pv-volume1")
    kubectl(Action.delete, type=Type.pv, name="pv-volume2")
    kubectl(Action.delete, type=Type.pv, name="pv-volume3")

    return ({"test": "dlTest", "deployed": res}, testCost)