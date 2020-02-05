#!/usr/bin/env python3

from checker import *
from provisionment import *
from kubern8s import *
from aux import *
from multiprocessing import Process, Queue

import init


def sharedClusterTests(msgArr,onlyTest,retry,noTerraform,resDir):
    """Runs the test that shared the general purpose cluster.

    Parameters:
        msgArray (Array<str>): Stuff to show on the banner. Contains the
                               tests to be deployed on the shared cluster.

    Returns:
        None: In case of errors the function stops (returns None)
    """

    start = time.time()
    sharedClusterProcs = []
    testCost = 0
    logger(msgArr, "=", "src/logging/shared")
    if onlyTest is False:
        prov, msg = provisionAndBootstrap("shared",
                                           len(msgArr) - 1,
                                           None,
                                           None,
                                           "src/logging/shared",
                                           init.configs,
                                           testsRoot,
                                           retry,
                                           instanceDefinition,
                                           credentials,
                                           dependencies,
                                           baseCWD,
                                           provDict,
                                           extraSupportedClouds,
                                           noTerraform)
        if prov is False:
            writeFail(resDir, "sharedCluster_result.json",
                      msg, "src/logging/shared")
            return
    else:
        if not checkCluster("shared"):
            return  # Cluster not reachable, do not add cost for this test
    for test in msgArr[1:]:
        p = Process(target=eval(test),args=(resDir,))
        sharedClusterProcs.append(p)
        p.start()
    for p in sharedClusterProcs:
        p.join()
    if init.obtainCost is True:  # duration * instancePrice * numberOfInstances
        testCost = ((time.time() - start) / 3600) * \
            init.configs["costCalculation"]["generalInstancePrice"] * \
            len(msgArr[1:])
    init.queue.put((None, testCost))


def s3Test(resDir):
    """Run S3 endpoints test."""

    res = False
    testCost = 0
    with open(testsRoot + "s3/raw/s3pod_raw.yaml", 'r') as infile:
        with open(testsRoot + "s3/s3pod.yaml", 'w') as outfile:
            outfile.write(
                infile.read().replace(
                    "ENDPOINT_PH",
                    init.testsCatalog["s3Test"]["endpoint"]) .replace(
                    "ACCESS_PH",
                    init.testsCatalog["s3Test"]["accessKey"]) .replace(
                    "SECRET_PH",
                    init.testsCatalog["s3Test"]["secretKey"]))

    start = time.time()  # create bucket
    if kubectl(
        Action.create,
        file=testsRoot +
        "s3/s3pod.yaml",
            toLog="src/logging/shared") != 0:
        writeFail(resDir, "s3Test.json",
                  "Error deploying s3pod.", "src/logging/shared")
    else:
        fetchResults(resDir, "s3pod:/home/s3_test.json",
                     "s3_test.json", "src/logging/shared")
        end = time.time()  # bucket deletion
        # cleanup
        writeToFile("src/logging/shared", "Cluster cleanup...", True)
        kubectl(Action.delete, type=Type.pod, name="s3pod")
        res = True
        if init.obtainCost is True:
            testCost = float(init.configs["costCalculation"]
                             ["s3bucketPrice"]) * (end - start) / 3600

    init.queue.put(({"test": "s3Test", "deployed": res}, testCost))


def dataRepatriationTest(resDir):
    """Run Data Repatriation Test -Exporting from cloud to Zenodo-."""

    res = False
    testCost = 0
    with open(testsRoot + "data_repatriation/raw/repatriation_pod_raw.yaml",
              'r') as infile:
        with open(testsRoot + "data_repatriation/repatriation_pod.yaml",
                  'w') as outfile:
            outfile.write(infile.read().replace(
                "PROVIDER_PH", init.configs["providerName"]))

    if kubectl(
            Action.create,
            file="%sdata_repatriation/repatriation_pod.yaml" %
            testsRoot,
            toLog="src/logging/shared") != 0:
        writeFail(resDir, "data_repatriation_test.json",
                  "Error deploying data_repatriation pod.", "src/logging/shared")

    else:
        fetchResults(
            resDir,
            "repatriation-pod:/home/data_repatriation_test.json",
            "data_repatriation_test.json",
            "src/logging/shared")
        # cleanup
        writeToFile("src/logging/shared", "Cluster cleanup...", True)
        kubectl(Action.delete, type=Type.pod, name="repatriation-pod")
        res = True

    init.queue.put(({"test": "dataRepatriationTest", "deployed": res}, testCost))


