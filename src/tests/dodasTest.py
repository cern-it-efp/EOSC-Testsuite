#!/usr/bin/env python3

from lib.checker import *
from lib.terraform import *
from lib.kubern8s import *    

def dodasTest(resDir):
    """Run DODAS test."""

    res = False
    testsRoot =  "../"
    if kubectl(
        Action.create,
        file="dodas/dodas_pod.yaml",
            toLog="logging/shared") != 0:
        writeFail(resDir, "dodas_test.json",
                  "Error deploying DODAS pod.", "logging/shared")
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
                      "Error running script test on pod.", "logging/shared")
        else:
            fetchResults(resDir, "dodas-pod:/tmp/dodas_test.json",
                         "dodas_results.json", "logging/shared")
            res = True
            # cleanup
            writeToFile("logging/shared", "Cluster cleanup...", True)
            kubectl(Action.delete, type=Type.pod, name="dodas-pod")