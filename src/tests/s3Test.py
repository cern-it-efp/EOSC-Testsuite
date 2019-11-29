#!/usr/bin/env python3

from lib.checker import *
from lib.terraform import *
from lib.kubern8s import *    

def s3Test(testsCatalog, configs, resDir, obtainCost):
    """Run S3 endpoints test."""

    with open("s3/raw/s3pod_raw.yaml", 'r') as infile:
        with open("s3/s3pod.yaml", 'w') as outfile:
            outfile.write(
                infile.read().replace(
                    "ENDPOINT_PH",
                    testsCatalog["s3Test"]["endpoint"]) .replace(
                    "ACCESS_PH",
                    testsCatalog["s3Test"]["accessKey"]) .replace(
                    "SECRET_PH",
                    testsCatalog["s3Test"]["secretKey"]))

    start = time.time()  # create bucket
    if kubectl(
        Action.create,
        file="s3/s3pod.yaml",
            toLog="../../logging/shared") != 0:
        writeFail(resDir, "s3Test.json",
                  "Error deploying s3pod.", "../logging/shared")
    else:
        fetchResults(resDir, "s3pod:/home/s3_test.json",
                     "s3_test.json", "../logging/shared")
        end = time.time()  # bucket deletion
        # cleanup
        writeToFile("../logging/shared", "Cluster cleanup...", True)
        kubectl(Action.delete, type=Type.pod, name="s3pod")
        if obtainCost is True:
            testCost = float(configs["costCalculation"]
                             ["s3bucketPrice"]) * (end - start) / 3600