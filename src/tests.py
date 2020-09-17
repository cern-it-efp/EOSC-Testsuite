#!/usr/bin/env python3

import sys
try:
    from multiprocessing import Process, Queue
    import contextlib
    import io
except ModuleNotFoundError as ex:
    print(ex)
    sys.exit(1)
from checker import *
from provisionment import *
from kubernetesFunctions import *
from aux import *
import init


def sharedClusterTests(msgArr,
                       onlyTest,
                       retry,
                       noTerraform,
                       resDir,
                       numberOfNodes,
                       usePrivateIPs):
    """ Runs the test that share the general purpose cluster.

    Parameters:
        msgArray (Array<str>): Stuff to show on the banner. Contains the
                               tests to be deployed on the shared cluster.
        onlyTest (bool): If true, skip provisioning phase.
        retry (bool): If true, try to reuse existing infrastructure.
        noTerraform (bool): Specifies whether current run uses terraform.
        resDir (str): Path to the results folder for the current run.
        numberOfNodes (int): Number of nodes to provision.
        usePrivateIPs (bool): Indicates usage of private or public IPs.

    Returns:
        None: In case of errors the function stops (returns None)
    """

    start = time.time()
    sharedClusterProcs = []
    testCost = 0
    logger(msgArr, "=", "src/logging/shared")

    if noTerraform is True:
        flavor = None
    else:
        flavor = init.configs["flavor"]

    if onlyTest is False:
        prov, msg = provisionAndBootstrap("shared",
                                          numberOfNodes,
                                          flavor,
                                          None,
                                          "src/logging/shared",
                                          init.configs,
                                          init.cfgPath,
                                          testsRoot,
                                          retry,
                                          instanceDefinition,
                                          credentials,
                                          dependencies,
                                          baseCWD,
                                          extraSupportedClouds,
                                          noTerraform,
                                          usePrivateIPs)
        if prov is False:
            toPut = {"test": "shared", "deployed": False}
            if "provision" in msg:
                toPut["reason"] = "ProvisionFailed"
            writeFail(resDir, "sharedCluster_result.json",
                      msg, "src/logging/shared")
            init.queue.put((toPut, testCost))
            return
    else:
        if not checkCluster("shared"):
            return # Cluster not reachable, do not add cost for this test
    for test in msgArr[1:]:
        p = Process(target=eval(test), args=(resDir,))
        sharedClusterProcs.append(p)
        p.start()
    for p in sharedClusterProcs:
        p.join()
    if init.obtainCost is True: # duration * instancePrice * numberOfInstances
        testCost = ((time.time() - start) / 3600) * \
            init.configs["costCalculation"]["generalInstancePrice"] * \
            len(msgArr[1:])
    init.queue.put((None, testCost))


def runTest(definition,
            toLog,
            testName,
            resDir,
            resultFile,
            podName,
            resultOnPod,
            kubeconfig,
            definition_raw=None,
            substitution=None,
            copyToPodAndRun_flag=None,
            podPath=None,
            localPath=None,
            cmd=None,
            additionalResourcesPrices=None): # additionalResourcePrice is an array
    """ Runs tests.

    Parameters:
        msgArray (Array<str>): Stuff to show on the banner. Contains the
                               tests to be deployed on the shared cluster.
        onlyTest (bool): If true, skip provisioning phase.
        retry (bool): If true, try to reuse existing infrastructure.
        noTerraform (bool): Specifies whether current run uses terraform.
        resDir (str): Path to the results folder for the current run.
        numberOfNodes (int): Number of nodes to provision.
    """

    testCost = 0
    if definition_raw is not None:
        groupReplace(definition_raw, substitution, definition)

    #---------------------------------------------------------------------------
    start = time.time() # For tests with additional resources (i.e S3 bucket)
    #---------------------------------------------------------------------------

    if kubectl(Action.create,
               kubeconfig,
               file=definition,
               toLog=toLog) != 0:
        init.queue.put(({"test": testName, "deployed": False}, testCost))
        writeFail(resDir, resultFile, "%s pod deploy failed." % podName, toLog)
    else:
        if copyToPodAndRun_flag is True:
            copyToPodAndRun(
                podName,
                kubeconfig,
                resDir,
                toLog,
                podPath,
                localPath,
                cmd,
                resultFile,
                resultOnPod)
        else:
            fetchResults(resDir,kubeconfig,podName,resultOnPod,resultFile,toLog)

        #-----------------------------------------------------------------------
        testDuration = time.time() - start # For tests with additional resources
        if init.obtainCost is True and additionalResourcesPrices is not None:
            for price in additionalResourcesPrices:
                testCost = float(price) * testDuration / 3600
        #-----------------------------------------------------------------------

        # cleanup
        writeToFile(toLog, "Cluster cleanup...", True)
        kubectl(Action.delete, kubeconfig, type=Type.pod, name=podName)
        init.queue.put(({"test": testName, "deployed": True}, testCost))


