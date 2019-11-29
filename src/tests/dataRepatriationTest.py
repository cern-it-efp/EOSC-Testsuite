#!/usr/bin/env python3

from lib.checker import *
from lib.terraform import *
from lib.kubern8s import *    

def dataRepatriationTest(configs, resDir):
    """Run Data Repatriation Test -Exporting from cloud to Zenodo-."""

    testsRoot =  "../"
    with open("data_repatriation/raw/repatriation_pod_raw.yaml",
              'r') as infile:
        with open("data_repatriation/repatriation_pod.yaml",
                  'w') as outfile:
            outfile.write(infile.read().replace(
                "PROVIDER_PH", configs["providerName"]))

    if kubectl(
            Action.create,
            file="%sdata_repatriation/repatriation_pod.yaml" %
            testsRoot,
            toLog="logging/shared") != 0:
        writeFail(resDir, "data_repatriation_test.json",
                  "Error deploying data_repatriation pod.", "logging/shared")

    else:
        fetchResults(
            resDir,
            "repatriation-pod:/home/data_repatriation_test.json",
            "data_repatriation_test.json",
            "logging/shared")
        # cleanup
        writeToFile("logging/shared", "Cluster cleanup...", True)
        kubectl(Action.delete, type=Type.pod, name="repatriation-pod")