def cpuBenchmarking(resDir):
    """Run containerised CPU Benchmarking test."""

    res = False
    testCost = 0
    with open(testsRoot + "cpu_benchmarking/raw/cpu_benchmarking_pod_raw.yaml",
              'r') as infile:
        with open(testsRoot + "cpu_benchmarking/cpu_benchmarking_pod.yaml",
                  'w') as outfile:
            outfile.write(infile.read().replace(
                "PROVIDER_PH", init.configs["providerName"]))

    if kubectl(
            Action.create,
            file="%scpu_benchmarking/cpu_benchmarking_pod.yaml" %
            testsRoot,
            toLog="src/logging/shared") != 0:
        writeFail(resDir, "cpu_benchmarking.json",
                  "Error deploying cpu_benchmarking_pod.", "src/logging/shared")
    else:
        fetchResults(
            resDir,
            "cpu-bmk-pod:/tmp/cern-benchmark_root/bmk_tmp/result_profile.json",
            "cpu_benchmarking.json",
            "src/logging/shared")
        # cleanup
        writeToFile("src/logging/shared", "Cluster cleanup...", True)
        kubectl(Action.delete, type=Type.pod, name="cpu-bmk-pod")
        res = True

    init.queue.put(({"test": "cpuBenchmarking", "deployed": res}, testCost))


def perfsonarTest(resDir):
    """Run Networking Performance test -perfSONAR toolkit-."""

    res = False
    testCost = 0
    endpoint = init.testsCatalog["perfsonarTest"]["endpoint"]
    if kubectl(
        Action.create,
        file=testsRoot +
        "perfsonar/ps_pod.yaml",
            toLog="src/logging/shared") != 0:
        writeFail(resDir, "perfsonar_results.json",
                  "Error deploying perfsonar pod.", "src/logging/shared")
    else:
        while kubectl(
            Action.cp,
            podPath="ps-pod:/tmp",
            localPath=testsRoot +
            "perfsonar/ps_test.py",
                fetch=False) != 0:
            pass  # Copy script to pod
        # Run copied script
        dependenciesCMD = "yum -y install python-dateutil python-requests"
        runScriptCMD = "python /tmp/ps_test.py --ep %s" % endpoint
        runOnPodCMD = "%s && %s" % (dependenciesCMD, runScriptCMD)
        if kubectl(Action.exec, name="ps-pod", cmd="%s" % runOnPodCMD) != 0:
            writeFail(resDir, "perfsonar_results.json",
                      "Error running script test on pod.", "src/logging/shared")
        else:

            fetchResults(resDir, "ps-pod:/tmp/perfsonar_results.json",
                         "perfsonar_results.json", "src/logging/shared")
            res = True
        # cleanup
        writeToFile("src/logging/shared", "Cluster cleanup...", True)
        kubectl(Action.delete, type=Type.pod, name="ps-pod")

    init.queue.put(({"test": "perfsonarTest", "deployed": res}, testCost))


def dodasTest(resDir):
    """Run DODAS test."""

    res = False
    testCost = 0
    if kubectl(
        Action.create,
        file=testsRoot +
        "dodas/dodas_pod.yaml",
            toLog="src/logging/shared") != 0:
        writeFail(resDir, "dodas_test.json",
                  "Error deploying DODAS pod.", "src/logging/shared")
    else:
        while kubectl(
                Action.cp,
                localPath="%sdodas/custom_entrypoint.sh" %
                testsRoot,
                podPath="dodas-pod:/CMSSW/CMSSW_9_4_0/src",
                fetch=False) != 0:
            pass  # Copy script to pod
        # Run copied script
        if kubectl(
                Action.exec,
                name="dodas-pod",
                cmd="sh /CMSSW/CMSSW_9_4_0/src/custom_entrypoint.sh") != 0:
            writeFail(resDir, "dodas_results.json",
                      "Error running script test on pod.", "src/logging/shared")
        else:
            fetchResults(resDir, "dodas-pod:/tmp/dodas_test.json",
                         "dodas_results.json", "src/logging/shared")
            res = True
        # cleanup
        writeToFile("src/logging/shared", "Cluster cleanup...", True)
        kubectl(Action.delete, type=Type.pod, name="dodas-pod") # TODO: debug

    init.queue.put(({"test": "dodasTest", "deployed": res}, testCost))


