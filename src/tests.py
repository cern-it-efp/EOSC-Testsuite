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
                       usePrivateIPs,
                       freeMaster):
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
                                          "src/logging/shared",
                                          init.configs,
                                          init.cfgPath,
                                          testsRoot,
                                          retry,
                                          baseCWD,
                                          extraSupportedClouds,
                                          noTerraform,
                                          usePrivateIPs,
                                          freeMaster)
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
            additionalResourcesPrices=None,
            keepResources=False): # additionalResourcePrice is an array
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
        if keepResources is False:
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
    definition = "%sdata_repatriation/repatriation_pod.yaml" % testsRoot
    resultFile = "data_repatriation_test.json"
    testName = "dataRepatriationTest"
    resultOnPod = "/home/data_repatriation_test.json"

    kubeconfig = defaultKubeconfig
    runTest(definition,
            toLog,
            testName,
            resDir,
            resultFile,
            podName,
            resultOnPod,
            kubeconfig)


def cpuBenchmarking(resDir):
    """ Run containerised CPU Benchmarking test.

    Parameters:
        resDir (str): Path to the results folder for the current run.
    """

    podName = "hep-bmk-pod"
    definition = "%scpu_benchmarking/cpu_benchmarking_pod.yaml" % testsRoot
    resultFile = "cpu_benchmarking.json"
    toLog = "src/logging/shared"
    testName = "cpuBenchmarking"
    resultOnPod = "/tmp/hep-benchmark-suite/bmkrun_report.json"

    kubeconfig = defaultKubeconfig
    runTest(definition,
            toLog,
            testName,
            resDir,
            resultFile,
            podName,
            resultOnPod,
            kubeconfig)

def dodasTest(resDir):
    """ Run DODAS test.

    Parameters:
        resDir (str): Path to the results folder for the current run.
    """

    podName = "dodas-pod"
    definition = "%sdodas/dodas_pod.yaml" % testsRoot
    resultFile = "dodas_results.json"
    toLog = "src/logging/shared"
    testName = "dodasTest"
    resultOnPod = "/tmp/%s" % resultFile

    kubeconfig = defaultKubeconfig
    runTest(definition,
            toLog,
            testName,
            resDir,
            resultFile,
            podName,
            resultOnPod,
            kubeconfig)