def s3Test(resDir):
    """ Run S3 endpoints test.

    Parameters:
        resDir (str): Path to the results folder for the current run.
    """

    testCost = 0
    podName = "s3pod"
    definition_raw = "%ss3/raw/s3pod_raw.yaml" % testsRoot
    definition = "%ss3/s3pod.yaml" % testsRoot
    resultFile = "s3Test.json"
    toLog = "src/logging/shared"
    testName = "s3Test"
    resultOnPod = "/home/s3_test.json"
    additionalResourcesPrices = [tryTakeFromYaml(
                                init.configs,
                                "costCalculation.s3bucketPrice",
                                None)]
    substitution = [
        {
            "before": "ENDPOINT_PH",
            "after": init.testsCatalog["s3Test"]["endpoint"]
        },
        {
            "before": "ACCESS_PH",
            "after": init.testsCatalog["s3Test"]["accessKey"]
        },
        {
            "before": "SECRET_PH",
            "after": init.testsCatalog["s3Test"]["secretKey"]
        }
    ]
    kubeconfig = defaultKubeconfig
    runTest(definition,
            toLog,
            testName,
            resDir,
            resultFile,
            podName,
            resultOnPod,
            kubeconfig,
            definition_raw=definition_raw,
            substitution=substitution,
            additionalResourcesPrices=additionalResourcesPrices)


def dataRepatriationTest(resDir):
    """ Run Data Repatriation Test -Exporting from cloud to Zenodo-.

    Parameters:
        resDir (str): Path to the results folder for the current run.
    """

    podName = "repatriation-pod"
    toLog = "src/logging/shared"
    definition_raw = "%sdata_repatriation/raw/repatriation_pod_raw.yaml" % testsRoot
    definition = "%sdata_repatriation/repatriation_pod.yaml" % testsRoot
    resultFile = "data_repatriation_test.json"
    testName = "cpuBenchmarking"
    resultOnPod = "/home/data_repatriation_test.json"
    substitution = [
        {
            "before": "PROVIDER_PH",
            "after": init.configs["providerName"]
        }
    ]
    kubeconfig = defaultKubeconfig
    runTest(definition,
            toLog,
            testName,
            resDir,
            resultFile,
            podName,
            resultOnPod,
            kubeconfig,
            definition_raw=definition_raw,
            substitution=substitution)


def cpuBenchmarking(resDir):
    """ Run containerised CPU Benchmarking test.

    Parameters:
        resDir (str): Path to the results folder for the current run.
    """

    podName = "cpu-bmk-pod"
    definition_raw = "%scpu_benchmarking/raw/cpu_benchmarking_pod_raw.yaml" % testsRoot
    definition = "%scpu_benchmarking/cpu_benchmarking_pod.yaml" % testsRoot
    resultFile = "cpu_benchmarking.json"
    toLog = "src/logging/shared"
    testName = "cpuBenchmarking"
    resultOnPod = "/tmp/cern-benchmark_root/bmk_tmp/result_profile.json"
    substitution = [
        {
            "before": "PROVIDER_PH",
            "after": init.configs["providerName"]
        }
    ]
    kubeconfig = defaultKubeconfig
    runTest(definition,
            toLog,
            testName,
            resDir,
            resultFile,
            podName,
            resultOnPod,
            kubeconfig,
            definition_raw=definition_raw,
            substitution=substitution)


