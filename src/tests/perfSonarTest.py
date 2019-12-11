#!/usr/bin/env python3

from lib.checker import *
from lib.terraform import *
from lib.kubern8s import *    

def perfSonarTest(testsCatalog, configs, resDir, obtainCost):
    """Run Networking Performance test -perfSONAR toolkit-."""

    res = False
    testCost = 0
    testsRoot =  "../"
    endpoint = testsCatalog["perfsonarTest"]["endpoint"]
    if kubectl(
        Action.create,
        file=testsRoot +
        "perfsonar/ps_pod.yaml",
            toLog="logging/shared") != 0:
        writeFail(resDir, "perfsonar_results.json",
                  "Error deploying perfsonar pod.", "logging/shared")
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
                      "Error running script test on pod.", "logging/shared")
        else:
            fetchResults(resDir, "ps-pod:/tmp/perfsonar_results.json",
                         "perfsonar_results.json", "logging/shared")
            # cleanup
            writeToFile("logging/shared", "Cluster cleanup...", True)
            kubectl(Action.delete, type=Type.pod, name="ps-pod")

    return ({"test": "perfsonarTest", "deployed": res}, testCost)