def perfsonarTest(resDir):
    """ Run Networking Performance test -perfSONAR toolkit-.

    Parameters:
        resDir (str): Path to the results folder for the current run.
    """

    try:
        keepPerfsonarPod = init.testsCatalog["perfsonarTest"]["keepPod"]
    except:
        keepPerfsonarPod = False

    podName = "ps-pod"
    definition_raw = "%sperfsonar/raw/ps_pod.yaml" % testsRoot
    definition = "%sperfsonar/ps_pod.yaml" % testsRoot
    resultFile = "perfsonar_results.json"
    toLog = "src/logging/shared"
    testName = "perfSONAR"
    resultOnPod = "/home/perfsonar_results.json"
    substitution = [
        {
            "before": "ENDPOINT_PH",
            "after": init.testsCatalog["perfsonarTest"]["endpoint"]
        },{
            "before": "CLOUDIP_PH",
            "after": getMasterIP("src/tests/shared/hosts")
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
            keepResources=keepPerfsonarPod)


def perfsonarTest_og(resDir):
    """ Run Networking Performance test -perfSONAR toolkit-.

    Parameters:
        resDir (str): Path to the results folder for the current run.
    """

    keepPerfsonarPod = False # TODO: CTS-190

    podName = "ps-pod"
    testName = "perfSONAR"
    endpoint = init.testsCatalog["perfsonarTest"]["endpoint"]
    dependenciesCMD = "yum -y install python-dateutil python-requests"
    runScriptCMD = "python -u /tmp/ps_test.py --ep %s > /tmp/ps_test_logs 2>&1" % endpoint
    cmd = "%s && %s" % (dependenciesCMD, runScriptCMD)
    resultFile = "perfsonar_results.json"
    definition = "%sperfsonar/ps_pod.yaml" % testsRoot
    toLog = "src/logging/shared"
    podPath="%s:/tmp" % podName
    localPath=testsRoot + "perfsonar/ps_test.py"
    resultOnPod = "/home/perfsonar_results.json"

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
            cmd=cmd,
            keepResources=keepPerfsonarPod)


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
                                          "src/logging/dlTest",
                                          init.configs,
                                          init.cfgPath,
                                          testsRoot,
                                          retry,
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

    # 1) Write the ConfigMap (data set) and MPIJob resource files:

    fullDataset = open("%s/dlTest/fullDataset" % testsRoot, 'r').readlines()
    selectedDataset = ""

    for f in range(dl["datasetSize"]):
        selectedDataset += "%s\\r\\n" % fullDataset[f].replace('\n','')

    with open("%s/dlTest/raw/dataset_raw.yaml" % testsRoot, 'r') as inputfile:
        with open("%s/dlTest/dataset.yaml" % testsRoot, 'w') as outfile:
            outfile.write(str(inputfile.read()).replace(
            "DS_PH", "\"%s\"" % selectedDataset))

    mpijobResourceFile = '%s/dlTest/raw/%s_raw.yaml' % (testsRoot, dl["benchmark"])

    gpusPerNode = getGpusPerNode(kubeconfig)
    replicas = gpusPerNode * dl["nodes"]

    with open(mpijobResourceFile, 'r') as inputfile:
        with open(testsRoot + "dlTest/mpiJob.yaml", 'w') as outfile:
            outfile.write(str(inputfile.read()).replace(
                "REP_PH", str(replicas)).replace( # this depends on the GPUs per node not the amount of nodes
                "EPOCHS_PH", str(dl["epochs"])))

    # 2) Deploy the data set ConfigMap and the MPIJob resource file:
    podName = "train-mpijob-worker-0"

    kubectl(Action.create,
        kubeconfig,
        file="%sdlTest/dataset.yaml" % testsRoot,
        ignoreErr=True)

    if kubectl(Action.create,
               kubeconfig,
               file="%sdlTest/mpiJob.yaml" % testsRoot,
               toLog="src/logging/dlTest") != 0:
        writeFail(resDir, "bb_train_history.json",
                  "Error deploying 3D GAN benchmark.", "src/logging/dlTest")

    elif waitForResource(podName, Type.pod, kubeconfig, retrials=70, sleepTime=10) is False:
        writeFail(resDir,
                  "bb_train_history.json",
                  "Error deploying 3D GAN benchmark: pods were never created",
                  "src/logging/dlTest")

    else:
        fetchResults(resDir,
                     kubeconfig,
                     podName,
                     "/%s/bb_train_history.json" % dl["benchmark"], # Losses
                     "bb_train_history.json",
                     "src/logging/dlTest")
        fetchResults(resDir,
                     kubeconfig,
                     podName,
                     "/%s/m0_bb_train_history.model" % dl["benchmark"], # Discriminator model
                     "m0_bb_train_history.model",
                     "src/logging/dlTest")
        fetchResults(resDir,
                     kubeconfig,
                     podName,
                     "/%s/m1_bb_train_history.model" % dl["benchmark"], # Combined model
                     "m1_bb_train_history.model",
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

    init.queue.put(({"test": "dlTest", "deployed": res}, testCost))


def proGANTest(onlyTest, retry, noTerraform, resDir, usePrivateIPs, freeMaster):
    """ Train a Progressive GAN.

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
    proGAN = init.testsCatalog["proGANTest"]
    kubeconfig = "src/tests/proGANTest/config"

    if noTerraform is True:
        flavor = None
    else:
        flavor = proGAN["flavor"]

    numberOfNodes = 1
    if freeMaster is True:
        numberOfNodes = 2

    if onlyTest is False:
        prov, msg = provisionAndBootstrap("proGANTest",
                                          numberOfNodes,
                                          flavor,
                                          "src/logging/proGANTest",
                                          init.configs,
                                          init.cfgPath,
                                          testsRoot,
                                          retry,
                                          baseCWD,
                                          extraSupportedClouds,
                                          noTerraform,
                                          usePrivateIPs,
                                          freeMaster)
        if prov is False:
            toPut = {"test": "proGANTest", "deployed": res}
            if "provision" in msg:
                toPut["reason"] = "ProvisionFailed"
            writeFail(resDir, "proGANTest.json",
                      msg, "src/logging/proGANTest")
            init.queue.put((toPut, testCost))
            return
    else:
        if not checkCluster("proGANTest"):
            return  # Cluster not reachable, do not add cost for this test

    # 1) Write the proGAN pod file:

    try:
        gpusToUse = proGAN["gpus"]
    except:
        gpusToUse = getGpusPerNode(kubeconfig)

    with open('%s/proGANTest/raw/progan_raw.yaml' % testsRoot, 'r') as inputfile:
        with open('%s/proGANTest/progan.yaml' % testsRoot, 'w') as outfile:
            outfile.write(str(inputfile.read()).replace(
                "BMARK_GPUS_PH", str(gpusToUse)).replace(
                "BMARK_KIMG_PH", str(proGAN["kimg"])).replace(
                "IMAGES_AMOUNT_PH", str(proGAN["images_amount"])))

    # 2) Deploy the Pro-GAN pod:

    podName = "progan-pod"
    proganPodResDir = "000-pgan-syn256rgb_conditional-preset-v2-%s-fp32"

    if gpusToUse == 1:
        proganPodResDir = proganPodResDir % "1gpu"
    elif gpusToUse == 2:
        proganPodResDir = proganPodResDir % "2gpus"
    elif gpusToUse == 4:
        proganPodResDir = proganPodResDir % "4gpus"
    else:
        proganPodResDir = proganPodResDir % "8gpus"

    if kubectl(Action.create,
               kubeconfig,
               file="%sproGANTest/progan.yaml" % testsRoot,
               toLog="src/logging/proGANTest") != 0:
        writeFail(resDir, "progan.json",
                  "Error deploying Pro-GAN benchmark.", "src/logging/proGANTest")

    else:
        fetchResults(resDir,
                     kubeconfig,
                     podName,
                     "/root/CProGAN-ME/results/%s/network-final.pkl" % proganPodResDir,
                     "network-final.pkl",
                     "src/logging/proGANTest")

        generatedImage = 'fakes%06d.png' % proGAN["kimg"]
        #fetchResults(resDir,
        #             kubeconfig,
        #             podName,
        #             "/root/CProGAN-ME/results/%s/%s" % (proganPodResDir, generatedImage),
        #             "fakes.png",
        #             "src/logging/proGANTest")
        cmd = "cp progan-pod:/root/CProGAN-ME/results/%s/%s %s/fakesLast.png" % (proganPodResDir, generatedImage, resDir)
        kubectlCLI(cmd, kubeconfig)

        fetchResults(resDir,
                     kubeconfig,
                     podName,
                     "/root/CProGAN-ME/results/%s/log.txt" % proganPodResDir,
                     "log.txt",
                     "src/logging/proGANTest")
        res = True

    # Cost estimation
    if init.obtainCost is True:
        testCost = ((time.time() - start) / 3600) * \
            init.configs["costCalculation"]["GPUInstancePrice"]

    # cleanup
    #writeToFile("src/logging/proGANTest", "Cluster cleanup...", True)
    kubectl(Action.delete, kubeconfig, type=Type.pod, name=podName)
    init.queue.put(({"test": "proGANTest", "deployed": res}, testCost))


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
                                          "src/logging/hpcTest",
                                          init.configs,
                                          init.cfgPath,
                                          testsRoot,
                                          retry,
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