def perfsonarTest(resDir):
    """ Run Networking Performance test -perfSONAR toolkit-.

    Parameters:
        resDir (str): Path to the results folder for the current run.
    """

    podName = "ps-pod"
    testName = "perfSONAR"
    endpoint = init.testsCatalog["perfsonarTest"]["endpoint"]
    dependenciesCMD = "yum -y install python-dateutil python-requests"
    runScriptCMD = "python /tmp/ps_test.py --ep %s" % endpoint
    runOnPodCMD = "%s && %s" % (dependenciesCMD, runScriptCMD)
    cmd = "%s" % runOnPodCMD
    resultFile = "perfsonar_results.json"
    definition = "%sperfsonar/ps_pod.yaml" % testsRoot
    toLog = "src/logging/shared"
    podPath="%s:/tmp" % podName
    localPath=testsRoot + "perfsonar/ps_test.py"
    resultOnPod = "/tmp/perfsonar_results.json"
    kubeconfig = defaultKubeconfig
    runTest(definition,
            toLog,
            testName,
            resDir,
            resultFile,
            podName,
            resultOnPod,
            kubeconfig,
            copyToPodAndRun_flag=True,
            podPath=podPath,
            localPath=localPath,
            cmd=cmd)


def dodasTest(resDir):
    """ Run DODAS test.

    Parameters:
        resDir (str): Path to the results folder for the current run.
    """

    podName = "dodas-pod"
    toLog = "src/logging/shared"
    resultFile = "dodas_results.json"
    resultOnPod = "/tmp/%s" % resultFile
    definition = "%sdodas/dodas_pod.yaml" % testsRoot
    testName = "dodasTest"
    podPath = "%s:/CMSSW/CMSSW_9_4_0/src" % podName
    localPath = "%sdodas/custom_entrypoint.sh" % testsRoot
    cmd = "sh /CMSSW/CMSSW_9_4_0/src/custom_entrypoint.sh"
    kubeconfig = defaultKubeconfig
    runTest(definition,
            toLog,
            testName,
            resDir,
            resultFile,
            podName,
            resultOnPod,
            kubeconfig,
            copyToPodAndRun_flag=True,
            podPath=podPath,
            localPath=localPath,
            cmd=cmd)