def dlTest(onlyTest,retry,noTerraform,resDir):
    """Run Deep Learning test -GAN training- on GPU nodes.

    Returns:
        None: In case of errors the function stops (returns None)
    """

    start = time.time()
    testCost = 0
    dl = init.testsCatalog["dlTest"]
    kubeconfig = "src/tests/dlTest/config"
    if onlyTest is False:
        prov, msg = provisionAndBootstrap("dlTest",
                                           dl["nodes"],
                                           dl["flavor"],
                                           extraInstanceConfig,
                                           "src/logging/dlTest",
                                           init.configs,
                                           testsRoot,
                                           retry,
                                           instanceDefinition,
                                           credentials,
                                           dependencies,
                                           baseCWD,
                                           provDict,
                                           extraSupportedClouds,
                                           noTerraform)
        if prov is False:
            writeFail(resDir, "bb_train_history.json", msg, "src/logging/dlTest")
            return
    else:
        if not checkCluster("dlTest"):
            return  # Cluster not reachable, do not add cost for this test
    res = False

    #### This should be done at the end of this function #####################
    if init.obtainCost is True:
        testCost = ((time.time() - start) / 3600) * \
            init.configs["costCalculation"]["GPUInstancePrice"] * dl["nodes"]
    ##########################################################################

    ##########################################################################
    writeFail(
        resDir,
        "bb_train_history.json",
        "Unable to download training data: bucket endpoint not reachable.",
        "src/logging/dlTest")
    init.queue.put(({"test": "dlTest", "deployed": res}, testCost))
    return
    ##########################################################################

    # 1) Install the stuff needed for this test: device plugin yaml file
    # (contains driver too) and dl_stack.sh for kubeflow and mpi.
    # (backend run assumes dl support)
    if checkDLsupport() is False and viaBackend is False:
        writeToFile("src/logging/dlTest", "Preparing cluster for DL test...", True)
        masterIP = runCMD(
            "kubectl --kubeconfig %s get nodes -owide |\
            grep master | awk '{print $6}'" %
            kubeconfig, read=True)
        script = "src/tests/dlTest/installKubeflow.sh"
        retries = 10
        if runCMD(
            "src/provisionment/ssh_connect.sh --usr root --ip %s\
            --file %s --retries %s" %
                (masterIP, script, retries)) != 0:
            writeFail(
                resDir,
                "bb_train_history.json",
                "Failed to prepare GPU/DL cluster (Kubeflow/Tensorflow/MPI)",
                "src/logging/dlTest")
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
            "src/logging/dlTest",
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
            toLog="src/logging/dlTest") != 0:
        writeFail(resDir, "bb_train_history.json",
                  "Error deploying train-mpi_3dGAN.", "src/logging/dlTest")
    elif runCMD(
            'kubectl describe pods | grep \"Insufficient nvidia.com/gpu\"',
            read=True):
        writeFail(
            resDir,
            "bb_train_history.json",
            "Cluster doesn't have enough GPU support. GPU flavor required.",
            "src/logging/dlTest")
    else:
        fetchResults(
            resDir,
            "train-mpijob-worker-0:/mpi_learn/bb_train_history.json",
            "bb_train_history.json",
            "src/logging/dlTest")
        res = True
    # cleanup
    writeToFile("src/logging/dlTest", "Cluster cleanup...", True)
    kubectl(Action.delete, type=Type.mpijob, name="train-mpijob")
    kubectl(Action.delete, type=Type.configmap, name="3dgan-datafile-lists")
    kubectl(Action.delete, type=Type.pv, name="pv-volume1")
    kubectl(Action.delete, type=Type.pv, name="pv-volume2")
    kubectl(Action.delete, type=Type.pv, name="pv-volume3")

    init.queue.put(({"test": "dlTest", "deployed": res}, testCost))


def hpcTest(onlyTest,retry,noTerraform,resDir):
    """HPC test.

    Returns:
        None: In case of errors the function stops (returns None)
    """

    start = time.time()
    testCost = 0
    hpc = init.testsCatalog["hpcTest"]
    if onlyTest is False:
        prov, msg = provisionAndBootstrap("hpcTest",
                                           hpc["nodes"],
                                           hpc["flavor"],
                                           None,
                                           "src/logging/hpcTest",
                                           init.configs,
                                           testsRoot,
                                           retry,
                                           instanceDefinition,
                                           credentials,
                                           dependencies,
                                           baseCWD,
                                           provDict,
                                           extraSupportedClouds,
                                           noTerraform)
        if prov is False:
            writeFail(resDir, "hpcTest_result.json", msg, "src/logging/hpcTest")
            return
    else:
        if not checkCluster("hpcTest"):
            return  # Cluster not reachable, do not add cost for this test
    writeToFile("src/logging/hpcTest", "(to be done)", True)
    res = False

    if init.obtainCost is True:
        testCost = ((time.time() - start) / 3600) * \
            init.configs["costCalculation"]["HPCInstancePrice"] * hpc["nodes"]

    init.queue.put(({"test": "hpcTest", "deployed": res}, testCost))
    return  # if errors: finish run