def dlTest(onlyTest, retry, noTerraform, resDir, usePrivateIPs):
    """ Run Deep Learning test -GAN training- on GPU nodes.

    Parameters:
        onlyTest (bool): If true, skip provisioning phase.
        retry (bool): If true, try to reuse existing infrastructure.
        noTerraform (bool): Specifies whether current run uses terraform.
        resDir (str): Path to the results folder for the current run.
        usePrivateIPs (bool): Indicates usage of private or public IPs.

    Returns:
        None: In case of errors the function stops (returns None)
    """

    start = time.time()
    testCost = 0
    res = False
    dl = init.testsCatalog["dlTest"]
    kubeconfig = "src/tests/dlTest/config"

    if noTerraform is True:
        flavor = None
    else:
        flavor = dl["flavor"]

    if onlyTest is False:
        prov, msg = provisionAndBootstrap("dlTest",
                                          dl["nodes"],
                                          flavor,
                                          extraInstanceConfig,
                                          "src/logging/dlTest",
                                          init.configs,
                                          init.cfgPath,
                                          testsRoot,
                                          retry,
                                          instanceDefinition,
                                          credentials,
                                          dependencies,
                                          baseCWD,
                                          extraSupportedClouds,
                                          noTerraform,
                                          usePrivateIPs)
        if prov is False:
            toPut = {"test": "dlTest", "deployed": res}
            if "provision" in msg:
                toPut["reason"] = "ProvisionFailed"
            writeFail(resDir, "bb_train_history.json",
                      msg, "src/logging/dlTest")
            init.queue.put((toPut, testCost))
            return
    else:
        if not checkCluster("dlTest"):
            return  # Cluster not reachable, do not add cost for this test

    # TODO: what happens when running on a non-GPU cluster or a GPU cluster that is not prepared (i.e no drivers)?

    # 1) Install the stuff needed for this test: device plugin yaml file
    # (contains driver too) and dl_stack.sh for kubeflow and mpi.
    # (backend run assumes dl support)
    kubectl(Action.create, kubeconfig, file=testsRoot +
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
    with open(testsRoot + 'dlTest/mpi_learn_raw.yaml', 'r') as inputfile:
        with open(testsRoot + "dlTest/mpi_learn.yaml", 'w') as outfile:
            outfile.write(str(inputfile.read()).replace( # TODO: do not use replace
                "REP_PH", str(nodesToUse))) # w/o -1 because the launcher does not get a GPU anymore, hence all nodes can allocate worker replicas
                #"REP_PH", str(nodesToUse - 1))) # -1 because these are worker replicas, and the launcher gets a GPU

    podName = "train-mpijob-worker-0"

    if kubectl(
        Action.create,
        kubeconfig,
        file=testsRoot +
        "dlTest/mpi_learn.yaml",
            toLog="src/logging/dlTest") != 0:
        writeFail(resDir, "bb_train_history.json",
                  "Error deploying 3D GAN benchmark.", "src/logging/dlTest")

    elif waitForPod(podName, kubeconfig, retrials=20, sleepTime=10) is False:
        writeFail(resDir,
                  "bb_train_history.json",
                  "Error deploying 3D GAN benchmark: pods were never created",
                  "src/logging/dlTest")

    else:
        fetchResults(
            resDir,
            kubeconfig,
            podName,
            "/mpi_learn/bb_train_history.json",
            "bb_train_history.json",
            "src/logging/dlTest")

        res = True

    # Cost estimation
    if init.obtainCost is True:
        testCost = ((time.time() - start) / 3600) * \
            init.configs["costCalculation"]["GPUInstancePrice"] * dl["nodes"]

    # cleanup
    writeToFile("src/logging/dlTest", "Cluster cleanup...", True)
    kubectl(Action.delete, kubeconfig, type=Type.mpijob, name="train-mpijob")
    kubectl(Action.delete, kubeconfig, type=Type.configmap, name="3dgan-datafile-lists")
    #kubectl(Action.delete, kubeconfig, type=Type.pv, name="pv-volume1")
    #kubectl(Action.delete, kubeconfig, type=Type.pv, name="pv-volume2")
    #kubectl(Action.delete, kubeconfig, type=Type.pv, name="pv-volume3")

    init.queue.put(({"test": "dlTest", "deployed": res}, testCost))


def hpcTest(onlyTest, retry, noTerraform, resDir, usePrivateIPs):
    """ HPC test.

    Parameters:
        onlyTest (bool): If true, skip provisioning phase.
        retry (bool): If true, try to reuse existing infrastructure.
        noTerraform (bool): Specifies whether current run uses terraform.
        resDir (str): Path to the results folder for the current run.
        usePrivateIPs (bool): Indicates usage of private or public IPs.

    Returns:
        None: In case of errors the function stops (returns None)
    """

    start = time.time()
    testCost = 0
    res = False
    hpc = init.testsCatalog["hpcTest"]

    if noTerraform is True:
        flavor = None
    else:
        flavor = hpc["flavor"]

    if onlyTest is False:
        prov, msg = provisionAndBootstrap("hpcTest",
                                          hpc["nodes"],
                                          flavor,
                                          None,
                                          "src/logging/hpcTest",
                                          init.configs,
                                          init.cfgPath,
                                          testsRoot,
                                          retry,
                                          instanceDefinition,
                                          credentials,
                                          dependencies,
                                          baseCWD,
                                          extraSupportedClouds,
                                          noTerraform,
                                          usePrivateIPs)
        if prov is False:
            toPut = {"test": "hpcTest", "deployed": res}
            if "provision" in msg:
                toPut["reason"] = "ProvisionFailed"
            writeFail(resDir, "hpcTest_result.json",
                      msg, "src/logging/hpcTest")
            init.queue.put((toPut, testCost))
            return
    else:
        if not checkCluster("hpcTest"):
            return  # Cluster not reachable, do not add cost for this test
    writeToFile("src/logging/hpcTest", "(to be done)", True)

    if init.obtainCost is True:
        testCost = ((time.time() - start) / 3600) * \
            init.configs["costCalculation"]["HPCInstancePrice"] * hpc["nodes"]

    init.queue.put(({"test": "hpcTest", "deployed": res}, testCost))
    return  # if errors: finish run
